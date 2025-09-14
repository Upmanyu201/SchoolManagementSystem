# 🧪 Testing Rules (2025 Compact)

## Test Strategy
- **Unit Tests (70%)**: Individual functions
- **Integration (20%)**: Component interactions  
- **E2E (10%)**: Complete workflows
- **AI Testing**: Visual regression, property-based

## Core Patterns

### Unit Testing
```python
# Async test methods
import pytest
@pytest.mark.asyncio
async def test_student_creation():
    student = await Student.objects.acreate(name="John", age=15)
    assert student.name == "John"

# Factory pattern
import factory
class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student
    name = factory.Faker('name')
    age = factory.Faker('random_int', min=5, max=18)
```

### API Testing
```python
from rest_framework.test import APITestCase
class StudentAPITest(APITestCase):
    async def test_create_student(self):
        data = {'name': 'Jane', 'age': 16}
        response = await self.aclient.post('/api/students/', data)
        self.assertEqual(response.status_code, 201)
```

### Property-Based Testing
```python
from hypothesis import given, strategies as st
@given(name=st.text(min_size=1), age=st.integers(5, 18))
def test_student_properties(name, age):
    student = Student(name=name, age=age)
    assert student.is_valid_age()
```

### E2E with Playwright
```python
import pytest
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_student_workflow():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.goto('/students/add/')
        await page.fill('[name="name"]', 'Test Student')
        await page.click('button[type="submit"]')
        
        await page.wait_for_selector('.success-message')
        await browser.close()
```

### AI Visual Testing
```python
# Visual regression with AI
async def test_visual_regression():
    async with async_playwright() as p:
        page = await p.chromium.launch().new_page()
        await page.goto('/dashboard/')
        
        # AI-powered visual comparison
        screenshot = await page.screenshot()
        assert await compare_with_ai_baseline(screenshot, 'dashboard.png')
```

## Performance Testing
```python
# Load testing
from locust import HttpUser, task
class SchoolUser(HttpUser):
    @task(3)
    def view_students(self):
        self.client.get("/students/")
    
    @task(1)
    def add_student(self):
        self.client.post("/students/", {"name": "Test", "age": 15})

# Performance benchmarks
def test_query_performance():
    with timer() as t:
        students = Student.objects.select_related('class').all()[:100]
        list(students)  # Force evaluation
    assert t.elapsed < 0.1  # <100ms
```

## Test Configuration
```python
# settings/test.py
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable migrations for speed
class DisableMigrations:
    def __contains__(self, item): return True
    def __getitem__(self, item): return None
MIGRATION_MODULES = DisableMigrations()
```

## Mock Patterns
```python
from unittest.mock import patch, AsyncMock

@patch('services.email_service.send_email')
async def test_notification(mock_send):
    mock_send.return_value = AsyncMock()
    await send_fee_reminder(student_id=1)
    mock_send.assert_called_once()
```

## Test Data
```python
# Fixtures
@pytest.fixture
async def student():
    return await Student.objects.acreate(name="Test", age=15)

# Factory with relationships
class StudentWithClassFactory(StudentFactory):
    student_class = factory.SubFactory(ClassFactory)
```

## CI/CD Testing
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - run: pip install -r requirements-test.txt
    - run: pytest --cov=. --cov-report=xml
    - run: playwright test
```

## Quick Checklist
- [ ] Async test methods for async code
- [ ] Factory pattern for test data
- [ ] Property-based testing for edge cases
- [ ] Playwright for E2E workflows
- [ ] AI visual regression testing
- [ ] Performance benchmarks
- [ ] Mock external dependencies
- [ ] CI/CD pipeline integration