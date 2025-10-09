# Fixed student_fees/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.db.models import Sum, Q
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone as django_timezone
from decimal import Decimal
from users.decorators import module_required
import logging

# Integrated fee service
from .integration import integrated_service, CENTRALIZED_SERVICE_AVAILABLE

from transport.models import TransportAssignment
from fines.models import Fine, FineStudent
from students.models import Student
from fees.models import FeesType
from subjects.models import ClassSection
from school_profile.models import SchoolProfile
from messaging.fee_messaging import FeeMessagingService
from messaging.message_tokens import MessageFormatter
from messaging.cross_module_logger import CrossModuleMessageLogger

from .models import FeeDeposit
from .forms import FeePaymentForm
from .utils import generate_receipt_no
from .services import FeeCalculationService, PaymentProcessingService, FeeReportingService
# Security utilities moved to centralized service
from django.utils.html import escape
from django.core.exceptions import ValidationError

def sanitize_log_input(text):
    """Simple log sanitization"""
    return str(text)[:200] if text else ''

def sanitize_html_output(text):
    """Simple HTML sanitization"""
    return escape(str(text)) if text else ''

def validate_numeric_id(value, field_name="ID"):
    """Simple numeric ID validation"""
    try:
        num_id = int(value)
        if num_id <= 0:
            raise ValidationError(f"Invalid {field_name}")
        return num_id
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid {field_name} format")

def validate_receipt_number(receipt_no):
    """Simple receipt number validation"""
    if not receipt_no or len(receipt_no) > 50:
        raise ValidationError("Invalid receipt number")
    return receipt_no

# Optional ML integration
try:
    from core.ml_integrations import ml_service
    ML_AVAILABLE = True
except ImportError:
    ml_service = None
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)

class FeeDepositListView(ListView):
    def dispatch(self, request, *args, **kwargs):
        from users.models import UserModulePermission
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
        if not request.user.is_superuser:
            permissions = UserModulePermission.get_user_permissions(request.user)
            if not permissions.get('payments', {}).get('view', False):
                messages.error(request, 'Sorry, you don\'t have permission to view payments. Please contact your administrator.')
                return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    model = Student
    template_name = 'student_fees/deposit.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        queryset = Student.objects.all_statuses().select_related('class_section').order_by('admission_number')
        
        if query:
            safe_query = query[:50]
            
            # Handle multi-word searches (e.g., "Upmanyu Mukund")
            query_parts = safe_query.split()
            
            if len(query_parts) >= 2:
                # Multi-word search - match first and last name separately
                first_part = query_parts[0]
                last_part = query_parts[-1]
                
                name_filter = (
                    (Q(first_name__icontains=first_part) & Q(last_name__icontains=last_part)) |
                    (Q(first_name__icontains=last_part) & Q(last_name__icontains=first_part))
                )
                
                queryset = queryset.filter(
                    Q(admission_number__icontains=safe_query) |
                    name_filter |
                    Q(father_name__icontains=safe_query) |
                    Q(class_section__class_name__icontains=safe_query)
                )
            else:
                # Single word search - original logic
                queryset = queryset.filter(
                    Q(admission_number__icontains=safe_query) |
                    Q(first_name__icontains=safe_query) |
                    Q(last_name__icontains=safe_query) |
                    Q(father_name__icontains=safe_query) |
                    Q(class_section__class_name__icontains=safe_query)
                )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['school_name'] = 'School Management System'
        return context

class FeeDepositCreateView(CreateView):
    def dispatch(self, request, *args, **kwargs):
        from users.models import UserModulePermission
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
        if not request.user.is_superuser:
            permissions = UserModulePermission.get_user_permissions(request.user)
            if not permissions.get('payments', {}).get('edit', False):
                messages.error(request, 'Sorry, you don\'t have permission to create payments. Please contact your administrator.')
                return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    model = FeeDeposit
    form_class = FeePaymentForm
    template_name = 'student_fees/deposit.html'
    success_url = reverse_lazy('student_fees:fee_deposit')
    
    def form_valid(self, form):
        form.instance.receipt_no = generate_receipt_no()
        form.instance.student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        
        success_msg = MessageFormatter.format_success(
            'payment_received',
            amount=form.instance.paid_amount,
            receipt_no=form.instance.receipt_no
        )
        messages.success(self.request, success_msg)
        return super().form_valid(form)

class FeeDepositUpdateView(UpdateView):
    def dispatch(self, request, *args, **kwargs):
        from users.models import UserModulePermission
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
        if not request.user.is_superuser:
            permissions = UserModulePermission.get_user_permissions(request.user)
            if not permissions.get('payments', {}).get('edit', False):
                messages.error(request, 'Sorry, you don\'t have permission to edit payments. Please contact your administrator.')
                return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    model = FeeDeposit
    form_class = FeePaymentForm
    template_name = 'student_fees/edit_deposit.html'
    context_object_name = 'deposit'

    def form_valid(self, form):
        form.instance.paid_amount = form.instance.amount - (form.instance.discount or 0)
        messages.success(self.request, "Great! Payment details have been updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('student_fees:student_fee_preview', args=[self.object.student.id])

class FeeDepositDeleteView(DeleteView):
    def dispatch(self, request, *args, **kwargs):
        from users.models import UserModulePermission
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
        if not request.user.is_superuser:
            permissions = UserModulePermission.get_user_permissions(request.user)
            if not permissions.get('payments', {}).get('edit', False):
                messages.error(request, 'Sorry, you don\'t have permission to delete payments. Please contact your administrator.')
                return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    model = FeeDeposit
    template_name = 'student_fees/confirm_delete.html'
    context_object_name = 'deposit'

    def delete(self, request, *args, **kwargs):
        student_id = self.object.student.id
        paid_amount = self.object.paid_amount
        receipt_no = self.object.receipt_no
        note = self.object.note
        
        if note and "Carry Forward" in note:
            payment_type = "Carry Forward payment"
        elif note and "Fine Payment" in note:
            payment_type = "Fine payment"
        else:
            payment_type = "Payment"
        
        response = super().delete(request, *args, **kwargs)
        
        messages.success(
            request, 
            f"Perfect! {payment_type} has been removed successfully. Receipt {receipt_no} for ₹{paid_amount} has been cancelled."
        )
        return response

    def get_success_url(self):
        return reverse('student_fees:student_fee_preview', args=[self.object.student.id])

@module_required('payments', 'view')
def get_student_fees(request):
    """Get student fees for payment form"""
    admission_number = request.GET.get('admission_number', '').strip()
    discount_enabled_param = request.GET.get("discount_enabled", "false").lower()
    discount_enabled = discount_enabled_param in ["true", "1", "yes", "on"]
    
    logger.info(f"🔍 [FEES DEBUG] get_student_fees called - admission_number: {admission_number}, discount_enabled: {discount_enabled}")
    
    try:
        if not admission_number or len(admission_number) > 20:
            logger.warning(f"❌ [FEES DEBUG] Invalid admission number: {admission_number}")
            error_msg = MessageFormatter.format_error('student_not_found')
            return JsonResponse({
                "status": "error",
                "message": error_msg,
                "html": f'<div class="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center"><i class="fas fa-search text-yellow-500 text-3xl mb-3"></i><p class="text-yellow-700 font-semibold">{error_msg}</p></div>',
                "fees_count": 0
            })
        
        logger.info(f"🔍 [FEES DEBUG] Searching for student with admission_number: {admission_number}")
        student = Student.objects.all_statuses().select_related('class_section').get(admission_number=admission_number)
        logger.info(f"✅ [FEES DEBUG] Student found: {student.first_name} {student.last_name} (ID: {student.id})")
        
        # Use integrated fee service
        logger.info(f"🔍 [FEES DEBUG] CENTRALIZED_SERVICE_AVAILABLE: {CENTRALIZED_SERVICE_AVAILABLE}")
        logger.info(f"🔍 [FEES DEBUG] Using integrated fee service for student {student.id}")
        
        payable_fees = integrated_service.get_student_payable_fees(student, discount_enabled)
        balance_info = integrated_service.get_student_balance_info(student)
        
        logger.info(f"✅ [FEES DEBUG] Integrated service returned {len(payable_fees)} payable fees")
        # Debug: Log each fee for verification
        for i, fee in enumerate(payable_fees):
            logger.info(f"🔍 [FEES DEBUG] Payable fee {i+1}: {fee}")
        
        # Sanitize data for template
        logger.info(f"🔍 [FEES DEBUG] Processing {len(payable_fees)} fees for template")
        safe_fees = []
        
        for i, fee in enumerate(payable_fees):
            logger.debug(f"🔍 [FEES DEBUG] Fee {i+1}: {fee} (type: {type(fee)})")
            
            if isinstance(fee, dict):
                safe_fees.append({
                    'id': fee.get('id', f'fee_{i}'),
                    'amount': fee.get('amount', fee.get('payable', 0)),
                    'display_name': sanitize_html_output(fee.get('name', fee.get('display_name', fee.get('fee_type', 'Fee')))),
                    'type': fee.get('type', fee.get('fee_type', 'Fee')),
                    'is_overdue': fee.get('is_overdue', False),
                    'due_date': fee.get('due_date', '')
                })
            else:
                logger.warning(f"🔍 [FEES DEBUG] Unexpected fee format: {fee}")
                safe_fees.append({
                    'id': f'fee_{i}',
                    'amount': 0,
                    'display_name': str(fee),
                    'type': 'Fee',
                    'is_overdue': False,
                    'due_date': ''
                })
        logger.info(f"✅ [FEES DEBUG] Processed {len(safe_fees)} safe fees for template")
        
        template_context = {
            'fees': safe_fees,
            'student': student,
            'balance_info': balance_info,
            'discount_enabled': bool(discount_enabled)
        }
        
        logger.info(f"🔍 [FEES DEBUG] Rendering template with context: fees={len(safe_fees)}, student={student.admission_number}, discount_enabled={discount_enabled}")
        logger.info(f"🔍 [FEES DEBUG] Template context discount_enabled type: {type(discount_enabled)}, value: {discount_enabled}, bool: {bool(discount_enabled)}")
        html = render_to_string('student_fees/components/fee_form.html', template_context)
        logger.info(f"✅ [FEES DEBUG] Template rendered successfully, HTML length: {len(html)}")
        
        # Debug: Check if discount column is in rendered HTML
        discount_column_count = html.count('Discount')
        discount_input_count = html.count('discount-input')
        logger.info(f"🔍 [FEES DEBUG] Rendered HTML contains: discount_column_count={discount_column_count}, discount_input_count={discount_input_count}")
        
        return JsonResponse({
            "status": "success",
            "html": html,
            "fees_count": len(safe_fees)
        })

    except Student.DoesNotExist:
        logger.error(f"❌ [FEES DEBUG] Student not found with admission_number: {admission_number}")
        error_msg = MessageFormatter.format_error('student_not_found')
        return JsonResponse({
            "status": "error",
            "message": error_msg
        })
    except Exception as e:
        logger.exception(f"❌ [FEES DEBUG] Error getting student fees: {sanitize_log_input(str(e))}")
        return JsonResponse({
            "status": "error",
            "message": f"Error: {str(e)}",
            "html": f'<div class="bg-red-50 border border-red-200 rounded-xl p-6 text-center"><i class="fas fa-exclamation-triangle text-red-500 text-3xl mb-3"></i><p class="text-red-700 font-semibold">Error: {str(e)}</p></div>',
            "fees_count": 0
        })

@require_POST
@csrf_protect
@module_required('payments', 'edit')
def submit_deposit(request):
    """Process fee deposit with centralized calculation service"""
    try:
        # Input validation
        student_id = request.POST.get('student_id')
        if not student_id:
            return JsonResponse({
                "status": "error", 
                "message": "Please select a student to process payment.",
                "show_message": True
            }, status=400)
        
        try:
            student_id = validate_numeric_id(student_id, "Student ID")
        except ValidationError:
            return JsonResponse({
                "status": "error", 
                "message": "Invalid student information. Please try again.",
                "show_message": True
            }, status=400)
            
        selected_fees = list(set(request.POST.getlist('selected_fees')))
        if not selected_fees:
            return JsonResponse({
                "status": "error",
                "message": "Please select at least one fee to pay.",
                "show_message": True
            }, status=400)
        
        # Use centralized payment processing
        with transaction.atomic():
            student = Student.objects.select_for_update().get(pk=student_id)
            receipt_no = generate_receipt_no()
            
            # Skip auto-sync to avoid receipt validation errors
            # if FEE_SERVICE_AVAILABLE:
            #     try:
            #         fee_service.sync_student_fees_and_fines(student)
            #     except Exception as e:
            #         logger.warning(f"Auto-sync failed before payment: {e}")
            
            # Prepare payment data
            payment_items = []
            for fee_id in selected_fees:
                amount_key = f'amount_{fee_id}'
                discount_key = f'discount_{fee_id}'
                payable_key = f'payable_{fee_id}'
                
                original_amount = Decimal(request.POST.get(amount_key, '0').replace('₹', '').replace(',', '')) or Decimal('0')
                discount = Decimal(request.POST.get(discount_key, '0').replace('₹', '').replace(',', '')) or Decimal('0')
                payable_amount = Decimal(request.POST.get(payable_key, '0').replace('₹', '').replace(',', '')) or Decimal('0')
                
                logger.info(f"🔍 [BACKEND] Fee {fee_id}: original={original_amount}, discount={discount}, payable={payable_amount}")
                
                # ALWAYS use payable amount (user's edited value)
                amount = payable_amount if payable_amount > 0 else (original_amount - discount)
                
                logger.info(f"✅ [BACKEND] Fee {fee_id}: final amount={amount}")
                
                if amount > 0:
                    payment_items.append({
                        'fee_id': fee_id,
                        'amount': amount,
                        'discount': Decimal('0')
                    })
            
            if not payment_items:
                return JsonResponse({
                    "status": "error",
                    "message": "Please enter valid payment amounts.",
                    "show_message": True
                }, status=400)
            
            # Validate receipt number before processing
            if not receipt_no or len(receipt_no) < 5:
                return JsonResponse({
                    "status": "error",
                    "message": "Failed to generate receipt number. Please try again.",
                    "show_message": True
                }, status=500)
            
            # Process payments
            total_paid = Decimal('0')
            deposits = []
            
            for item in payment_items:
                fee_id = item['fee_id']
                amount = item['amount']
                discount = item['discount']
                paid_amount = amount
                
                if paid_amount <= 0:
                    continue
                
                # Create deposit based on fee type
                deposit_data = {
                    'student': student,
                    'amount': amount,
                    'discount': discount,
                    'paid_amount': paid_amount,
                    'receipt_no': receipt_no,
                    'payment_mode': request.POST.get('payment_mode', 'Cash'),
                    'transaction_no': request.POST.get('transaction_no', ''),
                    'payment_source': request.POST.get('payment_source', ''),
                    'deposit_date': django_timezone.now()
                }
                
                if fee_id == 'carry_forward':
                    deposit_data.update({
                        'note': 'Carry Forward Payment'
                    })
                elif fee_id.startswith('fine_'):
                    fine_id = validate_numeric_id(fee_id.replace('fine_', ''), "Fine ID")
                    fine = Fine.objects.get(id=fine_id)
                    deposit_data.update({
                        'note': f'Fine Payment: {fine.fine_type.name}'
                    })
                    # Mark fine as paid
                    FineStudent.objects.filter(fine=fine, student=student).update(
                        is_paid=True,
                        payment_date=django_timezone.now().date()
                    )
                else:
                    fee = FeesType.objects.get(id=fee_id)
                    deposit_data['note'] = f'Fee Payment: {fee.fee_group.group_type} - {fee.amount_type}'
                
                deposits.append(FeeDeposit(**deposit_data))
                total_paid += paid_amount
            
            # Final validation before saving
            for deposit in deposits:
                if not deposit.receipt_no or len(deposit.receipt_no) < 5:
                    return JsonResponse({
                        "status": "error",
                        "message": "Invalid receipt number detected. Please try again.",
                        "show_message": True
                    }, status=500)
            
            # Bulk create deposits
            FeeDeposit.objects.bulk_create(deposits)
            
            # Clear cache and trigger post-payment sync
            try:
                from django.core.cache import cache
                # Clear all balance cache keys for this student
                cache_keys = [f"balance_{student.id}_{hash(str(getattr(student, 'updated_at', i)))}" for i in range(100)]
                for key in cache_keys:
                    cache.delete(key)
                cache.delete(f"balance_{student.id}")
                cache.delete('dashboard_stats')
                cache.set('dashboard_last_update', django_timezone.now().isoformat(), 3600)
                
                logger.info("Balance cache cleared for student after payment")
            except Exception as cache_error:
                logger.warning(f"Failed to invalidate cache: {cache_error}")
                pass
            
            request.session['last_receipt_no'] = receipt_no
            
            # Send SMS notification and log to messaging history
            try:
                messaging_service = FeeMessagingService()
                sms_result = messaging_service.send_payment_confirmation_sms(
                    student=student,
                    paid_amount=total_paid,
                    payment_date=django_timezone.now().date(),
                    receipt_no=receipt_no
                )
                
                # Log message to central messaging history
                message_content = f"Payment received! ₹{total_paid} for {student.get_full_display_name()}. Receipt: {receipt_no}"
                CrossModuleMessageLogger.log_fee_payment_notification(
                    user=request.user,
                    student=student,
                    message_content=message_content,
                    phone=student.mobile_number,
                    status='SENT' if sms_result.get('success') else 'FAILED'
                )
                
            except Exception as e:
                logger.warning(f"SMS notification failed: {str(e)}")
                # Still log the attempt even if SMS failed
                try:
                    message_content = f"Payment received! ₹{total_paid} for {student.get_full_display_name()}. Receipt: {receipt_no}"
                    CrossModuleMessageLogger.log_fee_payment_notification(
                        user=request.user,
                        student=student,
                        message_content=message_content,
                        phone=student.mobile_number,
                        status='FAILED'
                    )
                except Exception:
                    pass
            
            # Add success message and redirect to confirmation page
            messages.success(
                request, 
                f"Excellent! Payment of ₹{total_paid} has been received successfully. Receipt: {receipt_no}"
            )
            
            # Redirect to payment confirmation page with receipt number
            confirmation_url = reverse('student_fees:payment_confirmation', args=[student_id]) + f"?receipt_no={receipt_no}"
            return redirect(confirmation_url)
                
    except Exception as e:
        logger.error(f"Payment processing error: {sanitize_log_input(str(e))}")
        return JsonResponse({
            "status": "error",
            "message": "We couldn't process your payment right now. Please try again or contact support.",
            "show_message": True
        }, status=500)

@module_required('payments', 'view')
def student_fee_preview(request, student_id):
    """Student fee preview using centralized calculation service"""
    try:
        student_id = validate_numeric_id(student_id, "Student ID")
        student = get_object_or_404(Student.objects.all_statuses(), pk=student_id)
        
        # Use integrated fee service with fallback
        balance_info = integrated_service.get_student_balance_info(student)
        payment_history = integrated_service.get_student_payment_history(student)
        
        # Fallback to local service if integrated service returns empty values
        if not balance_info or not isinstance(balance_info, dict) or 'total_balance' not in balance_info:
            logger.warning(f"Integrated service returned invalid balance, using local fallback for student {student.id}")
            balance_info = FeeCalculationService.calculate_student_balance(student)
            
        if not payment_history or not isinstance(payment_history, dict) or 'total_paid' not in payment_history:
            logger.warning(f"Integrated service returned invalid payment history, using local fallback for student {student.id}")
            payment_history = FeeReportingService.get_student_payment_history(student)
        
        # ML Insights
        ml_insights = {}
        if ML_AVAILABLE:
            try:
                ml_insights = ml_service.get_student_insights(student.id)
            except Exception:
                ml_insights = {}
        
        # Calculate due amount using SAME logic as reports view for consistency
        applied_fees = Decimal(str(balance_info.get('current_session', {}).get('total_fees', 0)))
        cf_amount = Decimal(str(balance_info.get('carry_forward', {}).get('total_due', 0)))
        fine_amount = Decimal(str(balance_info.get('fines', {}).get('unpaid', 0)))
        total_fees_due = applied_fees + cf_amount + fine_amount
        
        # Use same calculation as reports: Total fees - Total paid - Total discount + Unpaid fines
        total_received = Decimal(str(payment_history.get('total_paid', 0)))
        total_discount = Decimal(str(payment_history.get('total_discount', 0)))
        total_due = max(total_fees_due - total_received - total_discount + fine_amount, Decimal('0'))
        
        # Debug logging
        logger.info(f"🔍 [DUE CALC] Student {student.id}: applied_fees={applied_fees}, cf_amount={cf_amount}, fine_amount={fine_amount}, total_due={total_due}")
        logger.info(f"🔍 [DUE CALC] total_received={total_received}, payment_history.total_paid={payment_history.get('total_paid', 0)}")
        logger.info(f"🔍 [DUE CALC] fine_paid_amount={balance_info.get('fines', {}).get('paid', 0)}, balance_info.total_balance={balance_info.get('total_balance', 0)}")
        
        # Calculate separate payment totals
        all_payments = payment_history.get('all_payments', [])
        fee_payments_only = sum(d.paid_amount for d in all_payments if not ('Fine Payment' in (d.note or '') or 'Carry Forward' in (d.note or '')))
        fine_payments_only = sum(d.paid_amount for d in all_payments if 'Fine Payment' in (d.note or ''))
        cf_payments_only = sum(d.paid_amount for d in all_payments if 'Carry Forward' in (d.note or ''))
        
        # Fee Payments should only include Applied Fees + Carry Forward (NOT fines)
        fee_payments_total = fee_payments_only + cf_payments_only
        
        context = {
            'student': student,
            'payment_history': payment_history,
            'balance_info': balance_info,
            'ml_insights': ml_insights,
            # Template compatibility with safe access
            'applied_fees': applied_fees,
            'cf_balance': cf_amount,
            'total_paid': fee_payments_total,  # Only fee + CF payments (NOT fines)
            'total_discount': payment_history.get('total_discount', 0),
            'balance': total_due,  # Use calculated due amount instead of total_balance
            'deposits': all_payments,
            'fine_paid_amount': fine_payments_only,  # Only fine payments
            'fine_unpaid_amount': fine_amount
        }
        
        # Final debug log
        logger.info(f"🔍 [DUE CALC] Final context balance (due amount): {total_due}")
        logger.info(f"🔍 [DUE CALC] Debug totals - Fee: {fee_payments_only}, Fine: {fine_payments_only}, CF: {cf_payments_only}")
        logger.info(f"🔍 [DUE CALC] Payment history total_paid: {payment_history.get('total_paid', 0)}")
        
        # Verify payment calculation
        actual_total = fee_payments_only + fine_payments_only + cf_payments_only
        reported_total = payment_history.get('total_paid', 0)
        if abs(actual_total - reported_total) > 0.01:
            logger.warning(f"🚨 [DUE CALC] Payment total mismatch! Actual: {actual_total}, Reported: {reported_total}")
        
        return render(request, 'student_fees/student_fee_preview.html', context)
        
    except Exception as e:
        logger.error(f"Error in student fee preview: {sanitize_log_input(str(e))}")
        messages.error(request, "We're having trouble loading the fee information. Please try again.")
        return redirect('student_fees:fee_deposit')

@module_required('payments', 'view')
def receipt_view(request, receipt_no):
    """Receipt view - uses service layer"""
    try:
        receipt_data = FeeReportingService.get_receipt_data(receipt_no)
        school = SchoolProfile.objects.first()
        
        payments = receipt_data['deposits']
        fine_payments = payments.filter(note__icontains="Fine Payment")
        cf_payments = payments.filter(note__icontains="Carry Forward Payment")
        regular_payments = payments.exclude(note__icontains="Fine Payment").exclude(note__icontains="Carry Forward Payment")
        
        return render(request, 'student_fees/receipt.html', {
            'school': school,
            'student': receipt_data['student'],
            'class_name': receipt_data['student'].class_section.class_name if receipt_data['student'].class_section else '',
            'receipt_no': receipt_data['receipt_no'],
            'deposit_date': receipt_data['deposit_date'],
            'payments': payments,
            'regular_payments': regular_payments,
            'cf_payments': cf_payments,
            'fine_payments': fine_payments,
            'total_amount': receipt_data['total_amount'],
            'total_discount': receipt_data['total_discount'],
            'total_paid': receipt_data['total_paid'],
            'show_discount': any(p.discount for p in payments),
            'copy_labels': ['Original', 'Duplicate']
        })
        
    except ValueError as e:
        raise Http404(str(e))
    except Exception as e:
        logger.exception(f"Error loading receipt {sanitize_log_input(receipt_no)}")
        raise Http404("Error loading receipt") from e

@module_required('payments', 'view')
def payment_confirmation(request, student_id):
    try:
        student_id = validate_numeric_id(student_id, "Student ID")
    except ValidationError:
        raise Http404("Invalid student ID")
    
    student = get_object_or_404(Student.objects.all_statuses(), pk=student_id)
    receipt_no = request.GET.get('receipt_no') or request.session.get('last_receipt_no')
    
    if not receipt_no:
        all_deposits = FeeDeposit.objects.filter(student=student).order_by('-deposit_date')
        receipt_no = all_deposits.first().receipt_no if all_deposits.exists() else None
    
    deposits = FeeDeposit.objects.filter(student=student, receipt_no=receipt_no) if receipt_no else FeeDeposit.objects.none()
    
    fine_deposits = deposits.filter(note__icontains="Fine Payment")
    cf_deposits = deposits.filter(note__icontains="Carry Forward Payment")
    regular_deposits = deposits.exclude(note__icontains="Fine Payment").exclude(note__icontains="Carry Forward Payment")
    
    return render(request, 'student_fees/payment_confirmation.html', {
        'student': student,
        'deposits': deposits,
        'regular_deposits': regular_deposits,
        'cf_deposits': cf_deposits,
        'fine_deposits': fine_deposits,
        'receipt_no': receipt_no,
        'deposit_date': deposits.first().deposit_date if deposits.exists() else django_timezone.now(),
        'total_amount': sum(d.amount for d in deposits),
        'total_discount': sum(d.discount for d in deposits),
        'total_paid': sum(d.paid_amount for d in deposits)
    })

@require_POST
@module_required('payments', 'edit')
def bulk_delete_deposits(request):
    """Bulk delete multiple payment deposits"""
    try:
        student_id = request.POST.get('student_id')
        payment_ids = request.POST.getlist('payment_ids')
        
        if not student_id or not payment_ids:
            messages.error(request, "Please select valid payments to delete.")
            return redirect('student_fees:fee_deposit')
        
        student_id = validate_numeric_id(student_id, "Student ID")
        student = get_object_or_404(Student.objects.all_statuses(), pk=student_id)
        
        # Validate payment IDs and get deposits
        deposits = []
        for payment_id in payment_ids:
            try:
                payment_id = validate_numeric_id(payment_id, "Payment ID")
                deposit = FeeDeposit.objects.get(id=payment_id, student=student)
                deposits.append(deposit)
            except (ValidationError, FeeDeposit.DoesNotExist):
                continue
        
        if not deposits:
            messages.error(request, "We couldn't find the selected payments. Please try again.")
            return redirect('student_fees:student_fee_preview', student_id=student_id)
        
        # Delete deposits in transaction
        with transaction.atomic():
            total_amount = sum(d.paid_amount for d in deposits)
            count = len(deposits)
            
            for deposit in deposits:
                deposit.delete()
            
            messages.success(
                request,
                f"Perfect! We've removed {count} payment(s) totaling ₹{total_amount}. The amounts are now showing as unpaid."
            )
        
        return redirect('student_fees:student_fee_preview', student_id=student_id)
        
    except Exception as e:
        logger.error(f"Error in bulk delete: {sanitize_log_input(str(e))}")
        messages.error(request, "We couldn't delete the selected payments. Please try again.")
        student_id = request.POST.get('student_id')
        if student_id:
            return redirect('student_fees:student_fee_preview', student_id=student_id)
        return redirect('student_fees:fee_deposit')