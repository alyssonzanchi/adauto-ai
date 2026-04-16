# AI Service Setup Guide

This guide explains how to configure and use the AI-powered vehicle analysis features.

## Prerequisites

1. **API Keys**: You need API keys for:
   - **Anthropic Claude** (primary): https://console.anthropic.com/
   - **OpenAI** (fallback + embeddings): https://platform.openai.com/

2. **PostgreSQL with pgvector**: Ensure pgvector extension is installed
   ```bash
   # In PostgreSQL
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Redis**: For caching and performance

## Configuration

### 1. Environment Variables

Add these to your `.env` file:

```bash
# AI Service Configuration
ENABLE_AI_SERVICE=true                    # Master switch for AI features
ENABLE_CLAUDE_AI=true                     # Enable Claude (primary LLM)
ENABLE_OPENAI_FALLBACK=true               # Enable OpenAI fallback
ENABLE_VECTOR_SEARCH=true                 # Enable semantic search
ENABLE_EMBEDDING_CACHE=true               # Enable embedding caching

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxx           # Your Anthropic API key
OPENAI_API_KEY=sk-xxxxx                   # Your OpenAI API key

# AI Models
AI_MODEL_PRIMARY=claude-3-5-sonnet-20241022
AI_MODEL_FALLBACK=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small

# AI Configuration
AI_MAX_RETRIES=3                          # Retry attempts for API calls
AI_TIMEOUT=30                             # Request timeout in seconds
AI_ENABLE_CACHING=true                    # Enable response caching

# Vector Store Configuration
VECTOR_DIMENSIONS=1536                     # Embedding dimensions
VECTOR_SIMILARITY_THRESHOLD=0.7            # Minimum similarity for search

# Feature Store (Redis Cache)
FEATURE_CACHE_TTL=3600                    # Vehicle features cache (1h)
EMBEDDING_CACHE_TTL=86400                 # Embedding cache (24h)
```

### 2. Database Migration

Run the pgvector migration:

```bash
cd backend
alembic upgrade head
```

This will:
- Enable pgvector extension
- Add `description_embedding` and `features_embedding` columns
- Create HNSW indexes for fast similarity search

### 3. Verify Installation

Check AI service health:

```bash
curl http://localhost:8000/health/ai
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "llm_client": "ok",
    "embedding_service": "ok",
    "feature_store": "ok"
  }
}
```

## Usage

### Vehicle Analysis

Analyze a vehicle with AI:

```bash
curl -X POST http://localhost:8000/api/v1/vehicles/{vehicle_id}/analyze \
  -H "Authorization: Bearer {token}"
```

Response includes:
- `price_market`: Estimated fair market price
- `price_score`: Competitiveness score (0-100)
- `selling_points`: List of key selling points
- `target_audience': List of audience segments
- `suggested_improvements`: Actionable suggestions
- `estimated_ctr`: Expected click-through rate
- `estimated_conversion`: Expected conversion rate

### Semantic Search

Search vehicles using natural language:

```bash
curl "http://localhost:8000/api/v1/vehicles/search/semantic?query=SUV familiar econômico&limit=10" \
  -H "Authorization: Bearer {token}"
```

### Similar Vehicles

Find vehicles similar to a given vehicle:

```bash
curl http://localhost:8000/api/v1/vehicles/{vehicle_id}/similar?limit=10 \
  -H "Authorization: Bearer {token}"
```

### Ad Content Generation

Generate advertisement copy:

```bash
curl -X POST http://localhost:8000/api/v1/vehicles/ai/generate-ad?vehicle_id={vehicle_id} \
  -H "Authorization: Bearer {token}"
```

## Background Tasks

Generate embeddings asynchronously:

```python
from app.tasks.ai_tasks import generate_vehicle_embeddings

# Queue embedding generation
generate_vehicle_embeddings.delay(str(vehicle_id))
```

Batch analyze vehicles:

```python
from app.tasks.ai_tasks import batch_analyze_vehicles

# Queue batch analysis
batch_analyze_vehicles.delay([str(id1), str(id2), str(id3)])
```

## Feature Flags

Control AI features via environment variables:

```bash
# Disable all AI features
ENABLE_AI_SERVICE=false

# Disable only semantic search
ENABLE_VECTOR_SEARCH=false

# Disable OpenAI fallback (use Claude only)
ENABLE_OPENAI_FALLBACK=false

# Disable caching
ENABLE_EMBEDDING_CACHE=false
```

## Monitoring

### Metrics

Access AI service metrics:

```python
from app.services.ai.orchestrator import get_orchestrator

orchestrator = get_orchestrator()
metrics = orchestrator.get_metrics()

print(metrics)
# {
#     "analyses_performed": 150,
#     "ads_generated": 45,
#     "price_scores": 200,
#     "cache_hits": 1200,
#     "errors": 3,
#     "llm_client": {...},
#     "embedding_service": {...},
#     ...
# }
```

### Performance Targets

- Vehicle analysis: < 3s (P95)
- Semantic search: < 100ms (P95)
- Cache retrieval: < 10ms
- Cache hit rate: > 80%

## Cost Estimation

Based on OpenAI and Anthropic pricing (2025):

### Vehicle Analysis
- Claude 3.5 Sonnet: ~$0.05 per analysis
- OpenAI GPT-4 Turbo (fallback): ~$0.10 per analysis

### Embeddings
- OpenAI text-embedding-3-small: $0.00002/1K tokens
- Typical vehicle: ~$0.0002 per embedding
- 1000 vehicles: ~$0.20

### Monthly Estimates
- 1000 vehicle analyses: ~$50-100
- 10,000 embedding generations: ~$2
- **Total**: ~$50-150/month for moderate usage

## Troubleshooting

### AI Service Not Starting

```bash
# Check logs
docker-compose logs backend

# Verify API keys
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY
```

### pgvector Errors

```sql
-- Check if extension is installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Install if missing
CREATE EXTENSION IF NOT EXISTS vector;
```

### Cache Issues

```bash
# Clear Redis cache
redis-cli FLUSHDB

# Check Redis connection
redis-cli PING
```

### High Fallback Rate

If OpenAI fallback rate is > 10%:

1. Check Claude API key validity
2. Verify Claude API status
3. Check rate limits
4. Review error logs

## Rollback

If AI service causes issues:

```bash
# Disable AI service (uses mock)
ENABLE_AI_SERVICE=false

# Restart backend
docker-compose restart backend
```

The system will fall back to the mock AI service without data loss.

## Best Practices

1. **Cache Warming**: Pre-generate embeddings for existing vehicles
2. **Batch Processing**: Use background tasks for bulk operations
3. **Monitoring**: Track metrics and costs regularly
4. **Rate Limiting**: Implement rate limits for AI endpoints
5. **Fallback Strategy**: Always have OpenAI fallback enabled

## Next Steps

- Week 6: Advanced Analyzer & Generator Agents
- Week 7: ML Models (XGBoost) for price prediction
- Week 8: Predictor & Optimizer Agents

## Support

For issues or questions:
- Check logs: `docker-compose logs -f backend`
- Review metrics: `/health/ai` endpoint
- Consult documentation: `docs/referencias/roadmap.md`
