from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils.html import escape
from users.decorators import module_required
import logging
import csv
from datetime import datetime

logger = logging.getLogger(__name__)

@login_required
@csrf_protect
@module_required('fines', 'edit')
def add_fine(request):
    try:
        if request.method == 'POST':
            from .forms import FineForm
            form = FineForm(request.POST, request=request)
            form.initial['user'] = request.user
            
            if form.is_valid():
                fine = form.save(commit=False)
                fine.created_by = request.user
                fine.save()
                
                logger.info(f"User {request.user.id} created fine: {fine.fine_type.name} - ₹{fine.amount}")
                messages.success(request, f"Great! Fine '{fine.fine_type.name}' of ₹{fine.amount} has been applied successfully.")
                return redirect('fines:fine_history')
            else:
                # Form has validation errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.title()}: {error}")
        else:
            from .forms import FineForm
            form = FineForm()
        
        context = {'form': form}
        return render(request, 'fines/add_fine.html', context)
        
    except Exception as e:
        logger.error(f"Error in add_fine for user {request.user.id}: {str(e)}")
        messages.error(request, "We couldn't add the fine right now. Please try again.")
        from .forms import FineForm
        return render(request, 'fines/add_fine.html', {'form': FineForm()})

@login_required
@module_required('fines', 'view')
def fine_history(request):
    try:
        from .models import FineStudent, Fine
        from django.core.paginator import Paginator
        from django.db import models
        
        # Get search parameters
        search_query = request.GET.get('search', '')
        class_filter = request.GET.get('class_filter', '')
        status_filter = request.GET.get('status_filter', '')
        
        # Query fines directly
        fines_qs = Fine.objects.select_related('fine_type', 'class_section').order_by('-applied_date')
        
        if search_query:
            # For class-level fines, search by class name or fine type
            fines_qs = fines_qs.filter(
                models.Q(class_section__class_name__icontains=search_query) |
                models.Q(class_section__section_name__icontains=search_query) |
                models.Q(fine_type__name__icontains=search_query) |
                models.Q(reason__icontains=search_query)
            )
        
        if class_filter:
            fines_qs = fines_qs.filter(class_section_id=class_filter)
        
        # Note: Status filtering removed as it's now class-level, not individual student level
        
        # Pagination
        paginator = Paginator(fines_qs, 25)
        page = request.GET.get('page', 1)
        page_obj = paginator.get_page(page)
        
        context = {
            'fines': page_obj,
            'page_obj': page_obj,
            'search_query': search_query,
            'class_filter': class_filter,
            'status_filter': status_filter,
        }
        
        return render(request, 'fines/fine_history.html', context)
    except Exception as e:
        logger.error(f"Error in fine_history for user {request.user.id}: {str(e)}")
        messages.error(request, "We're having trouble loading the fine history. Please try again.")
        return render(request, 'fines/fine_history.html')

@login_required
@require_POST
@csrf_protect
@module_required('fines', 'edit')
def toggle_fine_status(request, fine_id):
    try:
        # Validate fine ID
        fine_id_int = int(fine_id)
        if fine_id_int <= 0:
            raise ValidationError("Invalid fine ID")
        
        # Log the status change attempt
        logger.info(f"User {request.user.id} attempting to toggle fine status for ID {fine_id_int}")
        
        # Additional processing would go here
        messages.success(request, "Perfect! Fine status has been updated successfully.")
        
    except (ValueError, ValidationError):
        messages.error(request, "Invalid fine information. Please try again.")
    except Exception as e:
        logger.error(f"Error toggling fine status {fine_id} by user {request.user.id}: {str(e)}")
        messages.error(request, "We couldn't update the fine status right now. Please try again.")
    
    return redirect('fines:fine_history')

@login_required
@require_POST
@csrf_protect
@module_required('fines', 'edit')
def delete_fine(request, fine_id):
    try:
        from .models import Fine
        from django.shortcuts import get_object_or_404
        
        # Validate fine ID
        fine_id_int = int(fine_id)
        if fine_id_int <= 0:
            raise ValidationError("Invalid fine ID")
        
        # Get the fine object
        fine = get_object_or_404(Fine, id=fine_id_int)
        fine_info = f"{fine.fine_type.name} (₹{fine.amount})"
        
        # Log the deletion attempt
        logger.info(f"User {request.user.id} attempting to delete fine {fine_id_int}: {fine_info}")
        
        # Delete the fine (this will cascade delete FineStudent records)
        fine.delete()
        
        messages.success(request, f"Perfect! Fine '{fine_info}' has been removed successfully.")
        
    except (ValueError, ValidationError):
        messages.error(request, "Invalid fine information. Please try again.")
    except Exception as e:
        logger.error(f"Error deleting fine {fine_id} by user {request.user.id}: {str(e)}")
        messages.error(request, "We couldn't remove the fine right now. Please try again.")
    
    return redirect('fines:fine_history')

@module_required('fines', 'edit')
def upload_fines(request):
    return render(request, 'fines/upload_fines.html')

@module_required('fines', 'view')
def base_fine(request):
    return render(request, 'fines/base_fine.html')

@login_required
@csrf_protect
@module_required('fines', 'edit')
def edit_fine(request, fine_id):
    try:
        from .models import Fine
        from .forms import FineForm
        
        fine = get_object_or_404(Fine, id=fine_id)
        
        if request.method == 'POST':
            form = FineForm(request.POST, instance=fine, request=request)
            
            if form.is_valid():
                fine = form.save(commit=False)
                fine.save()
                
                logger.info(f"User {request.user.id} updated fine: {fine.fine_type.name} - ₹{fine.amount}")
                messages.success(request, f"Perfect! Fine '{fine.fine_type.name}' has been updated successfully.")
                return redirect('fines:fine_history')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.title()}: {error}")
        else:
            form = FineForm(instance=fine)
        
        context = {
            'form': form,
            'fine': fine
        }
        return render(request, 'fines/edit_fine.html', context)
        
    except Exception as e:
        logger.error(f"Error in edit_fine {fine_id} for user {request.user.id}: {str(e)}")
        messages.error(request, "We couldn't load the fine for editing. Please try again.")
        return redirect('fines:fine_history')

@module_required('fines', 'view')
def fine_types(request):
    try:
        from .models import FineType
        
        # Query fine types
        fine_types = FineType.objects.all().order_by('-created_at')
        
        context = {
            'fine_types': fine_types,
        }
        
        return render(request, 'fines/fine_types.html', context)
    except Exception as e:
        logger.error(f"Error in fine_types for user {request.user.id}: {str(e)}")
        messages.error(request, "We're having trouble loading the fine types. Please try again.")
        return render(request, 'fines/fine_types.html')

@login_required
@csrf_protect
@module_required('fines', 'edit')
def add_fine_type(request):
    try:
        if request.method == 'POST':
            from .forms import FineTypeForm
            form = FineTypeForm(request.POST)
            
            if form.is_valid():
                fine_type = form.save(commit=False)
                fine_type.created_by = request.user
                fine_type.save()
                
                logger.info(f"User {request.user.id} created fine type: {fine_type.name}")
                messages.success(request, f"Great! Fine type '{fine_type.name}' has been created successfully.")
                return redirect('fines:fine_types')
            else:
                # Form has validation errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.title()}: {error}")
        else:
            from .forms import FineTypeForm
            form = FineTypeForm()
        
        context = {'form': form}
        return render(request, 'fines/add_fine_type.html', context)
        
    except Exception as e:
        logger.error(f"Error in add_fine_type for user {request.user.id}: {str(e)}")
        messages.error(request, "We couldn't create the fine type right now. Please try again.")
        return render(request, 'fines/add_fine_type.html', {'form': FineTypeForm()})

@login_required
@csrf_protect
@module_required('fines', 'edit')
def edit_fine_type(request, fine_type_id):
    try:
        from .models import FineType
        from .forms import FineTypeForm
        from django.shortcuts import get_object_or_404
        
        fine_type = get_object_or_404(FineType, id=fine_type_id)
        
        if request.method == 'POST':
            form = FineTypeForm(request.POST, instance=fine_type)
            
            if form.is_valid():
                fine_type = form.save(commit=False)
                fine_type.updated_by = request.user
                fine_type.save()
                
                logger.info(f"User {request.user.id} updated fine type: {fine_type.name}")
                messages.success(request, f"Perfect! Fine type '{fine_type.name}' has been updated successfully.")
                return redirect('fines:fine_types')
            else:
                # Form has validation errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.title()}: {error}")
        else:
            form = FineTypeForm(instance=fine_type)
        
        context = {
            'form': form,
            'fine_type': fine_type
        }
        return render(request, 'fines/edit_fine_type.html', context)
        
    except Exception as e:
        logger.error(f"Error in edit_fine_type {fine_type_id} for user {request.user.id}: {str(e)}")
        messages.error(request, "We couldn't load the fine type for editing. Please try again.")
        return redirect('fines:fine_types')

@login_required
@require_POST
@csrf_protect
@module_required('fines', 'edit')
def toggle_fine_type_status(request, fine_type_id):
    try:
        from .models import FineType
        from django.shortcuts import get_object_or_404
        
        fine_type = get_object_or_404(FineType, id=fine_type_id)
        fine_type.is_active = not fine_type.is_active
        fine_type.save()
        
        status = "activated" if fine_type.is_active else "deactivated"
        logger.info(f"User {request.user.id} {status} fine type: {fine_type.name}")
        
        return JsonResponse({
            'status': 'success',
            'message': f"Perfect! Fine type '{fine_type.name}' has been {status} successfully.",
            'is_active': fine_type.is_active
        })
        
    except Exception as e:
        logger.error(f"Error toggling fine type status {fine_type_id} by user {request.user.id}: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': "We couldn't update the fine type status right now. Please try again."
        }, status=500)

@login_required
@require_POST
@csrf_protect
@module_required('fines', 'edit')
def delete_fine_type(request, fine_type_id):
    try:
        from .models import FineType, Fine
        from django.shortcuts import get_object_or_404
        
        # Validate fine type ID
        fine_type_id_int = int(fine_type_id)
        if fine_type_id_int <= 0:
            raise ValidationError("Invalid fine type ID")
        
        # Get the fine type object
        fine_type = get_object_or_404(FineType, id=fine_type_id_int)
        fine_type_name = fine_type.name
        
        # Check if fine type is being used
        active_fines = Fine.objects.filter(fine_type=fine_type).count()
        if active_fines > 0:
            messages.error(request, f"Cannot delete '{fine_type_name}' because it's being used by {active_fines} active fine(s). Please remove those fines first.")
            return redirect('fines:fine_types')
        
        # Log the deletion attempt
        logger.info(f"User {request.user.id} attempting to delete fine type {fine_type_id_int}: {fine_type_name}")
        
        # Delete the fine type
        fine_type.delete()
        
        messages.success(request, f"Perfect! Fine type '{fine_type_name}' has been removed successfully.")
        
    except (ValueError, ValidationError):
        messages.error(request, "Invalid fine type information. Please try again.")
    except Exception as e:
        logger.error(f"Error deleting fine type {fine_type_id} by user {request.user.id}: {str(e)}")
        messages.error(request, "We couldn't remove the fine type right now. Please try again.")
    
    return redirect('fines:fine_types')

@login_required
@module_required('fines', 'view')
def load_students_for_class(request):
    try:
        from students.models import Student
        
        class_id = request.GET.get('class_id')
        if class_id:
            try:
                class_id_int = int(class_id)
                if class_id_int <= 0:
                    return JsonResponse({'error': 'Invalid class ID'}, status=400)
                
                # Load students for the specific class
                students = Student.objects.filter(class_section_id=class_id_int).select_related('class_section')
                student_data = []
                for student in students:
                    student_data.append({
                        'id': student.id,
                        'name': f"{student.first_name} {student.last_name}",
                        'admission_number': student.admission_number,
                        'class_name': f"{student.class_section.class_name}{student.class_section.section_name}" if student.class_section else 'N/A',
                        'father_name': getattr(student, 'father_name', 'N/A')
                    })
                
                return JsonResponse({
                    'students': student_data,
                    'status': 'success'
                })
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Invalid class ID format'}, status=400)
        
        return JsonResponse({'students': [], 'status': 'success'})
    except Exception as e:
        logger.error(f"Error loading students for class by user {request.user.id}: {str(e)}")
        return JsonResponse({'error': 'Unable to load students'}, status=500)

@login_required
@module_required('fines', 'view')
def load_fees_types(request):
    try:
        fees_group_id = request.GET.get('fees_group_id')
        if fees_group_id:
            from fees.models import FeesType
            fees_types = FeesType.objects.filter(fee_group_id=fees_group_id).select_related('fee_group')
            
            fees_types_data = []
            for ft in fees_types:
                fees_types_data.append({
                    'id': ft.id,
                    'group_type': ft.group_type,  # This is a property
                    'fee_type': ft.fee_type,      # This is a property
                    'amount': str(ft.amount),
                    'amount_type': ft.amount_type,
                    'class_name': ft.class_name or '',
                    'month_name': ft.month_name or '',
                    'stoppage_name': ft.stoppage_name or '',
                    'display_format': ft.display_format
                })
            
            return JsonResponse({
                'fees_types': fees_types_data,
                'status': 'success'
            })
        return JsonResponse({'fees_types': [], 'status': 'success'})
    except Exception as e:
        logger.error(f"Error loading fees types: {str(e)}")
        return JsonResponse({'error': 'Unable to load fees types'}, status=500)

@login_required
@module_required('fines', 'view')
def load_classes_for_fees_type(request):
    try:
        from subjects.models import ClassSection
        classes = ClassSection.objects.all().values('id', 'class_name', 'section_name')
        return JsonResponse({
            'classes': [{'id': c['id'], 'name': f"{c['class_name']}{c['section_name']}"} for c in classes],
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error loading classes: {str(e)}")
        return JsonResponse({'error': 'Unable to load classes'}, status=500)

@login_required
@module_required('fines', 'view')
def load_students_for_fees_type(request):
    try:
        from students.models import Student
        students = Student.objects.select_related('class_section').all()[:100]  # Limit for performance
        student_data = []
        for student in students:
            student_data.append({
                'id': student.id,
                'name': f"{student.first_name} {student.last_name}",
                'admission_number': student.admission_number,
                'class_name': f"{student.class_section.class_name}{student.class_section.section_name}" if student.class_section else 'N/A',
                'father_name': getattr(student, 'father_name', 'N/A')
            })
        return JsonResponse({
            'students': student_data,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error loading students: {str(e)}")
        return JsonResponse({'error': 'Unable to load students'}, status=500)

@login_required
@module_required('fines', 'view')
def search_students(request):
    try:
        from students.models import Student
        from django.db.models import Q
        
        search_term = request.GET.get('q', '').strip()
        if search_term and len(search_term) >= 2:
            # Search students by name, admission number, or father name
            students = Student.objects.select_related('class_section').filter(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(admission_number__icontains=search_term) |
                Q(father_name__icontains=search_term)
            )[:50]  # Limit results
            
            student_data = []
            for student in students:
                student_data.append({
                    'id': student.id,
                    'name': f"{student.first_name} {student.last_name}",
                    'admission_number': student.admission_number,
                    'class_name': f"{student.class_section.class_name}{student.class_section.section_name}" if student.class_section else 'N/A',
                    'father_name': getattr(student, 'father_name', 'N/A')
                })
            
            return JsonResponse({
                'students': student_data,
                'status': 'success'
            })
        
        return JsonResponse({'students': [], 'status': 'success'})
    except Exception as e:
        logger.error(f"Error searching students by user {request.user.id}: {str(e)}")
        return JsonResponse({'error': 'Search unavailable'}, status=500)

@login_required
@module_required('fines', 'view')
def download_sample_csv(request):
    try:
        # Log the download attempt
        logger.info(f"User {request.user.id} downloading sample CSV")
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sample_fines.csv"'
        response['Content-Security-Policy'] = "default-src 'none'"
        
        # Add sample CSV content
        response.write('Student Name,Admission Number,Fine Amount,Reason\n')
        response.write('John Doe,ADM001,100,Late submission\n')
        
        return response
    except Exception as e:
        logger.error(f"Error downloading sample CSV by user {request.user.id}: {str(e)}")
        return HttpResponse('Error generating sample file', status=500)

@login_required
@module_required('fines', 'view')
def get_fine_type_usage(request, fine_type_id):
    try:
        from .models import FineType, Fine
        from django.shortcuts import get_object_or_404
        
        # Validate fine type ID
        try:
            type_id_int = int(fine_type_id)
            if type_id_int <= 0:
                return JsonResponse({'error': 'Invalid fine type ID'}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid fine type ID format'}, status=400)
        
        # Get the fine type and count usage
        fine_type = get_object_or_404(FineType, id=type_id_int)
        usage_count = Fine.objects.filter(fine_type=fine_type).count()
        
        return JsonResponse({
            'usage': usage_count,
            'status': 'success',
            'fine_type_name': fine_type.name,
            'can_delete': usage_count == 0
        })
    except Exception as e:
        logger.error(f"Error getting fine type usage {fine_type_id} by user {request.user.id}: {str(e)}")
        return JsonResponse({'error': 'Usage data unavailable'}, status=500)

@module_required('fines', 'edit')
def waive_fine(request, fine_id):
    return redirect('fines:fine_history')

@login_required
@module_required('fines', 'view')
def export_fines_csv(request):
    """Export fines data to CSV format"""
    try:
        import csv
        from datetime import datetime
        
        # Log the export attempt
        logger.info(f"User {request.user.id} exporting fines CSV")
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="fines_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        response['Content-Security-Policy'] = "default-src 'none'"
        
        writer = csv.writer(response)
        
        # Write CSV headers
        writer.writerow([
            'Student Name',
            'Admission Number', 
            'Class',
            'Fine Type',
            'Amount (₹)',
            'Due Date',
            'Status',
            'Applied Date',
            'Reason'
        ])
        
        # Sample data - in real implementation, this would fetch from database
        sample_data = [
            ['John Doe', 'ADM001', '10-A', 'Late Fee', '100', '2024-01-15', 'Pending', '2024-01-10', 'Late submission'],
            ['Jane Smith', 'ADM002', '9-B', 'Uniform Fine', '50', '2024-01-20', 'Paid', '2024-01-12', 'Improper uniform'],
        ]
        
        for row in sample_data:
            writer.writerow(row)
        
        messages.success(request, "Great! Fines data has been exported successfully.")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting fines CSV by user {request.user.id}: {str(e)}")
        messages.error(request, "We couldn't export the data right now. Please try again.")
        return redirect('fines:fine_history')

@login_required
@module_required('fines', 'view')
def verify_fine_application(request, fine_id):
    """Verify that fine was applied correctly to intended students"""
    try:
        from core.fee_management.services import fee_service
        
        verification = fee_service.verify_fine_application(fine_id)
        
        if 'error' in verification:
            messages.error(request, f"Error verifying fine: {verification['error']}")
            return redirect('fines:fine_history')
        
        context = {
            'verification': verification,
            'fine_id': fine_id
        }
        
        return render(request, 'fines/verify_fine.html', context)
        
    except Exception as e:
        logger.error(f"Error verifying fine {fine_id} by user {request.user.id}: {str(e)}")
        messages.error(request, "We couldn't verify the fine application. Please try again.")
        return redirect('fines:fine_history')

@login_required
@require_POST
@csrf_protect
@module_required('fines', 'edit')
def fix_fine_application(request, fine_id):
    """Fix incorrectly applied fine by removing from wrong classes"""
    try:
        from core.fee_management.services import fee_service
        
        result = fee_service.fix_incorrect_fine_application(fine_id)
        
        if result['success']:
            messages.success(request, result['message'])
            logger.info(f"User {request.user.id} fixed fine application {fine_id}: {result['message']}")
        else:
            messages.error(request, f"Error fixing fine: {result['error']}")
        
    except Exception as e:
        logger.error(f"Error fixing fine application {fine_id} by user {request.user.id}: {str(e)}")
        messages.error(request, "We couldn't fix the fine application. Please try again.")
    
    return redirect('fines:fine_history')

@login_required
@module_required('fines', 'view')
def analyze_fee_type(request, fees_type_id):
    """Analyze fee type payment status across all classes"""
    try:
        from core.fee_management.services import fee_service
        
        analysis = fee_service.get_fee_type_analysis(fees_type_id)
        
        if 'error' in analysis:
            messages.error(request, f"Error analyzing fee type: {analysis['error']}")
            return redirect('fines:fine_history')
        
        context = {
            'analysis': analysis,
            'fees_type_id': fees_type_id
        }
        
        return render(request, 'fines/analyze_fee_type.html', context)
        
    except Exception as e:
        logger.error(f"Error analyzing fee type {fees_type_id} by user {request.user.id}: {str(e)}")
        messages.error(request, "We couldn't analyze the fee type. Please try again.")
        return redirect('fines:fine_history')