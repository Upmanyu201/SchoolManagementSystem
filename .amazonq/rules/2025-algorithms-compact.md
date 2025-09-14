# 🧠 Algorithm Rules (2025 Compact)

## Core Principles
- **Performance**: <50ms operations
- **AI-Enhanced**: ML predictions
- **Async-First**: Python 3.12+ async/await
- **Vector Search**: Semantic queries
- **Real-time**: WebSocket updates

## Algorithm Types

### Data Processing
```python
# Async bulk operations
async def process_bulk(data, batch_size=1000):
    async for chunk in achunked(data, batch_size):
        await process_chunk(chunk)

# Parallel processing
from asyncio import gather
results = await gather(*[process_item(item) for item in items])
```

### AI-Powered Search
```python
# Vector search
from pgvector.django import VectorField
class Student(models.Model):
    embedding = VectorField(dimensions=384)
    
    @classmethod
    async def semantic_search(cls, query):
        embedding = await get_embedding(query)
        return cls.objects.order_by(cls.embedding.cosine_distance(embedding))[:10]

# Fuzzy matching
from rapidfuzz import fuzz
def fuzzy_search(query, items, threshold=80):
    return [(item, score) for item in items 
            if (score := fuzz.ratio(query, item)) >= threshold]
```

### Smart Caching
```python
# Adaptive TTL cache
class SmartCache:
    def __init__(self):
        self.cache = {}
        self.access_count = defaultdict(int)
    
    async def get_or_set(self, key, compute_func, base_ttl=300):
        if key in self.cache and not self._expired(key):
            self.access_count[key] += 1
            return self.cache[key]['value']
        
        value = await compute_func()
        ttl = base_ttl * (1 + min(self.access_count[key] / 10, 2))
        self.cache[key] = {'value': value, 'expires': time.time() + ttl}
        return value
```

### Validation Engine
```python
# Pydantic validation
from pydantic import BaseModel, validator
class StudentData(BaseModel):
    name: str
    age: int
    email: str
    
    @validator('age')
    def validate_age(cls, v):
        if not 5 <= v <= 18:
            raise ValueError('Invalid age')
        return v
```

## Integration Patterns

### Service Layer
```python
class AlgorithmService:
    algorithms = {
        'search': StudentSearchAlgorithm(),
        'predict': PerformancePrediction(),
        'validate': DataValidation()
    }
    
    async def execute(self, name, data):
        return await self.algorithms[name].process(data)
```

### Background Tasks
```python
from celery import shared_task
@shared_task
async def process_async(algorithm, data):
    service = AlgorithmService()
    return await service.execute(algorithm, data)
```

### Performance Monitoring
```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("algorithm_execution")
async def execute_with_monitoring(algorithm, data):
    start = time.time()
    result = await algorithm.process(data)
    duration = time.time() - start
    
    # Log if slow
    if duration > 0.05:  # 50ms threshold
        logger.warning(f"Slow algorithm: {algorithm.__class__.__name__} took {duration:.3f}s")
    
    return result
```

## School Management Examples

### Fee Calculation
```python
class FeeCalculator:
    async def calculate(self, student_id, month):
        student = await Student.objects.aget(id=student_id)
        base_fee = await self.get_base_fee(student.class_id)
        discounts = await self.calculate_discounts(student)
        return base_fee - discounts
```

### Attendance Analysis
```python
class AttendanceAnalyzer:
    async def analyze_pattern(self, student_id):
        records = await AttendanceRecord.objects.filter(
            student_id=student_id
        ).aorder_by('-date')[:30]
        
        rate = sum(1 for r in records if r.present) / len(records)
        trend = self.calculate_trend([r.present for r in records])
        
        return {'rate': rate, 'trend': trend}
```

### Performance Prediction
```python
from sklearn.ensemble import RandomForestClassifier
class PerformancePredictor:
    def __init__(self):
        self.model = RandomForestClassifier()
    
    async def predict_risk(self, student_id):
        features = await self.extract_features(student_id)
        risk_score = self.model.predict_proba([features])[0][1]
        return {'risk': 'high' if risk_score > 0.7 else 'low', 'score': risk_score}
```

## Quick Checklist
- [ ] Use async for I/O operations
- [ ] Implement vector search for semantic queries
- [ ] Add caching for expensive operations
- [ ] Monitor performance with OpenTelemetry
- [ ] Use Pydantic for validation
- [ ] Background tasks for heavy processing
- [ ] AI/ML for predictions and recommendations