# student_fees/services.py
"""Centralized fee calculation and processing services"""

from decimal import Decimal
from typing import Dict, List
from django.db.models import Sum, Q
from django.core.cache import cache
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class FeeCalculationService:
    """Centralized fee calculation service - single source of truth"""
    
    @staticmethod
    def get_applicable_fees(student) -> List:
        """Standardized fee matching logic - single source of truth"""
        from fees.models import FeesType
        from transport.models import TransportAssignment
        
        if not student.class_section:
            return FeesType.objects.filter(
                Q(class_name__isnull=True) | Q(class_name='')
            ).exclude(fee_group__group_type="Transport")
        
        class_name = student.class_section.class_name
        class_display = student.class_section.display_name
        
        # FIXED: Use display_name for matching since fees are stored with display names
        fees_query = (
            Q(class_name__isnull=True) | 
            Q(class_name='') |
            Q(class_name__iexact=class_display)  # Use display_name for matching
        )
        
        regular_fees = FeesType.objects.filter(
            fees_query & ~Q(fee_group__group_type="Transport")
        )
        
        # Add transport fees if assigned
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
    
    @staticmethod
    def calculate_student_balance(student) -> Dict:
        """Centralized balance calculation - atomic and consistent"""
        cache_key = f"balance_{student.id}_{hash(str(getattr(student, 'updated_at', 0)))}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Get applicable fees using standardized logic
        applicable_fees = FeeCalculationService.get_applicable_fees(student)
        current_fees_total = sum(fee.amount for fee in applicable_fees)
        
        # Current session payments - exclude fake auto-generated records
        from .models import FeeDeposit
        current_payments = FeeDeposit.objects.filter(
            student=student,
            paid_amount__gt=0  # Only count actual payments
        ).exclude(note__icontains="Fine Payment").exclude(
            note__icontains="Carry Forward"
        ).exclude(
            receipt_no__startswith="AUTO-"  # Exclude auto-generated fake records
        ).aggregate(
            paid=Sum('paid_amount'),
            discount=Sum('discount')
        )
        
        current_paid = current_payments['paid'] or Decimal('0')
        current_discount = current_payments['discount'] or Decimal('0')
        current_balance = max(current_fees_total - current_paid - current_discount, Decimal('0'))
        
        # Carry forward - single source of truth
        cf_original = Decimal(str(student.due_amount or 0))
        cf_payments = FeeDeposit.objects.filter(
            student=student,
            note__icontains="Carry Forward"
        ).aggregate(
            paid=Sum('paid_amount'),
            discount=Sum('discount')
        )
        
        cf_paid = cf_payments['paid'] or Decimal('0')
        cf_discount = cf_payments['discount'] or Decimal('0')
        cf_balance = max(cf_original - cf_paid - cf_discount, Decimal('0'))
        
        # Fines - optimized calculation
        fine_data = FeeCalculationService._calculate_fine_balance(student)
        
        result = {
            'current_session': {
                'total_fees': float(current_fees_total),
                'paid': float(current_paid),
                'discount': float(current_discount),
                'balance': float(current_balance)
            },
            'carry_forward': {
                'total_due': float(cf_original),
                'paid': float(cf_paid),
                'discount': float(cf_discount),
                'balance': float(cf_balance)
            },
            'fines': fine_data,
            'total_balance': float(current_balance + cf_balance + Decimal(str(fine_data['unpaid'])))
        }
        
        cache.set(cache_key, result, 300)  # 5 min cache
        return result
    
    @staticmethod
    def _calculate_fine_balance(student) -> Dict:
        """Optimized fine calculation"""
        try:
            from fines.models import FineStudent
            
            fine_records = FineStudent.objects.filter(
                student=student
            ).select_related('fine', 'fine__fine_type', 'fine__class_section')
            
            # Filter relevant fines
            relevant_fines = []
            for fs in fine_records:
                fine = fs.fine
                if (fine.target_scope == 'Individual' or 
                    fine.target_scope == 'All' or 
                    (fine.target_scope == 'Class' and fine.class_section == student.class_section)):
                    relevant_fines.append(fs)
            
            paid_amount = sum(fs.fine.amount for fs in relevant_fines if fs.is_paid)
            unpaid_amount = sum(fs.fine.amount for fs in relevant_fines if not fs.is_paid)
            
            return {
                'paid': float(paid_amount),
                'unpaid': float(unpaid_amount),
                'balance': float(unpaid_amount)
            }
        except Exception as e:
            logger.error(f"Fine calculation error: {str(e)}")
            return {'paid': 0.0, 'unpaid': 0.0, 'balance': 0.0}
    
    @staticmethod
    def get_payable_fees(student) -> List[Dict]:
        """Get payable fees using local calculation to avoid recursion"""
        logger.info(f"🔍 [FEE CALC] get_payable_fees called for student {student.id} ({student.admission_number})")
        try:
            # Local calculation to avoid recursion
            logger.info(f"🔍 [FEE CALC] Calculating student balance for {student.id}")
            balance_info = FeeCalculationService.calculate_student_balance(student)
            logger.info(f"✅ [FEE CALC] Balance calculated: total_balance={balance_info.get('total_balance', 0)}")
            payable_fees = []
            
            # Carry forward
            cf_balance = balance_info['carry_forward']['balance']
            logger.info(f"🔍 [FEE CALC] Carry forward balance: {cf_balance}")
            if cf_balance > 0:
                payable_fees.append({
                    'id': 'carry_forward',
                    'type': 'carry_forward',  # Add type field for template recognition
                    'fee_type': 'Carry Forward',
                    'display_name': 'Carry Forward - Previous Session Balance',
                    'amount': cf_balance,
                    'is_overdue': True,
                    'due_date': ''
                })
                logger.info(f"✅ [FEE CALC] Added carry forward fee: {cf_balance}")
            
            # Current session fees - use standardized logic
            logger.info(f"🔍 [FEE CALC] Getting applicable fees for student {student.id}")
            applicable_fees = FeeCalculationService.get_applicable_fees(student)
            logger.info(f"✅ [FEE CALC] Found {len(applicable_fees)} applicable fees")
            
            from .models import FeeDeposit
            for fee in applicable_fees:
                try:
                    # Optimized single query - match by note since no fees_type field
                    fee_name = f"{fee.fee_group.group_type} - {fee.amount_type}"
                    payment_data = FeeDeposit.objects.filter(
                        student=student,
                        note__icontains=fee_name
                    ).aggregate(
                        paid=Sum('paid_amount'),
                        discount=Sum('discount')
                    )
                    
                    paid = payment_data['paid'] or Decimal('0')
                    discount = payment_data['discount'] or Decimal('0')
                    remaining = fee.amount - paid - discount
                    
                    if remaining > 0:
                        payable_fees.append({
                            'id': fee.id,
                            'type': 'fee',  # Add type field for template recognition
                            'fee_type': f"{fee.fee_group.group_type} - {fee.amount_type}",
                            'display_name': f"{fee.fee_group.group_type} - {fee.amount_type}",
                            'amount': float(remaining),
                            'is_overdue': False,
                            'due_date': ''
                        })
                except Exception as e:
                    logger.error(f"Fee processing error {fee.id}: {str(e)}")
                    continue
            
            # Unpaid fines
            fines_unpaid = balance_info['fines']['unpaid']
            logger.info(f"🔍 [FEE CALC] Unpaid fines: {fines_unpaid}")
            if fines_unpaid > 0:
                FeeCalculationService._add_payable_fines(student, payable_fees)
                logger.info(f"✅ [FEE CALC] Added unpaid fines to payable fees")
            
            logger.info(f"✅ [FEE CALC] Final payable fees count: {len(payable_fees)}")
            for i, fee in enumerate(payable_fees):
                logger.debug(f"🔍 [FEE CALC] Payable fee {i+1}: {fee['display_name']} - {fee['amount']}")
            return payable_fees
            
        except Exception as e:
            logger.error(f"❌ [FEE CALC] Error in get_payable_fees: {str(e)}")
            return []
    
    @staticmethod
    def _add_payable_fines(student, payable_fees: List[Dict]):
        """Add unpaid fines to payable fees list"""
        try:
            from fines.models import FineStudent
            from datetime import date
            
            today = date.today()
            unpaid_fines = FineStudent.objects.filter(
                student=student,
                is_paid=False,
                fine__due_date__lte=today
            ).select_related('fine', 'fine__fine_type', 'fine__class_section')
            
            for fs in unpaid_fines:
                fine = fs.fine
                # Check relevance
                if (fine.target_scope == 'Individual' or 
                    fine.target_scope == 'All' or 
                    (fine.target_scope == 'Class' and fine.class_section == student.class_section)):
                    
                    display_name = f"Fine: {fine.fine_type.name} - {fine.reason[:50]}"
                    payable_fees.append({
                        'id': f"fine_{fine.id}",
                        'type': 'fine',  # Add type field for template recognition
                        'fee_type': 'Fine',
                        'display_name': display_name,
                        'amount': float(fine.amount),
                        'is_overdue': True,
                        'due_date': fine.due_date.strftime('%Y-%m-%d') if fine.due_date else ''
                    })
        except Exception as e:
            logger.error(f"Fine processing error: {str(e)}")


class PaymentProcessingService:
    """Service for processing payments"""
    
    @staticmethod
    @transaction.atomic
    def process_payment(student_id: int, payment_data: Dict) -> Dict:
        """Process payment with validation and error handling"""
        # Implementation would go here
        pass


class FeeReportingService:
    """Service for fee reporting and history"""
    
    @staticmethod
    def get_student_payment_history(student) -> Dict:
        """Get comprehensive payment history for student"""
        from .models import FeeDeposit
        
        deposits = FeeDeposit.objects.filter(student=student).order_by('-deposit_date')
        regular_deposits = deposits.exclude(note__icontains="Carry Forward").exclude(note__icontains="Fine Payment")
        cf_deposits = deposits.filter(note__icontains="Carry Forward")
        fine_deposits = deposits.filter(note__icontains="Fine Payment")
        
        total_paid = deposits.aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0')
        total_discount = deposits.aggregate(Sum('discount'))['discount__sum'] or Decimal('0')
        
        return {
            'all_payments': deposits,
            'regular_payments': regular_deposits,
            'carry_forward_payments': cf_deposits,
            'fine_payments': fine_deposits,
            'total_paid': float(total_paid),
            'total_discount': float(total_discount)
        }
    
    @staticmethod
    def get_receipt_data(receipt_no: str) -> Dict:
        """Get receipt data for printing"""
        from .models import FeeDeposit
        
        deposits = FeeDeposit.objects.filter(receipt_no=receipt_no)
        if not deposits.exists():
            raise ValueError(f"Receipt {receipt_no} not found")
        
        first_deposit = deposits.first()
        total_amount = deposits.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        total_discount = deposits.aggregate(Sum('discount'))['discount__sum'] or Decimal('0')
        total_paid = deposits.aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0')
        
        return {
            'receipt_no': receipt_no,
            'student': first_deposit.student,
            'deposits': deposits,
            'deposit_date': first_deposit.deposit_date,
            'total_amount': float(total_amount),
            'total_discount': float(total_discount),
            'total_paid': float(total_paid)
        }