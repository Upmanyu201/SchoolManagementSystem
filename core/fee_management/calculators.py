# core/fee_management/calculators.py
"""
Centralized Fee Calculation Engine
All fee and fine calculations happen here
"""

from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Sum, Q
from django.utils import timezone

class FeeCalculator:
    """Main fee calculation engine"""
    
    def calculate_student_fees(self, student, academic_year='2024-25'):
        """Calculate all fees for a student"""
        from fees.models import FeesType
        from .models import StudentFee
        
        # Get applicable fee types for student's class
        applicable_fees = FeesType.objects.filter(
            Q(applicable_to='All') | 
            Q(applicable_to=student.class_section.name if hasattr(student, 'class_section') else 'All')
        )
        
        calculated_fees = []
        for fee_type in applicable_fees:
            # Check if fee already exists for this student
            existing_fee = StudentFee.objects.filter(
                student=student,
                fee_type=fee_type,
                academic_year=academic_year
            ).first()
            
            if not existing_fee:
                # Calculate amount based on fee type
                amount = self._calculate_fee_amount(student, fee_type)
                due_date = self._calculate_due_date(fee_type)
                
                student_fee = StudentFee.objects.create(
                    student=student,
                    fee_type=fee_type,
                    amount=amount,
                    due_date=due_date,
                    academic_year=academic_year
                )
                calculated_fees.append(student_fee)
        
        return calculated_fees
    
    def _calculate_fee_amount(self, student, fee_type):
        """Calculate fee amount based on student and fee type"""
        base_amount = fee_type.base_amount
        
        # Apply any student-specific discounts or adjustments
        # This can be enhanced with scholarship logic, sibling discounts, etc.
        
        return base_amount
    
    def _calculate_due_date(self, fee_type):
        """Calculate due date based on fee frequency"""
        today = date.today()
        
        if fee_type.fee_group.frequency == 'Monthly':
            # Due on 10th of each month
            return date(today.year, today.month, 10)
        elif fee_type.fee_group.frequency == 'Quarterly':
            # Due every 3 months
            return today + timedelta(days=90)
        elif fee_type.fee_group.frequency == 'Yearly':
            # Due at start of academic year
            return date(today.year, 4, 1)  # April 1st
        else:
            # Default: 30 days from today
            return today + timedelta(days=30)
    
    def calculate_total_due(self, student):
        """Calculate total due amount for student"""
        from .models import StudentFee, AppliedFine
        
        # Unpaid fees
        unpaid_fees = StudentFee.objects.filter(
            student=student,
            is_paid=False
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Unpaid fines
        unpaid_fines = AppliedFine.objects.filter(
            student=student,
            is_paid=False
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        return unpaid_fees + unpaid_fines
    
    def get_payment_breakdown(self, student):
        """Get detailed breakdown of what student owes"""
        from .models import StudentFee, AppliedFine
        
        unpaid_fees = StudentFee.objects.filter(student=student, is_paid=False)
        unpaid_fines = AppliedFine.objects.filter(student=student, is_paid=False)
        
        return {
            'fees': list(unpaid_fees),
            'fines': list(unpaid_fines),
            'total_fees': sum(fee.amount for fee in unpaid_fees),
            'total_fines': sum(fine.amount for fine in unpaid_fines),
            'grand_total': sum(fee.amount for fee in unpaid_fees) + sum(fine.amount for fine in unpaid_fines)
        }

class FineCalculator:
    """Fine calculation and application engine"""
    
    def apply_late_fee_fines(self, student=None):
        """Apply late fee fines for overdue payments"""
        from .models import StudentFee, AppliedFine
        from fines.models import FineTemplate
        
        # Get overdue fees
        overdue_fees = StudentFee.objects.filter(
            is_paid=False,
            due_date__lt=date.today()
        )
        
        if student:
            overdue_fees = overdue_fees.filter(student=student)
        
        applied_fines = []
        
        # Get late fee template
        late_fee_template = FineTemplate.objects.filter(
            fine_type__category='Late Fee'
        ).first()
        
        if not late_fee_template:
            return applied_fines
        
        for overdue_fee in overdue_fees:
            # Check if fine already applied for this fee
            existing_fine = AppliedFine.objects.filter(
                student=overdue_fee.student,
                fine_template=late_fee_template,
                reason__contains=f"Fee ID: {overdue_fee.id}"
            ).exists()
            
            if not existing_fine:
                fine_amount = self._calculate_fine_amount(overdue_fee, late_fee_template)
                
                applied_fine = AppliedFine.objects.create(
                    student=overdue_fee.student,
                    fine_template=late_fee_template,
                    amount=fine_amount,
                    reason=f"Late fee for {overdue_fee.fee_type.name} (Fee ID: {overdue_fee.id})",
                    due_date=date.today() + timedelta(days=7),
                    auto_generated=True
                )
                applied_fines.append(applied_fine)
        
        return applied_fines
    
    def _calculate_fine_amount(self, overdue_fee, fine_template):
        """Calculate fine amount based on template"""
        if fine_template.amount_type == 'Fixed':
            return fine_template.amount or Decimal('50')  # Default ₹50
        elif fine_template.amount_type == 'Percentage':
            percentage = fine_template.percentage or Decimal('5')  # Default 5%
            return (overdue_fee.amount * percentage) / 100
        else:
            return Decimal('50')  # Default amount