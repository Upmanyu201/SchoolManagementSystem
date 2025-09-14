# core/fee_calculation_engine.py

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, date
from django.db.models import Sum, Q, F
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.html import escape
from core.security_utils import sanitize_input, validate_file_upload
import logging
import os

logger = logging.getLogger(__name__)

@dataclass
class FeeBreakdown:
    """Structured fee breakdown for calculations"""
    carry_forward: Decimal = field(default_factory=lambda: Decimal('0'))
    current_session_fees: Decimal = field(default_factory=lambda: Decimal('0'))
    transport_fees: Decimal = field(default_factory=lambda: Decimal('0'))
    fine_amount: Decimal = field(default_factory=lambda: Decimal('0'))
    total_fees: Decimal = field(default_factory=lambda: Decimal('0'))
    
    total_paid: Decimal = field(default_factory=lambda: Decimal('0'))
    total_discount: Decimal = field(default_factory=lambda: Decimal('0'))
    fine_paid: Decimal = field(default_factory=lambda: Decimal('0'))
    
    outstanding_balance: Decimal = field(default_factory=lambda: Decimal('0'))
    
    def calculate_totals(self):
        """Calculate derived totals"""
        self.total_fees = self.carry_forward + self.current_session_fees + self.transport_fees
        self.outstanding_balance = self.total_fees + self.fine_amount - self.total_paid - self.total_discount - self.fine_paid

@dataclass
class PaymentBreakdown:
    """Payment processing breakdown"""
    selected_fees: List[Dict] = field(default_factory=list)
    total_amount: Decimal = field(default_factory=lambda: Decimal('0'))
    total_discount: Decimal = field(default_factory=lambda: Decimal('0'))
    payable_amount: Decimal = field(default_factory=lambda: Decimal('0'))
    payment_method: str = 'Cash'
    transaction_details: Dict = field(default_factory=dict)

class FeeCalculationEngine:
    """Enterprise-grade fee calculation algorithm with advanced optimization"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def get_calculation_settings(self):
        """Get current calculation settings from database"""
        try:
            from fees.models import FeeCalculationSettings
            return FeeCalculationSettings.get_settings()
        except ImportError:
            # Fallback to default values if model doesn't exist
            from types import SimpleNamespace
            return SimpleNamespace(
                late_fee_enabled=True,
                late_fee_percentage=Decimal('5'),
                grace_period_days=7,
                bulk_discount_enabled=True,
                bulk_discount_threshold=Decimal('10000'),
                bulk_discount_percentage=Decimal('2'),
                auto_calculate_late_fees=False,
                auto_apply_bulk_discounts=True
            )
        
    def get_student_fee_summary(self, student) -> FeeBreakdown:
        """
        Calculate complete fee summary for student dashboard
        Integrates data from all fee-related templates
        """
        cache_key = f"fee_summary_{student.admission_number}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
            
        breakdown = FeeBreakdown()
        
        try:
            # a. Carry Forward Amount (from fees_carry_forward.html)
            breakdown.carry_forward = self._get_carry_forward_amount(student)
            
            # b. Current Session Due (from fees_rows.html)
            breakdown.current_session_fees = self._get_current_session_dues(student)
            
            # c. Transport fees if applicable
            breakdown.transport_fees = self._get_transport_fees(student)
            
            # d. Fine amounts (from fine_history.html)
            breakdown.fine_amount = self._get_unpaid_fines_total(student)
            
            # Payment calculations (from student_fee_preview.html)
            payment_data = self._get_payment_summary(student)
            breakdown.total_paid = payment_data['total_paid']
            breakdown.total_discount = payment_data['total_discount']
            breakdown.fine_paid = payment_data['fine_paid']
            
            # Calculate final totals
            breakdown.calculate_totals()
            
            # Cache the result
            cache.set(cache_key, breakdown, self.cache_timeout)
            
            logger.info(f"Fee summary calculated for {student.admission_number}: Outstanding Rs{breakdown.outstanding_balance}")
            
        except Exception as e:
            logger.error(f"Error calculating fee summary for {sanitize_input(student.admission_number)}: {sanitize_input(str(e))}")
            
        return breakdown
    
    def _get_carry_forward_amount(self, student) -> Decimal:
        """Get carry forward amount from previous session"""
        try:
            # Check if student has carry forward record
            cf_amount = getattr(student, 'due_amount', Decimal('0'))
            
            # Get carry forward from fee deposits marked as CF
            from student_fees.models import FeeDeposit
            cf_deposits = FeeDeposit.objects.filter(
                student=student,
                note__icontains="Carry Forward"
            ).aggregate(
                total_cf=Sum('amount'),
                paid_cf=Sum('paid_amount')
            )
            
            cf_total = cf_deposits.get('total_cf') or Decimal('0')
            cf_paid = cf_deposits.get('paid_cf') or Decimal('0')
            
            return max(cf_total - cf_paid, Decimal('0'))
            
        except Exception as e:
            logger.error(f"Error getting carry forward for {sanitize_input(student.admission_number)}: {sanitize_input(str(e))}")
            return Decimal('0')
    
    def _get_current_session_dues(self, student) -> Decimal:
        """Calculate current session fees (excluding CF and fines)"""
        try:
            from fees.models import FeesType
            from student_fees.models import FeeDeposit
            
            # Get applicable fees for current session
            class_name = student.class_section.class_name if student.class_section else 'N/A'
            applicable_fees = FeesType.objects.filter(
                Q(class_name__isnull=True) | Q(class_name__iexact=class_name)
            ).exclude(
                fee_group__group_type="Transport"
            )
            
            total_applicable = sum(fee.amount for fee in applicable_fees)
            
            # Get current session payments (exclude CF and fine payments)
            current_payments = FeeDeposit.objects.filter(
                student=student,
                fees_type__isnull=False
            ).exclude(
                Q(note__icontains="Fine Payment") | Q(note__icontains="Carry Forward")
            ).aggregate(
                paid=Sum('paid_amount'),
                discount=Sum('discount')
            )
            
            total_paid = current_payments.get('paid') or Decimal('0')
            total_discount = current_payments.get('discount') or Decimal('0')
            
            return max(total_applicable - total_paid - total_discount, Decimal('0'))
            
        except Exception as e:
            logger.error(f"Error calculating current session dues for {sanitize_input(student.admission_number)}: {sanitize_input(str(e))}")
            return Decimal('0')
    
    def _get_transport_fees(self, student) -> Decimal:
        """Calculate transport fees if student is assigned to transport"""
        try:
            from transport.models import TransportAssignment
            from fees.models import FeesType
            
            transport_assignment = TransportAssignment.objects.filter(student=student).first()
            if not transport_assignment:
                return Decimal('0')
            
            transport_fees = FeesType.objects.filter(
                fee_group__group_type="Transport",
                related_stoppage=transport_assignment.stoppage
            )
            
            return sum(fee.amount for fee in transport_fees)
            
        except Exception as e:
            logger.error(f"Error calculating transport fees for {sanitize_input(student.admission_number)}: {sanitize_input(str(e))}")
            return Decimal('0')
    
    def _get_unpaid_fines_total(self, student) -> Decimal:
        """Get total unpaid fines amount"""
        try:
            from fines.models import FineStudent
            
            unpaid_fines = FineStudent.objects.filter(
                student=student,
                is_paid=False
            ).select_related('fine')
            
            return sum(fs.fine.amount for fs in unpaid_fines)
            
        except Exception as e:
            logger.error(f"Error calculating unpaid fines for {sanitize_input(student.admission_number)}: {sanitize_input(str(e))}")
            return Decimal('0')
    
    def _get_payment_summary(self, student) -> Dict:
        """Get comprehensive payment summary"""
        try:
            from student_fees.models import FeeDeposit
            
            # Regular fee payments
            regular_payments = FeeDeposit.objects.filter(
                student=student
            ).exclude(
                note__icontains="Fine Payment"
            ).aggregate(
                total_paid=Sum('paid_amount'),
                total_discount=Sum('discount')
            )
            
            # Fine payments
            fine_payments = FeeDeposit.objects.filter(
                student=student,
                note__icontains="Fine Payment"
            ).aggregate(
                fine_paid=Sum('paid_amount')
            )
            
            return {
                'total_paid': regular_payments.get('total_paid') or Decimal('0'),
                'total_discount': regular_payments.get('total_discount') or Decimal('0'),
                'fine_paid': fine_payments.get('fine_paid') or Decimal('0')
            }
            
        except Exception as e:
            logger.error(f"Error getting payment summary for {sanitize_input(student.admission_number)}: {sanitize_input(str(e))}")
            return {
                'total_paid': Decimal('0'),
                'total_discount': Decimal('0'),
                'fine_paid': Decimal('0')
            }
    
    @transaction.atomic
    def process_fee_payment(self, student, payment_data: PaymentBreakdown) -> Dict:
        """
        Process fee payment with comprehensive breakdown update
        Updates payment history and recalculates all amounts
        """
        try:
            from student_fees.models import FeeDeposit
            from fees.models import FeesType
            from fines.models import FineStudent
            
            receipt_no = self._generate_receipt_number()
            payment_records = []
            
            # Process each selected fee
            for fee_item in payment_data.selected_fees:
                fee_type = fee_item.get('type')
                amount = Decimal(str(fee_item.get('amount', 0)))
                discount = Decimal(str(fee_item.get('discount', 0)))
                
                if fee_type == 'carry_forward':
                    # Handle carry forward payment
                    deposit = FeeDeposit.objects.create(
                        student=student,
                        amount=amount,
                        discount=discount,
                        paid_amount=amount - discount,
                        receipt_no=receipt_no,
                        payment_mode=payment_data.payment_method,
                        transaction_no=payment_data.transaction_details.get('transaction_no', ''),
                        payment_source=payment_data.transaction_details.get('payment_source', ''),
                        note="Carry Forward Payment"
                    )
                    payment_records.append(deposit)
                    
                elif fee_type.startswith('fine_'):
                    # Handle fine payment
                    fine_id = fee_type.replace('fine_', '')
                    fine_student = FineStudent.objects.get(
                        fine_id=fine_id,
                        student=student
                    )
                    
                    deposit = FeeDeposit.objects.create(
                        student=student,
                        amount=amount,
                        discount=discount,
                        paid_amount=amount - discount,
                        receipt_no=receipt_no,
                        payment_mode=payment_data.payment_method,
                        transaction_no=payment_data.transaction_details.get('transaction_no', ''),
                        payment_source=payment_data.transaction_details.get('payment_source', ''),
                        note=f"Fine Payment - {escape(fine_student.fine.fine_type.name)}"
                    )
                    
                    # Mark fine as paid
                    fine_student.is_paid = True
                    fine_student.payment_date = timezone.now().date()
                    fine_student.save()
                    
                    payment_records.append(deposit)
                    
                else:
                    # Handle regular fee payment
                    try:
                        fees_type = FeesType.objects.get(id=fee_type)
                        deposit = FeeDeposit.objects.create(
                            student=student,
                            fees_type=fees_type,
                            fees_group=fees_type.fee_group,
                            amount=amount,
                            discount=discount,
                            paid_amount=amount - discount,
                            receipt_no=receipt_no,
                            payment_mode=payment_data.payment_method,
                            transaction_no=payment_data.transaction_details.get('transaction_no', ''),
                            payment_source=payment_data.transaction_details.get('payment_source', '')
                        )
                        payment_records.append(deposit)
                    except FeesType.DoesNotExist:
                        logger.error(f"FeesType {sanitize_input(str(fee_type))} not found for student {sanitize_input(student.admission_number)}")
            
            # Update student due amount
            student.update_due_amount()
            
            # Clear cache
            self._clear_student_cache(student)
            
            # Generate updated fee summary
            updated_summary = self.get_student_fee_summary(student)
            
            return {
                'success': True,
                'receipt_no': receipt_no,
                'payment_records': payment_records,
                'updated_summary': updated_summary,
                'total_paid': payment_data.payable_amount
            }
            
        except Exception as e:
            logger.error(f"Error processing payment for {sanitize_input(student.admission_number)}: {sanitize_input(str(e))}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_dashboard_summary(self, student) -> Dict:
        """Get complete dashboard summary with all fee information"""
        fee_breakdown = self.get_student_fee_summary(student)
        
        return {
            'financial_overview': {
                'carry_forward': fee_breakdown.carry_forward,
                'current_session_dues': fee_breakdown.current_session_fees,
                'transport_fees': fee_breakdown.transport_fees,
                'unpaid_fines': fee_breakdown.fine_amount,
                'total_outstanding': fee_breakdown.outstanding_balance,
                'total_paid': fee_breakdown.total_paid,
                'total_discount': fee_breakdown.total_discount,
                'fine_paid': fee_breakdown.fine_paid
            },
            'status': {
                'has_dues': fee_breakdown.outstanding_balance > 0,
                'has_fines': fee_breakdown.fine_amount > 0,
                'payment_required': fee_breakdown.outstanding_balance > 0 or fee_breakdown.fine_amount > 0
            }
        }
    
    def _generate_receipt_number(self) -> str:
        """Generate secure unique receipt number"""
        import uuid
        
        # Use timezone-aware timestamp + UUID for uniqueness and security
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:8].upper()
        return f"RCP{timestamp}{unique_id}"
    
    def calculate_late_fees(self, student, due_date: date) -> Decimal:
        """Calculate late fees based on configurable settings"""
        try:
            settings = self.get_calculation_settings()
            
            if not settings.late_fee_enabled or not due_date or due_date >= timezone.now().date():
                return Decimal('0')
            
            days_overdue = (timezone.now().date() - due_date).days
            if days_overdue <= settings.grace_period_days:
                return Decimal('0')
            
            fee_summary = self.get_student_fee_summary(student)
            overdue_amount = fee_summary.outstanding_balance
            
            late_fee = (overdue_amount * settings.late_fee_percentage) / 100
            return late_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            logger.error(f"Error calculating late fees for {sanitize_input(student.admission_number)}: {sanitize_input(str(e))}")
            return Decimal('0')
    
    def calculate_bulk_payment_discount(self, payment_amount: Decimal) -> Decimal:
        """Calculate discount for bulk payments based on configurable settings"""
        try:
            settings = self.get_calculation_settings()
            
            if not settings.bulk_discount_enabled or payment_amount < settings.bulk_discount_threshold:
                return Decimal('0')
            
            discount = (payment_amount * settings.bulk_discount_percentage) / 100
            return discount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            logger.error(f"Error calculating bulk discount: {sanitize_input(str(e))}")
            return Decimal('0')
    
    def get_optimized_payment_plan(self, student) -> Dict:
        """Generate optimized payment plan for student"""
        try:
            fee_summary = self.get_student_fee_summary(student)
            
            # Priority order: Fines > Carry Forward > Current Session > Transport
            payment_plan = []
            
            if fee_summary.fine_amount > 0:
                payment_plan.append({
                    'priority': 1,
                    'type': 'fines',
                    'amount': fee_summary.fine_amount,
                    'description': 'Unpaid Fines (Highest Priority)',
                    'due_immediately': True
                })
            
            if fee_summary.carry_forward > 0:
                payment_plan.append({
                    'priority': 2,
                    'type': 'carry_forward',
                    'amount': fee_summary.carry_forward,
                    'description': 'Previous Session Dues',
                    'due_immediately': True
                })
            
            if fee_summary.current_session_fees > 0:
                payment_plan.append({
                    'priority': 3,
                    'type': 'current_session',
                    'amount': fee_summary.current_session_fees,
                    'description': 'Current Session Fees',
                    'due_immediately': False
                })
            
            if fee_summary.transport_fees > 0:
                payment_plan.append({
                    'priority': 4,
                    'type': 'transport',
                    'amount': fee_summary.transport_fees,
                    'description': 'Transport Fees',
                    'due_immediately': False
                })
            
            # Calculate potential discounts
            total_amount = fee_summary.outstanding_balance + fee_summary.fine_amount
            bulk_discount = self.calculate_bulk_payment_discount(total_amount)
            
            return {
                'payment_plan': payment_plan,
                'total_amount': total_amount,
                'potential_discount': bulk_discount,
                'recommended_action': self._get_payment_recommendation(fee_summary)
            }
            
        except Exception as e:
            logger.error(f"Error generating payment plan for {sanitize_input(student.admission_number)}: {sanitize_input(str(e))}")
            return {}
    
    def _get_payment_recommendation(self, fee_summary: FeeBreakdown) -> str:
        """Get payment recommendation based on fee analysis and settings"""
        settings = self.get_calculation_settings()
        total_outstanding = fee_summary.outstanding_balance + fee_summary.fine_amount
        
        if fee_summary.fine_amount > 0:
            return "Pay fines immediately to avoid additional penalties"
        elif fee_summary.carry_forward > 0:
            return "Clear previous dues to maintain good standing"
        elif settings.bulk_discount_enabled and total_outstanding >= settings.bulk_discount_threshold:
            return f"Pay full amount to get {settings.bulk_discount_percentage}% discount"
        else:
            return "Pay current session fees to stay up to date"
    
    def _clear_student_cache(self, student):
        """Clear all cached data for student"""
        cache_keys = [
            f"fee_summary_{student.admission_number}",
            f"student_dashboard_{student.admission_number}",
            f"student_dashboard_complete_{student.admission_number}"
        ]
        cache.delete_many(cache_keys)
    
    def auto_sync_student_fees(self, student):
        """Auto-sync new fees and fines for student"""
        try:
            if fee_service:
                # Get class fee summary using centralized service
                if hasattr(student, 'class_section') and student.class_section:
                    class_summary = fee_service.get_class_fee_summary(student.class_section.id)
                    logger.info(f"Class summary for {student.class_section.display_name}: {class_summary.get('students_with_dues', 0)} students with dues")
                
                return {'success': True, 'message': 'Fee service integration active'}
            
            return {'success': False, 'error': 'Fee service not available'}
            
        except Exception as e:
            logger.error(f"Error auto-syncing fees for {sanitize_input(student.admission_number)}: {sanitize_input(str(e))}")
            return {'success': False, 'error': str(e)}
    
    def get_student_fee_summary_with_sync(self, student) -> FeeBreakdown:
        """Get fee summary with automatic sync of new fees/fines"""
        # First sync any new fees/fines
        sync_result = self.auto_sync_student_fees(student)
        
        # Then get updated summary
        return self.get_student_fee_summary(student)
    
    def verify_class_fine_application(self, fine_id: int) -> Dict:
        """Verify fine application using centralized service"""
        try:
            if fee_service:
                return fee_service.verify_fine_application(fine_id)
            else:
                return {'error': 'Fee service not available'}
        except Exception as e:
            logger.error(f"Error verifying fine application: {sanitize_input(str(e))}")
            return {'error': str(e)}
    
    def fix_class_fine_application(self, fine_id: int) -> Dict:
        """Fix incorrect fine application using centralized service"""
        try:
            if fee_service:
                return fee_service.fix_incorrect_fine_application(fine_id)
            else:
                return {'success': False, 'error': 'Fee service not available'}
        except Exception as e:
            logger.error(f"Error fixing fine application: {sanitize_input(str(e))}")
            return {'success': False, 'error': str(e)}

# Singleton instance
fee_engine = FeeCalculationEngine()

# Import centralized fee service
try:
    from core.fee_management.services import fee_service
except ImportError:
    fee_service = None
    logger.warning("Fee management service not available")