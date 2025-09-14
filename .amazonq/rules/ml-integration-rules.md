# 🤖 ML Integration Rules (2025 - All 17 Modules)

## Core Principle
Use centralized ML service from `core.ml_integrations` with 26 trained models across all modules.

## Import Pattern
```python
# Updated ML import pattern
try:
    from core.ml_integrations import ml_service
    ML_AVAILABLE = True
except ImportError:
    ml_service = None
    ML_AVAILABLE = False

# Global ML status for templates
from django.conf import settings
if not hasattr(settings, 'ML_AVAILABLE'):
    settings.ML_AVAILABLE = ML_AVAILABLE

# Usage check
if ML_AVAILABLE:
    insights = ml_service.generate_performance_insights()
else:
    insights = {'error': 'ML models not available'}
```

## Required ML Integration Points (All 17 Modules)

### 1. Students Module (`students/views.py`)
```python
# Student performance and dropout risk
if ML_AVAILABLE:
    performance_risk = ml_service.predict_student_performance(student.id)
    dropout_risk = ml_service.predict_dropout_risk(student.id)
    recommendations = ml_service.get_student_recommendations(student.id)
```

### 2. Teachers Module (`teachers/views.py`)
```python
# Teacher performance and workload
if ML_AVAILABLE:
    teacher_performance = ml_service.analyze_teacher_performance(teacher.id)
    workload_optimization = ml_service.optimize_teacher_workload(teacher.id)
```

### 3. Fees Module (`fees/views.py`)
```python
# Fee structure optimization
if ML_AVAILABLE:
    fee_optimization = ml_service.optimize_fee_structure()
    collection_insights = ml_service.analyze_fee_collection_patterns()
```

### 4. Student Fees (`student_fees/views.py`)
```python
# Payment predictions and risk analysis
if ML_AVAILABLE:
    payment_risk = ml_service.predict_payment_delay(student.id)
    optimal_timing = ml_service.get_optimal_payment_timing(student.id)
```

### 5. Attendance Module (`attendance/views.py`)
```python
# Attendance patterns and predictions
if ML_AVAILABLE:
    attendance_patterns = ml_service.analyze_attendance_patterns(student.id)
    absence_prediction = ml_service.predict_student_absence(student.id)
```

### 6. Transport Module (`transport/views.py`)
```python
# Route optimization and delay prediction
if ML_AVAILABLE:
    route_optimization = ml_service.optimize_transport_routes()
    delay_prediction = ml_service.predict_transport_delays(route_id)
```

### 7. Messaging Module (`messaging/views.py`)
```python
# Message timing and priority optimization
if ML_AVAILABLE:
    optimal_timing = ml_service.optimize_message_timing()
    message_priority = ml_service.classify_message_priority(message_content)
```

### 8. Dashboard (`dashboard/views.py`)
```python
# Comprehensive school insights
if ML_AVAILABLE:
    school_insights = ml_service.generate_school_performance_insights()
    financial_forecasts = ml_service.forecast_revenue(months=6)
    risk_alerts = ml_service.get_high_risk_students()
```

## ML Functions Available (26 Models)

### Student Analytics (2 models)
- `predict_student_performance(student_id)` - Performance risk prediction
- `predict_dropout_risk(student_id)` - Dropout risk assessment
- `get_student_recommendations(student_id)` - Personalized interventions

### Teacher Analytics (2 models)
- `analyze_teacher_performance(teacher_id)` - Performance clustering
- `optimize_teacher_workload(teacher_id)` - Workload balancing

### Financial Analytics (2 models)
- `optimize_fee_structure()` - Fee structure optimization
- `predict_payment_delay(student_id)` - Payment delay prediction
- `analyze_fee_collection_patterns()` - Collection insights

### Attendance Analytics (2 models)
- `analyze_attendance_patterns(student_id)` - Pattern analysis
- `predict_student_absence(student_id)` - Absence prediction

### Transport Analytics (2 models)
- `optimize_transport_routes()` - Route optimization
- `predict_transport_delays(route_id)` - Delay prediction

### Communication Analytics (2 models)
- `optimize_message_timing()` - Optimal messaging times
- `classify_message_priority(content)` - Priority classification

### Academic Analytics (1 model)
- `predict_exam_grades(student_id)` - Grade prediction

### Resource Analytics (4 models)
- `recommend_library_books(student_id)` - Book recommendations
- `predict_inventory_needs()` - Stock prediction
- `analyze_hr_satisfaction()` - Employee satisfaction
- `forecast_budget_requirements()` - Budget forecasting

### System Analytics (9 models)
- `analyze_communication_effectiveness()` - Channel effectiveness
- `optimize_report_generation()` - Report optimization
- `optimize_dashboard_performance()` - Dashboard optimization
- `optimize_system_settings()` - Settings optimization
- `optimize_backup_schedule()` - Backup optimization
- `detect_security_anomalies()` - Security monitoring
- `generate_school_performance_insights()` - Overall insights
- `forecast_revenue(months)` - Revenue forecasting
- `get_high_risk_students()` - Risk identification

## Implementation Rules

### 1. Always Check Availability
```python
# ✅ Correct
if ML_AVAILABLE:
    result = ml_service.predict_student_performance(student_id)
else:
    result = {'error': 'ML models not available', 'risk_level': 'unknown'}

# ❌ Wrong
result = ml_service.predict_student_performance(student_id)  # Will crash if not available
```

### 2. Graceful Degradation
```python
# ✅ Provide fallback with default values
ml_insights = {
    'performance_risk': 'unknown',
    'recommendations': [],
    'risk_score': 0.5,
    'status': 'ml_unavailable'
}

if ML_AVAILABLE:
    try:
        ml_insights = ml_service.predict_student_performance(student_id)
    except Exception as e:
        ml_insights.update({'error': str(e), 'status': 'ml_error'})
```

### 3. Context Integration
```python
# ✅ Add ML data to all relevant contexts
context = {
    'students': students,
    'ml_insights': ml_insights,
    'ml_available': ML_AVAILABLE,
    'performance_predictions': performance_data if ML_AVAILABLE else {},
    'risk_alerts': risk_data if ML_AVAILABLE else [],
    'optimization_suggestions': suggestions if ML_AVAILABLE else []
}
```

### 4. Template Usage
```html
<!-- ✅ Enhanced template integration -->
{% if ml_available %}
    <div class="ml-insights-panel bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg">
        <h3 class="text-lg font-bold text-blue-800 mb-3">
            <i class="fas fa-brain mr-2"></i>AI Insights
        </h3>
        
        {% if ml_insights.performance_risk %}
            <div class="risk-indicator mb-3">
                <span class="font-medium">Performance Risk:</span>
                <span class="{% if ml_insights.performance_risk == 'high' %}text-red-600{% elif ml_insights.performance_risk == 'medium' %}text-yellow-600{% else %}text-green-600{% endif %}">
                    {{ ml_insights.performance_risk|title }}
                </span>
            </div>
        {% endif %}
        
        {% if ml_insights.recommendations %}
            <div class="recommendations">
                <h4 class="font-medium mb-2">Recommendations:</h4>
                {% for rec in ml_insights.recommendations %}
                    <div class="bg-white p-2 rounded mb-2 border-l-4 border-blue-400">
                        {{ rec.message }}
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    </div>
{% else %}
    <div class="ml-unavailable text-gray-500 text-sm">
        <i class="fas fa-info-circle mr-1"></i>
        ML insights unavailable - install scikit-learn for AI features
    </div>
{% endif %}
```

## Quick Integration Checklist (All Modules)

### Core Integration
- [ ] Import `ml_service` from `core.ml_integrations` with try/except
- [ ] Set `ML_AVAILABLE` flag based on import success
- [ ] Check `ML_AVAILABLE` before all ML calls
- [ ] Provide meaningful fallback data structures
- [ ] Handle exceptions gracefully with error logging

### View Integration
- [ ] Add ML insights to all relevant view contexts
- [ ] Use appropriate ML functions for each module
- [ ] Implement caching for expensive ML operations
- [ ] Add async support for heavy ML computations

### Template Integration
- [ ] Use conditional rendering with `ml_available` flag
- [ ] Display ML insights in user-friendly format
- [ ] Show setup instructions when ML unavailable
- [ ] Add visual indicators for risk levels and recommendations

### Performance Optimization
- [ ] Cache ML results for 5-15 minutes
- [ ] Limit ML processing to reasonable data sizes
- [ ] Use background tasks for heavy ML operations
- [ ] Monitor ML performance and errors

## Performance Considerations

### Async Usage
```python
# For heavy ML operations across multiple modules
import asyncio
from asgiref.sync import sync_to_async

async def get_comprehensive_ml_insights(student_id):
    if not ML_AVAILABLE:
        return {'error': 'ML not available'}
    
    # Run multiple ML predictions concurrently
    tasks = [
        sync_to_async(ml_service.predict_student_performance)(student_id),
        sync_to_async(ml_service.predict_dropout_risk)(student_id),
        sync_to_async(ml_service.analyze_attendance_patterns)(student_id),
        sync_to_async(ml_service.predict_payment_delay)(student_id)
    ]
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            'performance': results[0] if not isinstance(results[0], Exception) else None,
            'dropout_risk': results[1] if not isinstance(results[1], Exception) else None,
            'attendance': results[2] if not isinstance(results[2], Exception) else None,
            'payment_risk': results[3] if not isinstance(results[3], Exception) else None
        }
    except Exception as e:
        return {'error': f'ML processing failed: {str(e)}'}
```

### Caching Strategy
```python
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

def get_cached_ml_insights(cache_key, ml_function, *args, cache_timeout=300):
    """Get ML insights with intelligent caching"""
    insights = cache.get(cache_key)
    
    if not insights and ML_AVAILABLE:
        try:
            insights = ml_function(*args)
            # Cache successful results
            cache.set(cache_key, insights, cache_timeout)
        except Exception as e:
            # Cache errors for shorter time to retry sooner
            error_result = {'error': f'ML error: {str(e)}', 'timestamp': time.time()}
            cache.set(cache_key, error_result, 60)  # 1 min cache for errors
            insights = error_result
    
    return insights or {'error': 'ML not available'}

# Module-specific caching
def cache_student_ml_data(student_id):
    """Cache all student-related ML predictions"""
    cache_keys = {
        'performance': f'ml_student_performance_{student_id}',
        'dropout': f'ml_student_dropout_{student_id}',
        'attendance': f'ml_student_attendance_{student_id}',
        'payment': f'ml_student_payment_{student_id}'
    }
    
    results = {}
    for key, cache_key in cache_keys.items():
        if key == 'performance':
            results[key] = get_cached_ml_insights(cache_key, ml_service.predict_student_performance, student_id)
        elif key == 'dropout':
            results[key] = get_cached_ml_insights(cache_key, ml_service.predict_dropout_risk, student_id)
        elif key == 'attendance':
            results[key] = get_cached_ml_insights(cache_key, ml_service.analyze_attendance_patterns, student_id)
        elif key == 'payment':
            results[key] = get_cached_ml_insights(cache_key, ml_service.predict_payment_delay, student_id)
    
    return results
```

## Error Handling Pattern
```python
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def safe_ml_call(ml_function, *args, **kwargs):
    """Safely call ML function with comprehensive error handling"""
    if not ML_AVAILABLE:
        return {
            'error': 'ML models not available',
            'status': 'ml_unavailable',
            'suggestion': 'Install scikit-learn to enable AI features'
        }
    
    try:
        result = ml_function(*args, **kwargs)
        return {
            'data': result,
            'status': 'success',
            'timestamp': time.time()
        }
    except Exception as e:
        logger.error(f'ML function {ml_function.__name__} failed: {str(e)}')
        return {
            'error': f'ML processing failed: {str(e)}',
            'status': 'ml_error',
            'function': ml_function.__name__
        }

# Decorator for automatic ML error handling
def ml_safe(fallback_value=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not ML_AVAILABLE:
                return fallback_value or {'error': 'ML not available'}
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f'ML operation failed in {func.__name__}: {str(e)}')
                return fallback_value or {'error': str(e)}
        return wrapper
    return decorator

# Usage example
@ml_safe(fallback_value={'risk_level': 'unknown', 'score': 0.5})
def get_student_risk(student_id):
    return ml_service.predict_student_performance(student_id)
```

## Module-Specific Integration Examples

### Students Module Integration
```python
# students/views.py
class StudentDetailView(DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        
        if ML_AVAILABLE:
            ml_data = cache_student_ml_data(student.id)
            context.update({
                'performance_prediction': ml_data.get('performance', {}),
                'dropout_risk': ml_data.get('dropout', {}),
                'attendance_insights': ml_data.get('attendance', {}),
                'payment_risk': ml_data.get('payment', {})
            })
        
        context['ml_available'] = ML_AVAILABLE
        return context
```

### Dashboard Integration
```python
# dashboard/views.py
def dashboard_view(request):
    context = {'ml_available': ML_AVAILABLE}
    
    if ML_AVAILABLE:
        # Get comprehensive school insights
        school_insights = safe_ml_call(ml_service.generate_school_performance_insights)
        high_risk_students = safe_ml_call(ml_service.get_high_risk_students)
        financial_forecast = safe_ml_call(ml_service.forecast_revenue, 6)
        
        context.update({
            'school_insights': school_insights,
            'high_risk_students': high_risk_students,
            'financial_forecast': financial_forecast
        })
    
    return render(request, 'dashboard/index.html', context)
```

## Performance Monitoring
```python
# Monitor ML performance
class MLPerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        
        # Log slow ML operations
        if hasattr(request, '_ml_calls'):
            total_ml_time = sum(request._ml_calls)
            if total_ml_time > 0.5:  # 500ms threshold
                logger.warning(f'Slow ML operations: {total_ml_time:.3f}s on {request.path}')
        
        return response
```

This comprehensive ML integration ensures all 17 modules can leverage AI capabilities while maintaining system stability and performance.