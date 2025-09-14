from django import forms
from .models import Fine, FineType, FineStudent, FineAuditLog, FineTemplate
from students.models import Student
from subjects.models import ClassSection
from fees.models import FeesGroup, FeesType
from django.core.exceptions import ValidationError
from django.contrib import messages
import logging

logger = logging.getLogger("myapp")

class FineForm(forms.ModelForm):
    target_scope = forms.ChoiceField(choices=[('Individual', 'Individual'), ('Class', 'Class'), ('All', 'All Students')])
    class_section = forms.ModelChoiceField(
        queryset=ClassSection.objects.all(), 
        required=False, 
        label="Select Class Section",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-placeholder': 'Choose a class to apply fine...'
        })
    )
    fine_template = forms.ModelChoiceField(
        queryset=FineTemplate.objects.all(),
        required=False,
        label="Select Fine Template",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fees_group = forms.ModelChoiceField(
        queryset=FeesGroup.objects.all(),
        required=False,
        label="Fees Group",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fees_type = forms.ModelChoiceField(
        queryset=FeesType.objects.all(),
        required=False,
        label="Fees Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Fine
        fields = ['fine_template', 'fine_type', 'fees_type', 'amount', 'dynamic_amount_percent', 'reason', 'due_date', 'target_scope', 'class_section']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Fixed Amount'}),
            'dynamic_amount_percent': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'e.g., 5%'}),
            'reason': forms.Textarea(attrs={'rows': 3}),

        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Set field requirements based on target_scope
        if 'target_scope' in self.data:
            target_scope = self.data.get('target_scope')
            self.fields['class_section'].required = (target_scope == 'Class')
            logger.info(f"Form init - target_scope: {target_scope}, class_section required: {self.fields['class_section'].required}")
        else:
            # Default: class_section not required
            self.fields['class_section'].required = False
            
        # Set querysets for related fields
        try:
            self.fields['fine_type'].queryset = FineType.objects.filter(is_active=True).order_by('name')
            self.fields['fine_type'].empty_label = "Select Fine Type"
        except:
            self.fields['fine_type'].queryset = FineType.objects.all().order_by('name')
            self.fields['fine_type'].empty_label = "Select Fine Type"
        
        try:
            self.fields['fees_group'].queryset = FeesGroup.objects.all().order_by('fee_group')
            self.fields['fees_group'].empty_label = "Select Fees Group"
        except:
            self.fields['fees_group'].queryset = FeesGroup.objects.none()
            self.fields['fees_group'].empty_label = "No Fees Groups Available"
        
        try:
            self.fields['fees_type'].queryset = FeesType.objects.select_related('fee_group').order_by('fee_group__group_type', 'amount_type')
            self.fields['fees_type'].empty_label = "Select Fees Group first"
        except:
            self.fields['fees_type'].queryset = FeesType.objects.none()
            self.fields['fees_type'].empty_label = "No Fees Types Available"
        
        # Add CSS classes for better styling
        self.fields['class_section'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-400 focus:ring-0 transition-all duration-300',
            'data-placeholder': 'Choose a class section...'
        })
        self.fields['target_scope'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['fine_type'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-400 focus:ring-0 transition-all duration-300'
        })
        self.fields['fees_group'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-400 focus:ring-0 transition-all duration-300'
        })
        self.fields['fees_type'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-400 focus:ring-0 transition-all duration-300'
        })

    def clean(self):
        cleaned_data = super().clean()
        target_scope = cleaned_data.get('target_scope')
        amount = cleaned_data.get('amount')
        dynamic_amount_percent = cleaned_data.get('dynamic_amount_percent')
        fine_template = cleaned_data.get('fine_template')
        fees_type = cleaned_data.get('fees_type')
        class_section = cleaned_data.get('class_section')

        logger.info(f"Form validation - Target Scope: {target_scope}, Amount: {amount}, Dynamic Amount: {dynamic_amount_percent}, Class Section: {class_section}")

        if fine_template:
            cleaned_data['fine_type'] = fine_template.fine_type
            cleaned_data['amount'] = cleaned_data['amount'] or fine_template.amount
            cleaned_data['dynamic_amount_percent'] = cleaned_data['dynamic_amount_percent'] or fine_template.dynamic_amount_percent
            cleaned_data['reason'] = cleaned_data['reason'] or fine_template.reason
            cleaned_data['fees_type'] = cleaned_data['fees_type'] or fine_template.fees_type

        # Validate dynamic amount calculation
        if dynamic_amount_percent and not fees_type:
            logger.error("Validation error: Fees Type is required for dynamic amount calculation")
            raise ValidationError("Fees Type is required for dynamic amount calculation.")
        if dynamic_amount_percent and fees_type and not fees_type.amount:
            logger.error("Validation error: Selected Fees Type has no amount defined for dynamic calculation")
            raise ValidationError("Selected Fees Type has no amount defined for dynamic calculation.")
        if not amount and not (dynamic_amount_percent and fees_type):
            logger.error("Validation error: Amount is required unless dynamic amount is specified with a fees type")
            raise ValidationError("Amount is required unless dynamic amount is specified with a fees type.")
        
        # Validate class section for Class scope
        if target_scope == 'Class':
            if not class_section:
                logger.error("Validation error: Class Section is required for Class scope")
                raise ValidationError({"class_section": "Class Section is required for Class scope."})
            
            # Check if students exist in the class section
            if not Student.objects.filter(class_section=class_section).exists():
                logger.warning(f"No students found in class section {class_section.display_name} - fine will be created but no students assigned")
                if hasattr(self, 'request') and self.request:
                    from django.contrib import messages
                    messages.warning(self.request, f"Warning: No students found in class section {class_section.display_name}. Fine will be created but no students will be assigned.")

        logger.info("Form validation passed successfully")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        target_scope = self.cleaned_data['target_scope']
        user = self.initial.get('user', None)
        
        logger.info(f"Form save method - target_scope: {target_scope}, user: {user}")
        
        instance.target_scope = target_scope
        if user:
            instance.created_by = user

        if commit:
            instance.save()
            
            # Use centralized service for proper fine application
            if target_scope == 'Class' and instance.class_section:
                from core.fee_management.services import fee_service
                
                fine_data = {
                    'class_section_id': instance.class_section.id,
                    'fine_type_id': instance.fine_type.id,
                    'fees_type_id': instance.fees_type.id if instance.fees_type else None,
                    'amount': instance.amount,
                    'reason': instance.reason,
                    'due_date': instance.due_date,
                    'created_by': user
                }
                
                # Apply fine using centralized service (this will create FineStudent records)
                result = fee_service.apply_class_fine(fine_data)
                
                if not result['success']:
                    logger.error(f"Failed to apply class fine: {result.get('error')}")
                else:
                    logger.info(f"Successfully applied fine to {result['students_affected']} students in {result['class_name']}")
            
            logger.info(f"Form save method - successfully saved fine ID: {instance.id}")
        else:
            logger.info("Form save method - commit=False, not saving to DB yet")

        return instance

class FineTypeForm(forms.ModelForm):
    class Meta:
        model = FineType
        fields = ['name', 'category', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-400 focus:ring-0 transition-all duration-300',
                'placeholder': 'e.g., Late Fee, Library Fine'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-400 focus:ring-0 transition-all duration-300'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-400 focus:ring-0 transition-all duration-300',
                'rows': 4,
                'placeholder': 'Describe when this fine type should be applied...'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError("Fine type name is required.")
        if len(name) < 3:
            raise ValidationError("Fine type name must be at least 3 characters long.")
        if len(name) > 100:
            raise ValidationError("Fine type name cannot exceed 100 characters.")
        
        # Check for duplicate names (case-insensitive)
        if FineType.objects.filter(name__iexact=name).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError("A fine type with this name already exists.")
        
        return name

# Waiver functionality removed - use student_fees discount system instead

class FineVerificationForm(forms.Form):
    """Form to verify and fix fine applications"""
    fine_id = forms.IntegerField(widget=forms.HiddenInput())
    
    def clean_fine_id(self):
        fine_id = self.cleaned_data.get('fine_id')
        if fine_id:
            try:
                Fine.objects.get(id=fine_id)
            except Fine.DoesNotExist:
                raise ValidationError("Fine not found.")
        return fine_id
    
    def verify_fine(self):
        """Verify fine application using centralized service"""
        from core.fee_management.services import fee_service
        
        fine_id = self.cleaned_data['fine_id']
        return fee_service.verify_fine_application(fine_id)
    
    def fix_fine(self):
        """Fix incorrect fine application"""
        from core.fee_management.services import fee_service
        
        fine_id = self.cleaned_data['fine_id']
        return fee_service.fix_incorrect_fine_application(fine_id)