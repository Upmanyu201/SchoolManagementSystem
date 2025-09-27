from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
import json
from .services import LicenseService
from .models import DemoStatus

def demo_status(request):
    """Show demo status and license activation"""
    demo_status = LicenseService.get_demo_status()
    machine_id = LicenseService.get_machine_id()
    
    context = {
        'demo_status': demo_status,
        'machine_id': machine_id,
        'is_licensed': demo_status.is_licensed,
        'days_remaining': demo_status.days_remaining,
        'is_active': demo_status.is_active
    }
    
    return render(request, 'demo/status.html', context)

@csrf_protect
@require_POST
def activate_license(request):
    """Activate license key"""
    try:
        data = json.loads(request.body)
        license_key = data.get('license_key', '').strip()
        
        if not license_key:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a license key'
            })
        
        success, message = LicenseService.activate_license(
            license_key, 
            request.user if request.user.is_authenticated else None
        )
        
        return JsonResponse({
            'success': success,
            'message': message
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request format'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while activating the license'
        })

def demo_expired(request):
    """Demo expired page"""
    demo_status = LicenseService.get_demo_status()
    machine_id = LicenseService.get_machine_id()
    
    context = {
        'demo_status': demo_status,
        'machine_id': machine_id
    }
    
    return render(request, 'demo/expired.html', context)