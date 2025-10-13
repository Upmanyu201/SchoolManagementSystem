# core/fee_management/calculators.py
"""
ATOMIC FEE CALCULATOR - Single Source of Truth
Fixes all identified issues with centralized, consistent calculations
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from django.db.models import Sum, Q, F
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class AtomicFeeCalculator:
    """SINGLE SOURCE OF TRUTH for all fee calculations"""
    
    # Constants for consistency
    DECIMAL_PLACES = 2
    ROUNDING = ROUND_HALF_UP
    CACHE_TIMEOUT = 300  # 5 minutes
    
    @classmethod
    def _to_decimal(cls, value):
        """Consistent decimal conversion"""
        if value is None:
            return Decimal('0.00')
        return Decimal(str(value)).quantize(Decimal('0.01'), rounding=cls.ROUNDING)
    
    @classmethod
    def _get_cache_key(cls, prefix, student_id, *args):
        """Consistent cache key generation"""
        key_parts = [prefix, str(student_id)] + [str(arg) for arg in args]
        return '_'.join(key_parts)
    
    @classmethod
    def get_applicable_fees(cls, student):
        """SINGLE SOURCE: Get applicable fees for student"""
        from fees.models import FeesType
        from transport.models import TransportAssignment
        
        if not student.class_section:
            return FeesType.objects.filter(
                Q(class_name__isnull=True) | Q(class_name='')
            ).exclude(fee_group__group_type="Transport")
        
        # FIXED: Consistent class matching using display_name
        class_display = student.class_section.display_name
        
        regular_fees = FeesType.objects.filter(
            Q(class_name__isnull=True) | 
            Q(class_name='') |
            Q(class_name__iexact=class_display)
        ).exclude(fee_group__group_type="Transport")
        
        # Transport fees if assigned
        transport_fees = []
        try:
            assignment = TransportAssignment.objects.select_related('stoppage').filter(
                student=student
            ).first()
            if assignment and assignment.stoppage:
                transport_fees = FeesType.objects.filter(
                    fee_group__group_type="Transport",
                    related_stoppage=assignment.stoppage
                )
        except Exception:
            pass
        
        return list(regular_fees) + list(transport_fees)
    
    @classmethod
    @transaction.atomic
    def calculate_student_balance(cls, student):
        """ATOMIC: Calculate complete student balance"""
        cache_key = cls._get_cache_key('balance', student.id, timezone.now().hour)
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Get applicable fees
        applicable_fees = cls.get_applicable_fees(student)
        current_fees_total = cls._to_decimal(sum(fee.amount for fee in applicable_fees))
        
        # Current session payments - FIXED: Properly separate from carry forward
        from student_fees.models import FeeDeposit
        
        # Get ALL payments first
        all_payments = FeeDeposit.objects.filter(
            student=student,
            paid_amount__gt=0
        ).exclude(
            Q(receipt_no__startswith="AUTO-")
        )
        
        # Separate current session from carry forward payments
        current_payments = all_payments.exclude(
            Q(note__icontains="Fine Payment") | 
            Q(note__icontains="Carry Forward")
        ).aggregate(
            paid=Sum('paid_amount'),
            discount=Sum('discount')
        )
        
        current_paid = cls._to_decimal(current_payments['paid'])
        current_discount = cls._to_decimal(current_payments['discount'])
        current_balance = max(current_fees_total - current_paid - current_discount, Decimal('0.00'))
        
        # Carry forward - FIXED: Only include actual carry forward payments
        cf_original = cls._to_decimal(student.due_amount)
        cf_payments = all_payments.filter(
            note__icontains="Carry Forward"
        ).aggregate(
            paid=Sum('paid_amount'),
            discount=Sum('discount')
        )
        
        cf_paid = cls._to_decimal(cf_payments['paid'])
        cf_discount = cls._to_decimal(cf_payments['discount'])
        cf_balance = max(cf_original - cf_paid - cf_discount, Decimal('0.00'))
        
        # Debug logging for payment separation
        logger.info(f"Student {student.admission_number} payment breakdown:")
        logger.info(f"  Current session: Fees={current_fees_total}, Paid={current_paid}, Discount={current_discount}, Balance={current_balance}")
        logger.info(f"  Carry forward: Original={cf_original}, Paid={cf_paid}, Discount={cf_discount}, Balance={cf_balance}")
        logger.info(f"  Total payments found: {all_payments.count()}")
        logger.info(f"  Current session payments: {all_payments.exclude(Q(note__icontains='Fine Payment') | Q(note__icontains='Carry Forward')).count()}")
        logger.info(f"  Carry forward payments: {all_payments.filter(note__icontains='Carry Forward').count()}")
        
        # Fines
        fine_data = cls._calculate_fine_balance(student)
        fine_unpaid = cls._to_decimal(fine_data['unpaid'])
        
        # SINGLE CALCULATION FORMULA
        total_balance = current_balance + cf_balance + fine_unpaid
        
        logger.info(f"  Final totals: Current={current_balance}, CF={cf_balance}, Fines={fine_unpaid}, Total={total_balance}")
        
        result = {
            'current_session': {
                'total_fees': current_fees_total,
                'paid': current_paid,
                'discount': current_discount,
                'balance': current_balance
            },
            'carry_forward': {
                'total_due': cf_original,
                'paid': cf_paid,
                'discount': cf_discount,
                'balance': cf_balance
            },
            'fines': fine_data,
            'total_balance': total_balance
        }
        
        cache.set(cache_key, result, cls.CACHE_TIMEOUT)
        return result
    
    @classmethod
    def _calculate_fine_balance(cls, student):
        """Calculate fine balance with proper filtering"""
        try:
            from fines.models import FineStudent
            
            fine_records = FineStudent.objects.filter(
                student=student
            ).select_related('fine', 'fine__fine_type', 'fine__class_section')
            
            paid_amount = Decimal('0.00')
            unpaid_amount = Decimal('0.00')
            
            for fs in fine_records:
                fine = fs.fine
                # Proper relevance check
                if (fine.target_scope == 'Individual' or 
                    fine.target_scope == 'All' or 
                    (fine.target_scope == 'Class' and fine.class_section == student.class_section)):
                    
                    amount = cls._to_decimal(fine.amount)
                    if fs.is_paid:
                        paid_amount += amount
                    else:
                        unpaid_amount += amount
            
            return {
                'paid': paid_amount,
                'unpaid': unpaid_amount,
                'balance': unpaid_amount
            }
        except Exception as e:
            logger.error(f"Fine calculation error: {str(e)}")
            return {
                'paid': Decimal('0.00'),
                'unpaid': Decimal('0.00'),
                'balance': Decimal('0.00')
            }
    
    @classmethod
    def get_payable_fees(cls, student, discount_enabled=False):
        """Get payable fees with corrected calculations matching JS"""
        balance_info = cls.calculate_student_balance(student)
        payable_fees = []
        
        # Carry forward
        cf_balance = balance_info['carry_forward']['balance']
        cf_original = balance_info['carry_forward']['total_due']
        cf_paid = balance_info['carry_forward']['paid']
        cf_discount_paid = balance_info['carry_forward']['discount']
        
        if cf_balance > 0:
            # CORRECTED: Payable = Remaining balance (Original - Paid - DiscountPaid)
            payable_amount = cf_balance  # This is already calculated as remaining balance
            
            current_discount = cls._to_decimal(payable_amount * Decimal('0.05')) if discount_enabled else Decimal('0.00')
            
            # Due = Payable amount (what's still owed)
            due_amount = payable_amount
            
            payable_fees.append({
                'id': 'carry_forward',
                'type': 'carry_forward',
                'display_name': 'Previous Session Balance',
                'amount': cf_original,
                'paid_amount': cf_paid,
                'discount_paid': cf_discount_paid,
                'payable': payable_amount,  # FIXED: Show remaining payable amount
                'discount': current_discount,
                'due': due_amount,
                'is_overdue': True
            })
        
        # Current fees
        applicable_fees = cls.get_applicable_fees(student)
        from student_fees.models import FeeDeposit
        
        for fee in applicable_fees:
            fee_name = f"{fee.fee_group.group_type} - {fee.amount_type}"
            
            # FIXED: Multiple matching strategies for payments
            # Try exact match first
            payment_data = FeeDeposit.objects.filter(
                student=student,
                note__exact=f'Fee Payment: {fee_name}'
            ).aggregate(
                paid=Sum('paid_amount'),
                discount=Sum('discount')
            )
            
            # If no exact match, try broader matching
            if not payment_data['paid']:
                payment_data = FeeDeposit.objects.filter(
                    student=student
                ).filter(
                    Q(note__icontains=fee.amount_type) &
                    Q(note__icontains=fee.fee_group.group_type)
                ).exclude(
                    Q(note__icontains="Fine Payment") |
                    Q(note__icontains="Carry Forward")
                ).aggregate(
                    paid=Sum('paid_amount'),
                    discount=Sum('discount')
                )
            
            paid = cls._to_decimal(payment_data['paid'])
            discount_paid = cls._to_decimal(payment_data['discount'])
            original_amount = cls._to_decimal(fee.amount)
            
            # CORRECTED: Payable = Remaining amount after payments
            payable_amount = max(original_amount - paid - discount_paid, Decimal('0.00'))
            
            if payable_amount > 0:
                # Current discount (if enabled)
                current_discount = cls._to_decimal(payable_amount * Decimal('0.05')) if discount_enabled else Decimal('0.00')
                
                # Due = Payable amount (what's still owed)
                due_amount = payable_amount
                
                payable_fees.append({
                    'id': fee.id,
                    'type': 'fee',
                    'display_name': fee_name,
                    'amount': original_amount,  # Original fee amount (never changes)
                    'paid_amount': paid,        # Amount paid before
                    'discount_paid': discount_paid,  # Discount given before
                    'payable': payable_amount,  # FIXED: Show remaining payable amount
                    'discount': current_discount,  # Current discount
                    'due': due_amount,          # Final due amount
                    'is_overdue': False
                })
            
            # Debug logging with payment matching info
            logger.info(f"Fee {fee_name}: Original={original_amount}, Paid={paid}, Discount={discount_paid}, Payable={due_amount}")
            logger.info(f"  Payment search: 'Fee Payment: {fee_name}' and fallback: {fee.amount_type} + {fee.fee_group.group_type}")
        
        # Unpaid fines
        cls._add_payable_fines(student, payable_fees)
        
        # Final debug log
        logger.info(f"Total payable fees for student {student.id}: {len(payable_fees)}")
        for fee in payable_fees:
            logger.info(f"  {fee['display_name']}: Amount={fee['amount']}, Paid={fee['paid_amount']}, Payable={fee['payable']}, Due={fee['due']}")
        
        return payable_fees
    
    @classmethod
    def _add_payable_fines(cls, student, payable_fees):
        """Add unpaid fines to payable fees"""
        try:
            from fines.models import FineStudent
            
            unpaid_fines = FineStudent.objects.filter(
                student=student,
                is_paid=False
            ).select_related('fine', 'fine__fine_type')
            
            for fs in unpaid_fines:
                fine = fs.fine
                if (fine.target_scope == 'Individual' or 
                    fine.target_scope == 'All' or 
                    (fine.target_scope == 'Class' and fine.class_section == student.class_section)):
                    
                    amount = cls._to_decimal(fine.amount)
                    # Fines are always fully due (no partial payments)
                    payable_fees.append({
                        'id': f"fine_{fine.id}",
                        'type': 'fine',
                        'display_name': f"Fine: {fine.fine_type.name}",
                        'amount': amount,
                        'paid_amount': Decimal('0.00'),
                        'discount_paid': Decimal('0.00'),
                        'payable': amount,  # Fines show full amount as payable
                        'discount': Decimal('0.00'),
                        'due': amount,  # For fines, due = full amount
                        'is_overdue': True
                    })
        except Exception as e:
            logger.error(f"Fine processing error: {str(e)}")
    
    @classmethod
    @transaction.atomic
    def process_payment(cls, student, payment_data):
        """ATOMIC: Process payment with corrected validation"""
        try:
            from student_fees.models import FeeDeposit
            from fines.models import Fine, FineStudent
            from fees.models import FeesType
            
            receipt_no = cls._generate_receipt_number()
            if not receipt_no or len(receipt_no) < 5:
                raise ValidationError("Failed to generate receipt number")
            
            deposits = []
            total_paid = Decimal('0.00')
            
            for item in payment_data['selected_fees']:
                fee_id = item['id']
                original_amount = cls._to_decimal(item['amount'])
                discount = cls._to_decimal(item.get('discount', 0))
                
                # CORRECTED: Use custom payable if provided, otherwise use calculated
                if 'custom_payable' in item and item['custom_payable'] is not None:
                    paid_amount = cls._to_decimal(item['custom_payable'])
                else:
                    paid_amount = original_amount - discount
                
                if paid_amount <= 0:
                    continue
                
                deposit_data = {
                    'student': student,
                    'amount': original_amount,  # Always store original amount
                    'discount': discount,
                    'paid_amount': paid_amount,  # Actual payment amount
                    'receipt_no': receipt_no,
                    'payment_mode': payment_data.get('payment_mode', 'Cash'),
                    'transaction_no': payment_data.get('transaction_no', ''),
                    'payment_source': payment_data.get('payment_source', ''),
                    'deposit_date': timezone.now()
                }
                
                if fee_id == 'carry_forward':
                    deposit_data['note'] = 'Carry Forward Payment'
                elif fee_id.startswith('fine_'):
                    fine_id = int(fee_id.replace('fine_', ''))
                    fine = Fine.objects.get(id=fine_id)
                    deposit_data['note'] = f'Fine Payment: {fine.fine_type.name}'
                    # Mark fine as paid only if fully paid
                    if paid_amount >= original_amount:
                        FineStudent.objects.filter(fine=fine, student=student).update(
                            is_paid=True,
                            payment_date=timezone.now().date()
                        )
                else:
                    fee = FeesType.objects.get(id=fee_id)
                    deposit_data['note'] = f'Fee Payment: {fee.fee_group.group_type} - {fee.amount_type}'
                
                deposits.append(FeeDeposit(**deposit_data))
                total_paid += paid_amount
            
            # Bulk create with validation
            for deposit in deposits:
                deposit.full_clean()
            
            FeeDeposit.objects.bulk_create(deposits)
            
            # Clear cache
            cls._clear_student_cache(student)
            
            return {
                'success': True,
                'receipt_no': receipt_no,
                'total_paid': total_paid,
                'deposits_created': len(deposits)
            }
            
        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")
            raise ValidationError(f"Payment failed: {str(e)}")
    
    @classmethod
    def _generate_receipt_number(cls):
        """Generate unique receipt number"""
        import uuid
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:8].upper()
        return f"RCP{timestamp}{unique_id}"
    
    @classmethod
    def _clear_student_cache(cls, student):
        """Clear all cached data for student"""
        cache_patterns = [
            cls._get_cache_key('balance', student.id, '*'),
            f"student_fees_{student.id}_*",
            f"payable_fees_{student.id}_*"
        ]
        
        # Clear cache keys
        for hour in range(24):
            cache_key = cls._get_cache_key('balance', student.id, hour)
            cache.delete(cache_key)
    
    @classmethod
    def calculate_partial_payment_due(cls, original_amount, paid_amount, discount_paid, custom_payable=None, current_discount=0):
        """Calculate due amount for partial payments - matches JS logic"""
        original = cls._to_decimal(original_amount)
        paid = cls._to_decimal(paid_amount)
        discount_paid_amount = cls._to_decimal(discount_paid)
        current_disc = cls._to_decimal(current_discount)
        
        # CORRECTED: Payable = Original - (Paid + DiscountPaid)
        max_payable = original - paid - discount_paid_amount
        
        if custom_payable is not None:
            # Custom partial payment
            custom_pay = cls._to_decimal(custom_payable)
            # Ensure custom payable doesn't exceed max allowed
            actual_payable = min(custom_pay, max_payable)
            # Due = What user is paying now (the custom payable amount)
            due_amount = actual_payable
        else:
            # Standard calculation - due equals payable
            due_amount = max_payable
        
        return {
            'payable': max(max_payable, Decimal('0.00')),
            'due': due_amount,
            'max_allowed_payable': max(max_payable, Decimal('0.00'))
        }
    
    @classmethod
    def validate_payment_amounts(cls, fee_data):
        """Validate payment amounts before processing"""
        errors = []
        
        for fee in fee_data:
            original = cls._to_decimal(fee.get('amount', 0))
            paid = cls._to_decimal(fee.get('paid_amount', 0))
            discount_paid = cls._to_decimal(fee.get('discount_paid', 0))
            custom_payable = fee.get('custom_payable')
            
            calc = cls.calculate_partial_payment_due(
                original, paid, discount_paid, custom_payable
            )
            
            if custom_payable is not None:
                custom_pay = cls._to_decimal(custom_payable)
                if custom_pay > calc['max_allowed_payable']:
                    errors.append(
                        f"Payment amount ₹{custom_pay} exceeds maximum allowed "
                        f"₹{calc['max_allowed_payable']} for {fee.get('display_name', 'fee')}"
                    )
                elif custom_pay <= 0:
                    errors.append(
                        f"Payment amount must be greater than zero for {fee.get('display_name', 'fee')}"
                    )
        
        return errors

# Singleton instance
atomic_calculator = AtomicFeeCalculator()

# Export for backward compatibility
AtomicFeeCalculator.instance = atomic_calculator