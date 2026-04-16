# AI Service Testing Guide

This guide explains how to test and validate the AI Service implementation.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Validation Script](#validation-script)
4. [Running Tests](#running-tests)
5. [Test Coverage](#test-coverage)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before running tests, ensure you have:

- ✅ PostgreSQL with pgvector extension
- ✅ Redis running
- ✅ Python 3.10+
- ✅ API keys for Anthropic and/or OpenAI
- ✅ Test database configured

---

## Environment Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

### 2. Configure Environment

Create `.env.test` file:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/car_ads_test
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/car_ads_test

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Service
ENABLE_AI_SERVICE=true
ANTHROPIC_API_KEY=sk-ant-test-key
OPENAI_API_KEY=sk-test-key

# Disable rate limiting in tests
RATE_LIMIT_PER_MINUTE=10000
```

### 3. Run Migrations

```bash
# Apply migrations to test database
TEST_DATABASE=true alembic upgrade head
```

---

## Validation Script

The validation script performs comprehensive checks:

```bash
python scripts/validate_ai_setup.py
```

### What It Checks:

1. **Environment Variables** - Required and optional config
2. **pgvector Extension** - PostgreSQL extension installed
3. **Redis Connection** - Cache service available
4. **API Keys** - Anthropic and OpenAI key validity
5. **Database Migrations** - Migration status
6. **AI Services** - Service initialization and health
7. **Embeddings** - Existing embeddings in database

### Expected Output:

```
✅ All 7 validation checks passed! 🎉

AI Service is ready to use!
```

### If Checks Fail:

The script will tell you exactly what to fix:

```
❌ pgvector extension NOT installed
ℹ️  Run: CREATE EXTENSION IF NOT EXISTS vector;

⚠️  ANTHROPIC_API_KEY not set
ℹ️  Add to .env: ANTHROPIC_API_KEY=sk-ant-xxxxx
```

---

## Running Tests

### Run All Tests

```bash
# Run all tests
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=app/services --cov-report=html
```

### Run Specific Test Files

```bash
# Integration tests
pytest tests/api/test_ai_integration.py -v

# LLM Client tests
pytest tests/services/test_llm_client.py -v

# Agent tests
pytest tests/services/agents/test_agents.py -v
```

### Run Specific Test Cases

```bash
# Run specific test
pytest tests/services/test_llm_client.py::TestLLMClient::test_llm_client_initialization -v

# Run tests matching pattern
pytest -k "test_analyze" -v
```

### Run Tests by Marker

```bash
# Run only fast tests
pytest -m "not slow" -v

# Run integration tests only
pytest -m "integration" -v
```

---

## Test Coverage

### Current Test Files:

#### Integration Tests (`tests/api/test_ai_integration.py`)

- ✅ Health check endpoint
- ✅ Vehicle analysis endpoint
- ✅ Semantic search endpoint
- ✅ Similar vehicles endpoint
- ✅ Ad content generation
- ✅ Authentication/authorization
- ✅ Database updates
- ✅ Performance validation

#### Unit Tests (`tests/services/`)

- ✅ LLM Client (`test_llm_client.py`)
  - Claude API calls
  - OpenAI fallback
  - Retry logic
  - Circuit breaker
  - Cost tracking

- ✅ AI Agents (`agents/test_agents.py`)
  - AnalyzerAgent
  - GeneratorAgent
  - ScorerAgent
  - BaseAgent functionality

### Coverage Goals:

- Unit tests: > 80% coverage
- Integration tests: All endpoints covered
- Critical paths: 100% coverage

### View Coverage Report:

```bash
pytest --cov=app/services --cov-report=html
open htmlcov/index.html
```

---

## Embedding Population

After validation, populate embeddings for existing vehicles:

### 1. Dry Run (See what would be done)

```bash
python scripts/populate_embeddings.py --dry-run
```

### 2. Populate All Vehicles

```bash
python scripts/populate_embeddings.py
```

### 3. Populate Specific Vehicle

```bash
python scripts/populate_embeddings.py --vehicle-id <uuid>
```

### 4. Batch Processing

```bash
# Process 50 vehicles at a time
python scripts/populate_embeddings.py --batch-size 50
```

### 5. Limit Number of Vehicles

```bash
# Process only first 100 vehicles
python scripts/populate_embeddings.py --limit 100
```

---

## Manual Testing

### Test Vehicle Analysis

```bash
# 1. Create a test vehicle (via API or DB)
# 2. Run analysis
curl -X POST http://localhost:8000/api/v1/vehicles/{vehicle_id}/analyze \
  -H "Authorization: Bearer {manager_token}" | jq

# Expected response
{
  "price_market": 110000.0,
  "price_score": 80,
  "price_position": "good_price",
  "selling_points": ["unico_dono", "baixa_quilometragem"],
  "target_audience": ["familias", "profissionais"],
  "suggested_improvements": ["mais_fotos_interior"],
  "estimated_ctr": 0.045,
  "estimated_conversion": 0.028,
  ...
}
```

### Test Semantic Search

```bash
# Natural language search
curl "http://localhost:8000/api/v1/vehicles/search/semantic?query=SUV%20Honda%20forte%20e%20espaçoso&limit=5" \
  -H "Authorization: Bearer {token}" | jq
```

### Test Similar Vehicles

```bash
# Find similar vehicles
curl http://localhost:8000/api/v1/vehicles/{vehicle_id}/similar?limit=10 \
  -H "Authorization: Bearer {token}" | jq
```

### Test Ad Generation

```bash
# Generate headline
curl -X POST "http://localhost:8000/api/v1/vehicles/ai/generate-ad?vehicle_id={vehicle_id}&content_type=headline" \
  -H "Authorization: Bearer {token}" | jq

# Generate full ad
curl -X POST "http://localhost:8000/api/v1/vehicles/ai/generate-ad?vehicle_id={vehicle_id}&content_type=full" \
  -H "Authorization: Bearer {token}" | jq
```

### Check AI Health

```bash
curl http://localhost:8000/health/ai | jq

# Expected
{
  "status": "healthy",
  "services": {
    "llm_client": "ok",
    "embedding_service": "ok",
    "feature_store": "ok"
  }
}
```

---

## Troubleshooting

### Tests Fail with "AI service is disabled"

**Solution**: Set `ENABLE_AI_SERVICE=true` in `.env`

```bash
echo "ENABLE_AI_SERVICE=true" >> .env
```

### Tests Fail with "No module named 'anthropic'"

**Solution**: Install dependencies

```bash
pip install -r requirements.txt
```

### pgvector Extension Not Found

**Solution**: Install pgvector in PostgreSQL

```bash
# Using Docker
docker-compose exec postgres psql -U postgres -d car_ads_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Using local PostgreSQL
psql -U postgres -d car_ads_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Redis Connection Refused

**Solution**: Start Redis

```bash
# Using Docker
docker-compose up -d redis

# Using local Redis
redis-server
```

### API Key Validation Fails

**Solution**: Check API keys are set correctly

```bash
# Check Anthropic key
echo $ANTHROPIC_API_KEY

# Check OpenAI key
echo $OPENAI_API_KEY

# Test Anthropic API
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

### Tests Are Slow

**Solution**: Use mock API keys for faster unit tests

```bash
# In .env.test
ANTHROPIC_API_KEY=test-key-mock
OPENAI_API_KEY=test-key-mock
```

### Embedding Generation Fails

**Solution**: Check OpenAI API key and quota

```bash
# Test OpenAI API
curl https://api.openai.com/v1/embeddings \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input":"test","model":"text-embedding-3-small"}'
```

---

## CI/CD Integration

### GitHub Actions Example:

```yaml
name: AI Service Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: car_ads_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run migrations
        run: alembic upgrade head
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/car_ads_test

      - name: Run validation
        run: python scripts/validate_ai_setup.py

      - name: Run tests
        run: pytest --cov=app/services --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Best Practices

### 1. Run Tests Before Committing

```bash
# Quick check
pytest -q

# Full check
pytest --cov
```

### 2. Keep Tests Isolated

- Each test should be independent
- Use fixtures for common setup
- Clean up after tests

### 3. Mock External APIs

- Don't make real API calls in unit tests
- Use `unittest.mock` for mocking
- Test error conditions

### 4. Test Edge Cases

- Empty data
- Invalid input
- API failures
- Timeouts

### 5. Keep Tests Fast

- Unit tests: < 1s each
- Integration tests: < 5s each
- Use `@pytest.mark.slow` for slow tests

---

## Next Steps

After all tests pass:

1. ✅ Run validation script
2. ✅ Populate embeddings
3. ✅ Monitor metrics in production
4. ✅ Set up CI/CD pipeline
5. ✅ Configure alerts for failures

---

## Support

For issues or questions:

- Check logs: `docker-compose logs -f backend`
- Review validation output: `python scripts/validate_ai_setup.py`
- Consult docs: `backend/AI_SERVICE_SETUP.md`
- Check test logs: `pytest -v -s`
