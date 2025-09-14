from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.core.cache import cache
from django.db import transaction
from django.core.paginator import Paginator, Page
from django.db.models import Q
from .models import Student
from .forms import StudentForm
from .services import StudentService, StudentExportService
from users.decorators import module_required
from core.exports import ExportService
from core.security_utils import sanitize_input, log_security_event
from datetime import datetime
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@login_required
@module_required('students', 'view')
def student_list(request):
    try:
        # Get search and filter parameters
        search_query = request.GET.get('search', '').strip()
        class_filter = request.GET.get('class_filter')
        page_size = int(request.GET.get('page_size', 20))
        
        # Build queryset with optimized queries (use LEFT JOIN to include students without class)
        queryset = Student.objects.select_related('class_section').order_by('first_name', 'last_name')
        
        # Apply search filter with smart name matching
        if search_query:
            clean_query = sanitize_input(search_query)
            logger.info(f"Applying search filter: '{clean_query}'")
            
            # Smart search: handle "First Last" format
            search_parts = clean_query.strip().split()
            
            if len(search_parts) >= 2:
                # Multi-word search: try "First Last" combination
                first_part = search_parts[0]
                last_part = ' '.join(search_parts[1:])  # Handle "First Middle Last"
                
                queryset = queryset.filter(
                    # Exact name combination
                    (Q(first_name__icontains=first_part) & Q(last_name__icontains=last_part)) |
                    # Reverse combination
                    (Q(first_name__icontains=last_part) & Q(last_name__icontains=first_part)) |
                    # Single field matches
                    Q(first_name__icontains=clean_query) |
                    Q(last_name__icontains=clean_query) |
                    Q(admission_number__icontains=clean_query) |
                    Q(mobile_number__icontains=clean_query) |
                    Q(email__icontains=clean_query)
                )
            else:
                # Single word search
                queryset = queryset.filter(
                    Q(first_name__icontains=clean_query) |
                    Q(last_name__icontains=clean_query) |
                    Q(admission_number__icontains=clean_query) |
                    Q(mobile_number__icontains=clean_query) |
                    Q(email__icontains=clean_query)
                )
            
            logger.info(f"After search filter count: {queryset.count()}")
        
        # Apply class filter
        if class_filter:
            try:
                class_id = int(class_filter)
                logger.info(f"Applying class filter: class_section_id={class_id}")
                queryset = queryset.filter(class_section_id=class_id)
                logger.info(f"After class filter count: {queryset.count()}")
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid class filter value: {class_filter}, error: {e}")
                pass
        
        # Handle export requests
        export_format = request.GET.get('export')
        if export_format and export_format in ['excel', 'csv', 'pdf']:
            try:
                students_list = list(queryset)
                data, headers = StudentExportService.prepare_export_data(
                    students_list, 
                    include_financial=request.GET.get('include_financial') == '1'
                )
                filename = f"students_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                if export_format == 'excel':
                    return ExportService.export_to_xlsx(data, filename, headers)
                elif export_format == 'csv':
                    return ExportService.export_to_csv(data, filename, headers)
                elif export_format == 'pdf':
                    return ExportService.export_to_pdf(data, filename, headers, "Students Report")
            except Exception as e:
                logger.error(f"Export failed for user {sanitize_input(str(request.user.id))}: {sanitize_input(str(e))}")
                messages.error(request, "We couldn't export the data right now. Please try again.")
        
        # Debug: Log queryset info
        total_count = queryset.count()
        logger.info(f"Student queryset count: {total_count}")
        logger.info(f"Search query: '{search_query}', Class filter: '{class_filter}'")
        
        # Log the actual SQL query for debugging
        if total_count == 0 and (search_query or class_filter):
            basic_count = Student.objects.count()
            logger.warning(f"Filtered query returned 0, but basic query has {basic_count} students")
            logger.info(f"Queryset SQL: {queryset.query}")
            # DO NOT override queryset - respect the filters!
        
        # Ensure page_size is valid
        if page_size <= 0 or page_size > 100:
            page_size = 20
        
        # Pagination - Force creation
        paginator = Paginator(queryset, page_size)
        page_number = request.GET.get('page', 1)
        
        # Ensure page_number is valid
        try:
            page_number = int(page_number)
            if page_number < 1:
                page_number = 1
        except (ValueError, TypeError):
            page_number = 1
        
        # Create page object with error handling
        try:
            page_obj = paginator.get_page(page_number)
        except Exception as page_error:
            logger.error(f"Pagination error: {page_error}")
            # Force create page 1
            page_obj = paginator.get_page(1)
        
        # Debug: Log pagination info
        logger.info(f"Paginator count: {paginator.count}, Page obj count: {len(page_obj)}, Page number: {page_obj.number}")
        
        # Ensure page_obj is valid
        if not hasattr(page_obj, 'object_list'):
            logger.error("Invalid page_obj created")
            # Create emergency fallback
            from django.core.paginator import Page
            page_obj = paginator.get_page(1)
        
        # Get available classes for filter
        try:
            from subjects.models import ClassSection
            classes = ClassSection.objects.all().order_by('class_name', 'section_name')
        except ImportError:
            classes = []
        
        # Get dashboard stats with fallback
        try:
            stats = StudentService.get_dashboard_stats()
        except Exception as stats_error:
            logger.warning(f"Dashboard stats failed: {sanitize_input(str(stats_error))}")
            stats = {
                'total_students': paginator.count,
                'total_due_amount': 0,
                'class_distribution': [],
                'last_updated': timezone.now().isoformat()
            }
        
        # Ensure all context variables are properly set
        context = {
            'page_obj': page_obj,
            'search_query': search_query or '',
            'class_filter': class_filter or '',
            'page_size': page_size,
            'classes': classes or [],
            'stats': stats or {'total_students': 0},
            'total_students': paginator.count if paginator else 0,
            'paginator': paginator  # Add paginator to context
        }
        
        # Debug log final context
        logger.info(f"Final context - page_obj type: {type(page_obj)}, total_students: {context['total_students']}")
        return render(request, 'students/students_list.html', context)
        
    except Exception as e:
        logger.error(f"Error in student_list for user {sanitize_input(str(request.user.id))}: {sanitize_input(str(e))}")
        
        # Instead of showing error, create working context with basic data
        try:
            # Create minimal working context (ensure all students are included)
            queryset = Student.objects.all().order_by('first_name', 'last_name')
            paginator = Paginator(queryset, 20)
            page_obj = paginator.get_page(1)
            
            # Get classes safely
            try:
                from subjects.models import ClassSection
                classes = ClassSection.objects.all().order_by('class_name', 'section_name')
            except ImportError:
                classes = []
            
            context = {
                'page_obj': page_obj,
                'search_query': '',
                'class_filter': '',
                'page_size': 20,
                'classes': classes or [],
                'stats': {'total_students': paginator.count if paginator else 0},
                'total_students': paginator.count if paginator else 0,
                'paginator': paginator
            }
            
            messages.warning(request, "Some features may be limited. Student list loaded successfully.")
            return render(request, 'students/students_list.html', context)
            
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {sanitize_input(str(fallback_error))}")
            messages.error(request, "We're having trouble loading the student list. Please try again.")
            # Create empty page_obj for error case
            empty_paginator = Paginator(Student.objects.none(), 20)
            empty_page_obj = empty_paginator.get_page(1)
            return render(request, 'students/students_list.html', {
                'page_obj': empty_page_obj, 
                'stats': {},
                'total_students': 0,
                'search_query': '',
                'class_filter': '',
                'page_size': 20,
                'classes': [],
                'paginator': empty_paginator
            })

@login_required
@csrf_protect
@module_required('students', 'edit')
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Use optimized service for creation
                student = StudentService.create_student_optimized(
                    form.cleaned_data, 
                    request.user
                )
                
                # Try ML integration if available
                try:
                    from core.ml_integrations import ml_service
                    ml_insights = ml_service.predict_student_performance({
                        'admission_number': student.admission_number,
                        'class': student.class_section.class_name if student.class_section else 'N/A'
                    })
                    if ml_insights.get('risk_level') == 'high':
                        messages.warning(request, f"Note: AI analysis suggests {student.first_name} may need additional academic support.")
                except ImportError:
                    pass  # ML optional
                
                messages.success(request, f"Great! {student.first_name} {student.last_name} has been enrolled successfully with admission number {student.admission_number}.")
                return redirect('students:student_list')
                
            except ValidationError as e:
                messages.error(request, f"Validation error: {e.message if hasattr(e, 'message') else str(e)}")
            except Exception as e:
                logger.error(f"Error creating student by user {sanitize_input(str(request.user.id))}: {sanitize_input(str(e))}")
                messages.error(request, "We couldn't add the student right now. Please check all fields and try again.")
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = StudentForm()
    
    return render(request, 'students/add_student.html', {'form': form})

@login_required
@csrf_protect
@module_required('students', 'edit')
def edit_student(request, id):
    try:
        # Validate ID parameter
        student_id = int(id)
        if student_id <= 0:
            raise ValidationError("Invalid student ID")
        
        # Optimized query with select_related
        student = get_object_or_404(
            Student.objects.select_related('class_section'),
            id=student_id
        )
        
        if request.method == 'POST':
            form = StudentForm(request.POST, request.FILES, instance=student)
            
            if form.is_valid():
                try:
                    # Use optimized service for update
                    updated_student = StudentService.update_student_optimized(
                        student,
                        form.cleaned_data,
                        request.user
                    )
                    
                    messages.success(request, f"Perfect! {updated_student.first_name}'s details have been updated successfully.")
                    return redirect('students:student_list')
                    
                except Exception as e:
                    logger.error(f"Error updating student {sanitize_input(str(student_id))} by user {sanitize_input(str(request.user.id))}: {sanitize_input(str(e))}")
                    messages.error(request, "We couldn't update the student details. Please try again.")
            else:
                # Form validation errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
        else:
            form = StudentForm(instance=student)
        
        return render(request, 'students/add_student.html', {
            'form': form,
            'student': student
        })
        
    except (ValueError, ValidationError):
        messages.error(request, "Invalid student information. Please try again.")
        return redirect('students:student_list')
    except Exception as e:
        logger.error(f"Error in edit_student for ID {sanitize_input(str(id))} by user {sanitize_input(str(request.user.id))}: {sanitize_input(str(e))}")
        messages.error(request, "We couldn't load the student details. Please try again.")
        return redirect('students:student_list')

@login_required
@require_POST
@csrf_protect
@module_required('students', 'edit')
def delete_student(request, id):
    try:
        # Validate ID parameter
        student_id = int(id)
        if student_id <= 0:
            raise ValidationError("Invalid student ID")
        
        student = get_object_or_404(Student, id=student_id)
        student_name = sanitize_input(f"{student.first_name} {student.last_name}")
        
        # Use optimized service for safe deletion
        deletion_successful = StudentService.delete_student_safe(student, request.user)
        
        if deletion_successful:
            messages.success(request, f'Perfect! {student_name} has been removed successfully.')
        else:
            messages.warning(request, f"Cannot delete {student_name} - student has related records (fees, attendance). Please contact administrator.")
        
    except (ValueError, ValidationError):
        messages.error(request, "Invalid student information. Please try again.")
    except Exception as e:
        logger.error(f"Error deleting student {sanitize_input(str(id))} by user {sanitize_input(str(request.user.id))}: {sanitize_input(str(e))}")
        messages.error(request, "We couldn't remove the student right now. Please try again.")
    
    return redirect('students:student_list')

@login_required
def debug_pagination(request):
    """Debug endpoint to check pagination"""
    try:
        queryset = Student.objects.all().order_by('first_name', 'last_name')
        paginator = Paginator(queryset, 20)
        page_obj = paginator.get_page(1)
        
        return JsonResponse({
            'total_students': queryset.count(),
            'paginator_count': paginator.count,
            'page_obj_count': len(page_obj),
            'page_number': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'first_student': page_obj[0].first_name if page_obj else 'None'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})

@login_required
@module_required('students', 'view')
def debug_transport(request, admission_number):
    try:
        # Validate admission number
        if not admission_number or len(admission_number) > 20:
            return JsonResponse({'error': 'Invalid admission number'}, status=400)
        
        # Sanitize admission number
        clean_admission = sanitize_input(admission_number.strip())
        
        # Log debug access
        log_security_event(
            request.user,
            'debug_transport_access',
            f'Debug transport accessed for admission {clean_admission}'
        )
        
        return JsonResponse({
            'status': 'debug',
            'admission_number': clean_admission,
            'user': sanitize_input(request.user.username)
        })
    except Exception as e:
        logger.error(f"Debug transport error for {sanitize_input(str(admission_number))} by user {sanitize_input(str(request.user.id))}: {sanitize_input(str(e))}")
        return JsonResponse({'error': 'Debug information unavailable'}, status=500)

# Simple test endpoints
@login_required
def simple_test(request):
    """Simple test to verify basic functionality"""
    try:
        count = Student.objects.count()
        first_student = Student.objects.first()
        return JsonResponse({
            'status': 'success',
            'total_students': count,
            'first_student': f"{first_student.first_name} {first_student.last_name}" if first_student else 'None',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})

@login_required
def coordination_test(request):
    """Test frontend-backend coordination"""
    try:
        queryset = Student.objects.all().order_by('first_name', 'last_name')[:5]
        students_data = [{
            'id': s.id,
            'name': f"{s.first_name} {s.last_name}",
            'admission_number': s.admission_number
        } for s in queryset]
        
        return render(request, 'students/coordination_test.html', {
            'students': students_data,
            'total_count': Student.objects.count()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})

@login_required
def coordination_api(request):
    """API endpoint for coordination test"""
    try:
        queryset = Student.objects.all().order_by('first_name', 'last_name')[:10]
        students_data = [{
            'id': s.id,
            'name': f"{s.first_name} {s.last_name}",
            'admission_number': s.admission_number,
            'class': s.class_section.class_name if s.class_section else 'N/A'
        } for s in queryset]
        
        return JsonResponse({
            'status': 'success',
            'students': students_data,
            'total_count': Student.objects.count()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})