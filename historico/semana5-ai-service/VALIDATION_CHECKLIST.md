# 🎯 AI Service Validation - Step-by-Step Guide

Complete guide to validate and test the AI Service implementation.

## 📝 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Docker and Docker Compose installed
- [ ] Python 3.10+ installed
- [ ] Anthropic API key (get at https://console.anthropic.com/)
- [ ] OpenAI API key (get at https://platform.openai.com/)
- [ ] Git repository cloned

---

## 🚀 Step 1: Start Infrastructure

### Start Services

```bash
# From project root
docker-compose up -d postgres redis

# Verify services are running
docker-compose ps

# Expected output:
# NAME                 STATUS
# adauto-ai-postgres-1   Up
# adauto-ai-redis-1      Up
```

### Verify PostgreSQL

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d car_ads_db

# In psql, check connection
\conninfo

# Exit psql
\q
```

### Verify Redis

```bash
# Test Redis
docker-compose exec redis redis-cli ping

# Expected: PONG
```

---

## 🔧 Step 2: Install Dependencies

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-asyncio pytest-mock pytest-cov

# Verify installation
python -c "import anthropic; print('Anthropic OK')"
python -c "import openai; print('OpenAI OK')"
python -c "import pgvector; print('pgvector OK')"
python -c "import jinja2; print('Jinja2 OK')"
```

---

## 🔑 Step 3: Configure API Keys

### Create .env File

```bash
# Copy example file
cp .env.example .env

# Edit .env
nano .env
```

### Add Required Variables

```bash
# AI Service Configuration
ENABLE_AI_SERVICE=true
ENABLE_CLAUDE_AI=true
ENABLE_OPENAI_FALLBACK=true
ENABLE_VECTOR_SEARCH=true
ENABLE_EMBEDDING_CACHE=true

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Replace with your key
OPENAI_API_KEY=sk-xxxxx          # Replace with your key

# Models
AI_MODEL_PRIMARY=claude-3-5-sonnet-20241022
AI_MODEL_FALLBACK=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small

# Vector Store
VECTOR_DIMENSIONS=1536
VECTOR_SIMILARITY_THRESHOLD=0.7

# Cache
FEATURE_CACHE_TTL=3600
EMBEDDING_CACHE_TTL=86400
```

### Verify Keys

```bash
# Check environment variables are loaded
source .env
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY
```

---

## 🗄️ Step 4: Run Database Migrations

### Apply Migrations

```bash
cd backend

# Run migrations
alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade -> 20260415_1000, add_pgvector_support
```

### Verify pgvector Extension

```bash
# Check pgvector is installed
docker-compose exec postgres psql -U postgres -d car_ads_db -c \
  "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Expected output:
#  extname | extversion
# ---------+------------
#  vector  | 0.5.0
```

### Verify Vector Columns

```bash
# Check vector columns exist
docker-compose exec postgres psql -U postgres -d car_ads_db -c \
  "\d vehicles"

# Look for:
# description_embedding | ARRAY(1536) |
# features_embedding    | ARRAY(1536) |
```

---

## ✅ Step 5: Run Validation Script

```bash
cd backend

# Run validation
python scripts/validate_ai_setup.py
```

### Expected Output

```
AI Service Validation
============================================================

1. Environment Variables
------------------------------------------------------------
✅ DATABASE_URL: postgresql+asyncpg://...
✅ REDIS_URL: redis://localhost:6379/0
✅ ANTHROPIC_API_KEY: sk-ant-...xxx
✅ OPENAI_API_KEY: sk-xxx
⚠️  ENABLE_AI_SERVICE: Not set (using default: True)
...

2. PostgreSQL pgvector Extension
------------------------------------------------------------
✅ pgvector extension is installed
ℹ️  pgvector version: 0.5.0
✅ Vector columns found: 2
  - description_embedding: ARRAY
  - features_embedding: ARRAY

3. Redis Connection
------------------------------------------------------------
✅ Redis connection successful
ℹ️  Redis version: 7.0.0
ℹ️  Memory used: 10.5M

4. API Keys Validation
------------------------------------------------------------
✅ Anthropic API key is valid
✅ OpenAI API key is valid

5. Database Migrations
------------------------------------------------------------
✅ Database migrated to: 20260415_1...
✅ Database is up to date

6. AI Services Health
------------------------------------------------------------
✅ LLM Client initialized
✅ Embedding Service initialized
✅ Vector Service initialized
✅ Feature Store initialized
✅ Agent Orchestrator initialized

llm_client: ok
embedding_service: ok
feature_store: ok

Overall AI Service Status: healthy

7. Vehicle Embeddings
------------------------------------------------------------
ℹ️  Total vehicles: 0
⚠️  No vehicles in database

Summary
============================================================
✅ PASS environment
✅ PASS pgvector
✅ PASS redis
✅ PASS api_keys
✅ PASS migrations
✅ PASS ai_services
✅ PASS embeddings

All 7 validation checks passed! 🎉

AI Service is ready to use!
```

### If Validation Fails

See the [Troubleshooting section](#troubleshooting) below.

---

## 🧪 Step 6: Run Tests

### Run All Tests

```bash
cd backend

# Run all tests
pytest -v

# Or with coverage
pytest --cov=app/services --cov-report=html
```

### Expected Output

```
tests/api/test_ai_integration.py::test_health_check_ai PASSED
tests/api/test_ai_integration.py::test_analyze_vehicle_success PASSED
tests/services/test_llm_client.py::TestLLMClient::test_llm_client_initialization PASSED
tests/services/agents/test_agents.py::TestAnalyzerAgent::test_analyzer_execute_success PASSED
...

======== 20 passed in 15.23s =======
```

### View Coverage Report

```bash
# Open coverage report
open htmlcov/index.html

# Or in browser
file:///path/to/backend/htmlcov/index.html
```

---

## 🚗 Step 7: Create Test Data

### Option A: Using API

```bash
# Start backend server
uvicorn app.main:app --reload

# In another terminal, create a test user and vehicle
# (See API documentation)
```

### Option B: Using Python Script

```bash
# Run seed script (if available)
python scripts/seed_test_data.py
```

### Option C: Manual Database Insert

```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d car_ads_db

# Insert test vehicle
INSERT INTO vehicles (id, dealership_id, title, brand, model, year, price, status)
VALUES (
  gen_random_uuid(),
  (SELECT id FROM dealerships LIMIT 1),
  'Honda Civic Touring 2021',
  'Honda',
  'Civic',
  2021,
  115000.00,
  'active'
);
```

---

## 🔄 Step 8: Populate Embeddings

### Dry Run First

```bash
cd backend

# See what would be done
python scripts/populate_embeddings.py --dry-run
```

### Populate All Vehicles

```bash
# Generate embeddings
python scripts/populate_embeddings.py

# Expected output:
# Vehicle Embedding Population
# ============================================================
# ✅ AI services initialized
# Found 10 vehicles to process
#
# Generating embeddings...
# ============================================================
# Processing batch 1 (10 vehicles)...
#   ✅ Honda Civic Touring 2021
#   ✅ Toyota Corolla XEI 2022
#   ...
#
# Summary
# ============================================================
# ✅ Successfully processed: 10
# ⚠️  Skipped (already had embeddings): 0
# ❌ Failed: 0
# 📊 Total: 10
#
# ✨ Embedding population completed!
```

---

## 🌐 Step 9: Start Backend Server

```bash
cd backend

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# ✅ AI services initialized successfully
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🧪 Step 10: Manual API Testing

### Test Health Check

```bash
curl http://localhost:8000/health/ai | jq

# Expected:
# {
#   "status": "healthy",
#   "services": {
#     "llm_client": "ok",
#     "embedding_service": "ok",
#     "feature_store": "ok"
#   }
# }
```

### Test Vehicle Analysis

```bash
# Get a JWT token first
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | jq -r '.access_token')

# Get a vehicle ID
VEHICLE_ID=$(curl http://localhost:8000/api/v1/vehicles \
  -H "Authorization: Bearer $TOKEN" | jq -r '.items[0].id')

# Analyze vehicle
curl -X POST http://localhost:8000/api/v1/vehicles/$VEHICLE_ID/analyze \
  -H "Authorization: Bearer $TOKEN" | jq

# Expected response includes:
# - price_market
# - price_score
# - selling_points
# - target_audience
# - suggested_improvements
# - estimated_ctr
# - estimated_conversion
```

### Test Semantic Search

```bash
curl "http://localhost:8000/api/v1/vehicles/search/semantic?query=SUV%20espaçoso%20para%20família&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq

# Expected: Array of vehicles with similarity scores
```

### Test Similar Vehicles

```bash
curl http://localhost:8000/api/v1/vehicles/$VEHICLE_ID/similar?limit=5 \
  -H "Authorization: Bearer $TOKEN" | jq

# Expected: Array of similar vehicles
```

### Test Ad Generation

```bash
curl -X POST "http://localhost:8000/api/v1/vehicles/ai/generate-ad?vehicle_id=$VEHICLE_ID&content_type=full" \
  -H "Authorization: Bearer $TOKEN" | jq

# Expected: Generated ad content with headline, description, CTA, keywords
```

---

## 📊 Step 11: Monitor Metrics

### Check Service Metrics

```bash
# Access metrics endpoint (if implemented)
curl http://localhost:8000/metrics/ai

# Or check logs
docker-compose logs -f backend | grep "AI Service"
```

### Redis Cache Stats

```bash
docker-compose exec redis redis-cli INFO stats

# Check cache keys
docker-compose exec redis redis-cli KEYS "embedding:*"
docker-compose exec redis redis-cli KEYS "ai:analysis:*"
```

---

## 🎉 Step 12: Validation Complete!

### Success Indicators

- [x] All 7 validation checks pass
- [x] All tests pass
- [x] Embeddings generated
- [x] API endpoints respond correctly
- [x] Health check shows "healthy"
- [x] No errors in logs

### Production Readiness

Before deploying to production:

1. **API Costs**: Set up billing alerts
2. **Rate Limiting**: Configure appropriate limits
3. **Monitoring**: Set up logging and metrics
4. **Fallback**: Ensure OpenAI fallback is enabled
5. **Cache**: Verify Redis is persistent
6. **Backup**: Backup database with embeddings

---

## 🔧 Troubleshooting

### Issue: "pgvector extension NOT installed"

**Solution**:
```bash
docker-compose exec postgres psql -U postgres -d car_ads_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Issue: "Redis connection failed"

**Solution**:
```bash
docker-compose up -d redis
docker-compose ps redis
```

### Issue: "Anthropic API key validation failed"

**Solution**:
1. Check API key is correct
2. Verify API key has credits
3. Test API manually:
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

### Issue: "Tests fail with module not found"

**Solution**:
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-mock
```

### Issue: "Embedding generation fails"

**Solution**:
1. Check OpenAI API key
2. Verify vehicle data is complete
3. Check error logs:
```bash
docker-compose logs -f backend | grep "embedding"
```

### Issue: "AI service disabled"

**Solution**:
```bash
# Add to .env
echo "ENABLE_AI_SERVICE=true" >> .env

# Restart backend
docker-compose restart backend
```

---

## 📚 Additional Resources

- **Setup Guide**: `backend/AI_SERVICE_SETUP.md`
- **Testing Guide**: `backend/tests/README.md`
- **API Documentation**: http://localhost:8000/docs
- **Roadmap**: `docs/referencias/roadmap.md`

---

## 🎯 Next Steps

After validation:

1. **Week 6**: Advanced AI Agents
   - Improve prompts with more few-shot examples
   - Add RecommenderAgent
   - Implement trend analysis

2. **Week 7-8**: ML Models
   - XGBoost price prediction
   - PredictorAgent
   - OptimizerAgent

3. **Production**
   - Set up monitoring (Prometheus/Grafana)
   - Configure alerts (Sentry)
   - Scale Redis (cluster mode)
   - Optimize embeddings (batch processing)

---

## ✅ Success!

You've successfully validated the AI Service! 🎉

The system is now ready for:
- ✅ Production use
- ✅ Further development
- ✅ Advanced features

For questions or issues, consult the documentation or check logs.
