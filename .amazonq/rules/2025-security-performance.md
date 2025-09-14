# 🔒 2025 Security & Performance (Compact)

## Security Essentials

### Authentication
```python
# WebAuthn passwordless
from django_webauthn import WebAuthnUser
async def login_webauthn(request):
    user = WebAuthnUser(request.user)
    if await user.verify_assertion(request.POST['assertion']):
        await login(request, request.user)

# MFA with TOTP
from django_otp.decorators import otp_required
@otp_required
async def secure_view(request):
    pass
```

### Input Validation
```python
# Pydantic models
from pydantic import BaseModel, validator
class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    age: int
    
    @validator('age')
    def validate_age(cls, v):
        if not 5 <= v <= 18:
            raise ValueError('Invalid age')
        return v
```

### Rate Limiting
```python
# AI-powered adaptive limiting
from django_ratelimit import ratelimit
@ratelimit(key='user', rate='adaptive', method='POST')
async def api_endpoint(request):
    pass
```

## Performance Optimization

### Database
```python
# Async ORM
students = await Student.objects.aselect_related('class').all()

# Bulk operations
await Student.objects.abulk_create(students, batch_size=1000)

# Vector search
from pgvector.django import VectorField
class Student(models.Model):
    embedding = VectorField(dimensions=384)
    
    class Meta:
        indexes = [GinIndex(fields=['metadata'])]
```

### Caching
```python
# Redis with async
from django.core.cache import cache
async def get_student_stats():
    stats = await cache.aget('student_stats')
    if not stats:
        stats = await calculate_stats()
        await cache.aset('student_stats', stats, 300)
    return stats
```

### Background Tasks
```python
# Celery with async
from celery import shared_task
@shared_task
async def send_notifications(student_ids):
    students = Student.objects.filter(id__in=student_ids)
    async for student in students:
        await send_email(student.email)
```

## Frontend Performance

### Lazy Loading
```html
<img loading="lazy" src="student.jpg" alt="Student">
<script type="module" async src="app.js"></script>
```

### Virtual Scrolling
```javascript
// For large lists
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) loadMore();
  });
});
```

### Service Worker
```javascript
// Cache strategies
self.addEventListener('fetch', event => {
  if (event.request.url.includes('/api/')) {
    event.respondWith(staleWhileRevalidate(event.request));
  }
});
```

## Monitoring

### OpenTelemetry
```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("student_create")
async def create_student(data):
    return await Student.objects.acreate(**data)
```

### Health Checks
```python
async def health_check(request):
    checks = await asyncio.gather(
        check_db(), check_redis(), check_external_apis()
    )
    return JsonResponse({'healthy': all(checks)})
```

## Security Headers
```python
# settings.py
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
CSP_DEFAULT_SRC = ["'self'"]
```

## Performance Targets
- **Response Time**: <50ms for API calls
- **Page Load**: <2s for initial load
- **Database**: <10ms for simple queries
- **Memory**: <512MB per worker
- **CPU**: <70% average usage

## Quick Checklist
- [ ] Async views for I/O operations
- [ ] Database indexes on query fields
- [ ] Redis caching for expensive operations
- [ ] CDN for static assets
- [ ] Gzip compression enabled
- [ ] WebAuthn authentication
- [ ] Rate limiting on APIs
- [ ] Input validation with Pydantic
- [ ] HTTPS everywhere
- [ ] Security headers configured