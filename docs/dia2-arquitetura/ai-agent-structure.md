# AI Agent Structure - Car Ads Platform

## Overview

Este documento detalha a arquitetura completa do sistema de IA, incluindo os agentes, prompts templates, modelos de ML e estratégias de otimização.

---

## 1. Arquitetura do AI Agent Service

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI Agent Service                            │
│                    (FastAPI + Python)                           │
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────────────┐ │
│  │  LLM Orch.    │  │  Vector DB    │  │  Feature Store      │ │
│  │  (Claude/GPT) │  │  (pgvector)   │  │  (Redis)            │ │
│  │               │  │               │  │                     │ │
│  │ - Anthropic   │  │ - Embeddings  │  │ - Cached Features   │ │
│  │ - OpenAI      │  │ - Semantic    │  │ - Model Predictions │ │
│  │ - Fallback    │  │   Search      │  │ - User Preferences  │ │
│  └───────┬───────┘  └───────┬───────┘  └─────────────────────┘ │
│          │                  │                                  │
│          └──────────────────┼─────────────────────────────────┘ │
│                             │                                    │
│  ┌──────────────────────────▼─────────────────────────────────┐ │
│  │                    Agent Orchestrator                       │ │
│  │                                                             │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │ Analyzer │  │ Generator│  │ Scorer   │  │Predictor │  │ │
│  │  │ Agent    │  │ Agent    │  │ Agent    │  │ Agent    │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │ │
│  │                                                             │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                │ │
│  │  │Optimizer │  │Evaluator │  │Researcher│                │ │
│  │  │ Agent    │  │ Agent    │  │ Agent    │                │ │
│  │  └──────────┘  └──────────┘  └──────────┘                │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    ML Models Layer                         │ │
│  │                                                           │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │ │
│  │  │ Price   │  │ CTR     │  │ Lead    │  │ ROI     │     │ │
│  │  │ Model   │  │ Model   │  │ Score   │  │ Model   │     │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Componentes dos Agentes

### 2.1 Analyzer Agent

**Responsabilidade**: Analisar veículos e extrair insights

**Funções**:
- Extrair características do veículo
- Identificar features únicas
- Comparar com mercado
- Detectar anomalias
- Gerar score de atratividade

**Entrada**:
```json
{
  "vehicle": {
    "brand": "Honda",
    "model": "Civic",
    "year": 2024,
    "price": 135000,
    "mileage": 15000,
    "features": {...}
  },
  "market_data": {
    "avg_price": 142000,
    "competitor_count": 12
  }
}
```

**Saída**:
```json
{
  "score": 85,
  "price_analysis": {
    "position": "below_market",
    "discount_percent": 4.9,
    "score": 85
  },
  "selling_points": [
    "Único dono",
    "Baixa quilometragem"
  ],
  "target_audience": [
    "Famílias",
    "Profissionais liberais"
  ],
  "anomalies": [],
  "suggested_improvements": [
    "Adicionar vídeo",
    "Mais fotos do interior"
  ]
}
```

---

### 2.2 Generator Agent

**Responsabilidade**: Gerar conteúdo de anúncios

**Funções**:
- Gerar headlines persuasivas
- Criar descriptions atrativas
- Produzir CTAs eficazes
- Sugerir segmentações
- Recomendar orçamentos

**Entrada**:
```json
{
  "vehicle": {...},
  "target_audience": ["familias", "profissionais"],
  "platform": "facebook",
  "tone": "professional",
  "max_headlines": 3
}
```

**Saída**:
```json
{
  "headlines": [
    {
      "text": "Honda Civic Touring 2024 - Único Dono - Impecável",
      "score": 0.92
    }
  ],
  "descriptions": [...],
  "call_to_actions": [...],
  "targeting_suggestions": {...},
  "budget_recommendation": {...}
}
```

---

### 2.3 Scorer Agent

**Responsabilidade**: Calcular scores e rankings

**Funções**:
- Analisar preço vs mercado
- Score de atratividade (0-100)
- Potencial de conversão
- Priorizar sugestões
- Ranking de melhorias

**Modelos**:
- Price Score Model (XGBoost)
- Attractiveness Score (Ensemble)
- Conversion Potential (Logistic Regression)

---

### 2.4 Predictor Agent

**Responsabilidade**: Prever performance de campanhas

**Funções**:
- Prever CTR estimado
- Estimar conversão
- Projetar ROI
- Recomendar orçamento
- Calcular alcance

**Features**:
```json
{
  "vehicle_features": {
    "price": 135000,
    "year": 2024,
    "mileage": 15000,
    "brand_score": 0.85
  },
  "ad_features": {
    "headline_score": 0.92,
    "image_quality": 0.88,
    "targeting_precision": 0.75
  },
  "market_features": {
    "demand_index": 0.78,
    "competition_level": 0.65,
    "seasonality": 1.1
  },
  "historical_performance": {
    "avg_ctr": 0.035,
    "avg_conversion": 0.028
  }
}
```

**Saída**:
```json
{
  "ctr": {
    "min": 0.030,
    "avg": 0.035,
    "max": 0.041,
    "confidence": 0.85
  },
  "conversions": {
    "min": 35,
    "avg": 45,
    "max": 55,
    "confidence": 0.82
  },
  "roi": {
    "min": 25.5,
    "avg": 30.2,
    "max": 35.8
  }
}
```

---

### 2.5 Optimizer Agent

**Responsabilidade**: Otimizar anúncios existentes

**Funções**:
- Análise de performance atual
- Identificar oportunidades
- Sugerir mudanças (criativo, targeting, orçamento)
- A/B testing suggestions
- Implementar otimizações automáticas

**Processo**:
```
1. Coletar métricas do anúncio
2. Comparar com benchmarks
3. Identificar gaps
4. Gerar sugestões de melhoria
5. Priorizar por impacto esperado
6. Implementar (se auto-optimization ativado)
```

---

### 2.6 Evaluator Agent

**Responsabilidade**: Avaliar qualidade de conteúdo

**Funções**:
- Score de headlines
- Análise de sentimento
- Verificação de conformidade
- Detecção de problemas
- Sugestões de refinamento

---

### 2.7 Researcher Agent

**Responsabilidade**: Pesquisa de mercado e tendências

**Funções**:
- Análise de concorrência
- Tendências de mercado
- Preços médios por região
- Insights sazonais
- Recomendações de timing

---

## 3. Prompt Templates

### 3.1 Vehicle Analysis Prompt

```markdown
You are an expert automotive market analyst with 20 years of experience in the Brazilian used car market.

Analyze the following vehicle and provide comprehensive insights:

**Vehicle Details:**
- Brand: {brand}
- Model: {model}
- Year: {year}
- Model Year: {model_year}
- Version: {version}
- Price: R$ {price}
- Mileage: {mileage} km
- Color: {color}
- Fuel Type: {fuel_type}
- Transmission: {transmission}
- Body Type: {body_type}
- Features: {features}

**Market Context:**
- Average Market Price: R$ {market_avg_price}
- Price Range: R$ {market_min} - R$ {market_max}
- Competitor Count: {competitor_count}
- Location: {city}, {state}

**Analysis Required:**

1. **Price Analysis** (0-100 points):
   - Current price vs market average
   - Price position (below/fair/above market)
   - Discount percentage (if below market)
   - Price score (0-100)

2. **Selling Points** (list 3-5 key points):
   - Unique features
   - Competitive advantages
   - Value propositions
   - Emotional triggers

3. **Target Audience** (list 2-3 segments):
   - Demographics
   - Psychographics
   - Buying behaviors
   - Pain points addressed

4. **Suggested Improvements** (list 2-4 items):
   - Missing information
   - Better photos needed
   - Additional features to highlight
   - Documentation improvements

5. **Performance Prediction**:
   - Estimated CTR (min/avg/max)
   - Estimated conversion rate (min/avg/max)
   - Estimated cost per lead (R$)
   - Confidence level (0-1)

6. **Competitor Analysis**:
   - Competitive position
   - Market differentiation
   - Threats and opportunities

**Response Format (JSON):**
```json
{
  "score": 85,
  "price_analysis": {
    "current_price": 135000,
    "market_range": {"min": 130000, "avg": 140000, "max": 145000},
    "position": "below_market",
    "score": 85,
    "discount_percent": 3.57
  },
  "selling_points": [
    "Único dono",
    "Todas revisões na concessionária",
    "Baixa quilometragem (15.000 km)",
    "Garantia de fábrica vigente"
  ],
  "target_audience": [
    {
      "segment": "Famílias de classe média/alta",
      "demographics": "28-55 anos, renda A/B",
      "psychographics": "Valorizam segurança, conforto e confiabilidade",
      "pain_points": "Precisam de carro confiável para família"
    }
  ],
  "suggested_improvements": [
    "Adicionar vídeo walkaround do veículo",
    "Mais fotos do interior (painel, bancos, porta-malas)",
    "Destacar itens de série na descrição",
    "Incluir informações sobre garantia restante"
  ],
  "performance_prediction": {
    "ctr": {"min": 0.030, "avg": 0.035, "max": 0.041, "confidence": 0.85},
    "conversion_rate": {"min": 0.025, "avg": 0.028, "max": 0.032, "confidence": 0.82},
    "cost_per_lead": {"min": 4.00, "avg": 4.50, "max": 5.20}
  },
  "competitor_analysis": {
    "avg_price": 142000,
    "price_difference": -7000,
    "competitor_count": 12,
    "position": "top_3"
  }
}
```

Provide the analysis in Portuguese (Brazil), using professional but accessible language. Be specific and actionable.
```

---

### 3.2 Ad Content Generation Prompt

```markdown
You are a world-class copywriter specializing in automotive advertising, with expertise in creating high-converting ads for Facebook, Instagram, and Google.

Create compelling ad content for the following vehicle:

**Vehicle Details:**
{vehicle_details}

**Target Audience:**
{target_audience}

**Platform:** {platform}
**Tone:** {tone}

**Requirements:**

1. **Headlines** ({max_headlines} options):
   - Maximum character limit: {headline_char_limit}
   - Must include key selling points
   - Create urgency or curiosity
   - Include brand + model when possible
   - Score each headline (0-1)

2. **Descriptions** ({max_descriptions} options):
   - Maximum character limit: {description_char_limit}
   - Focus on benefits, not just features
   - Include social proof (if applicable)
   - Clear call-to-action
   - Portuguese grammar perfect
   - Score each description (0-1)

3. **Call-to-Actions** (3-5 options):
   - Action-oriented verbs
   - Clear and direct
   - Platform-appropriate

4. **Targeting Suggestions:**
   - Age range (with rationale)
   - Gender (if applicable)
   - Locations (radius + cities)
   - Interests (5-7 relevant)
   - Behaviors (3-5 relevant)

5. **Budget Recommendation:**
   - Daily minimum
   - Daily recommended
   - Daily maximum
   - Estimated reach
   - Rationale

**Response Format (JSON):**
```json
{
  "headlines": [
    {
      "text": "Honda Civic Touring 2024 - Único Dono - Impecável",
      "character_count": 56,
      "score": 0.92,
      "rationale": "Inclui modelo, ano, diferencial e condição"
    }
  ],
  "descriptions": [
    {
      "text": "Honda Civic Touring 2024/2024, único dono...",
      "character_count": 228,
      "score": 0.90
    }
  ],
  "call_to_actions": [
    "Agendar Test-Drive",
    "Saber Mais",
    "Ver Detalhes"
  ],
  "targeting_suggestions": {
    "age_range": {
      "min": 28,
      "max": 55,
      "rationale": "Poder aquisitivo compatível"
    },
    "genders": ["male", "female"],
    "locations": [
      {
        "city": "São Paulo",
        "radius": 30,
        "rationale": "Área de cobertura"
      }
    ],
    "interests": [
      "Automotive",
      "Honda",
      "New cars",
      "Compact cars"
    ],
    "behaviors": [
      "Car buyers (recent)",
      "Luxury shoppers"
    ]
  },
  "budget_recommendation": {
    "daily_min": 100.00,
    "daily_recommended": 150.00,
    "daily_max": 200.00,
    "estimated_reach": {
      "min": 30000,
      "avg": 45000,
      "max": 60000
    },
    "rationale": "Para atingir 40-60K pessoas no público-alvo"
  }
}
```

Create content that converts. Be persuasive but honest. Focus on value proposition.
```

---

### 3.3 Ad Optimization Prompt

```markdown
You are an expert digital marketing analyst specializing in paid advertising optimization.

Analyze the following ad's performance and provide optimization recommendations:

**Current Ad Details:**
- Ad ID: {ad_id}
- Platform: {platform}
- Status: {status}
- Created: {created_at}

**Current Content:**
- Headline: {headline}
- Description: {description}
- CTA: {cta}

**Current Targeting:**
{targeting}

**Current Performance (last 30 days):**
- Impressions: {impressions}
- Clicks: {clicks}
- CTR: {ctr}
- Spend: R$ {spend}
- Conversions: {conversions}
- Conversion Rate: {conversion_rate}
- Cost per Conversion: R$ {cost_per_conversion}
- ROI: {roi}

**Benchmark Performance:**
- Average CTR: {benchmark_ctr}
- Average Conversion: {benchmark_conversion}
- Average CPC: {benchmark_cpc}

**Analysis Required:**

1. **Performance Assessment**:
   - Overall score (0-100)
   - Above/below benchmarks
   - Key issues identified

2. **Optimization Opportunities** (prioritized by impact):
   - Creative improvements (headline, image, copy)
   - Targeting refinements
   - Bid/budget adjustments
   - Landing page optimizations

3. **Specific Recommendations**:
   - For each opportunity: current state → suggested state
   - Expected improvement (percentage)
   - Confidence level (0-1)
   - Priority (high/medium/low)

4. **A/B Testing Ideas** (2-3 variants):
   - What to test
   - Variants to create
   - Success metrics

**Response Format (JSON):**
```json
{
  "current_performance": {
    "overall_score": 72,
    "ctr_vs_benchmark": "below",
    "conversion_vs_benchmark": "below",
    "key_issues": ["low_ctr", "high_cost_per_conversion"]
  },
  "optimizations": [
    {
      "type": "creative",
      "priority": "high",
      "component": "headline",
      "current": "Honda Civic 2024",
      "suggestion": "Honda Civic Touring 2024 - Único Dono - Impecável",
      "expected_improvement": "+15% CTR",
      "confidence": 0.85,
      "rationale": "Headline atual genérico, falta diferenciais"
    }
  ],
  "ab_tests": [
    {
      "test_name": "Headline Test",
      "variants": [
        "Variant A: Current",
        "Variant B: Benefit-focused",
        "Variant C: Urgency-focused"
      ],
      "success_metric": "CTR",
      "duration_days": 7,
      "min_sample_size": 1000
    }
  ],
  "overall_potential_improvement": "+25% ROI"
}
```

Be specific, data-driven, and actionable. Prioritize quick wins first.
```

---

### 3.4 Performance Prediction Prompt

```markdown
You are a machine learning prediction system for automotive advertising performance.

Predict the performance for a campaign with the following parameters:

**Vehicle:**
{vehicle_details}

**Ad Content:**
{ad_content}

**Targeting:**
{targeting}

**Campaign Parameters:**
- Platform: {platform}
- Daily Budget: R$ {budget_daily}
- Duration: {duration_days} days
- Total Budget: R$ {budget_total}

**Historical Data:**
{historical_performance}

**Predictions Required:**

1. **Reach & Impressions:**
   - Total impressions (min/avg/max)
   - Unique reach
   - Frequency

2. **Engagement:**
   - CTR (min/avg/max)
   - Total clicks
   - CPC

3. **Conversions:**
   - Conversion rate (min/avg/max)
   - Total conversions
   - Cost per conversion

4. **ROI:**
   - Estimated revenue
   - ROI (min/avg/max)
   - ROAS

5. **Confidence:** (0-1) for each prediction

**Response Format (JSON):**
```json
{
  "predictions": {
    "impressions": {
      "min": 1200000,
      "avg": 1500000,
      "max": 1800000,
      "confidence": 0.88
    },
    "reach": {
      "min": 450000,
      "avg": 525000,
      "max": 600000
    },
    "clicks": {
      "min": 42000,
      "avg": 52500,
      "max": 63000
    },
    "ctr": {
      "min": 0.030,
      "avg": 0.035,
      "max": 0.040,
      "confidence": 0.85
    },
    "conversions": {
      "min": 1050,
      "avg": 1312,
      "max": 1575,
      "confidence": 0.82
    },
    "conversion_rate": {
      "min": 0.025,
      "avg": 0.028,
      "max": 0.032
    },
    "cost_per_click": {
      "min": 0.08,
      "avg": 0.09,
      "max": 0.10
    },
    "cost_per_conversion": {
      "min": 2.86,
      "avg": 3.43,
      "max": 4.29
    },
    "roi": {
      "min": 25.5,
      "avg": 30.2,
      "max": 35.8,
      "confidence": 0.80
    }
  },
  "assumptions": [
    "Average market demand",
    "No seasonality effects",
    "Competitive bid strategy"
  ],
  "sensitivity_analysis": {
    "budget_increase_20_percent": "+18% conversions",
    "budget_decrease_20_percent": "-15% conversions"
  }
}
```

Provide realistic predictions with appropriate confidence intervals. Be conservative rather than overpromising.
```

---

## 4. Modelos de Machine Learning

### 4.1 Price Scoring Model (XGBoost)

**Objetivo**: Predizer score de preço (0-100)

**Features**:
```python
features = {
    # Vehicle features
    'price': 135000,
    'year': 2024,
    'mileage': 15000,
    'brand_score': 0.85,  # Calculated from historical data
    'model_score': 0.78,
    'price_market': 140000,
    'price_diff_percent': -3.57,
    'price_vs_market': 0.964,  # price / market_price

    # Market features
    'demand_index': 0.78,
    'supply_index': 0.65,
    'competition_level': 0.72,

    # Condition features
    'owner_count': 1,
    'accident_free': 1,
    'service_history': 1,
    'warranty_remaining': 12,  # months

    # Location features
    'location_price_index': 1.05,
    'location_demand': 0.82
}
```

**Target**: `price_score` (0-100)

**Model**: XGBoost Regressor
```python
model = xgb.XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
```

---

### 4.2 CTR Prediction Model (Neural Network)

**Objetivo**: Predizer CTR esperado

**Features**:
```python
features = {
    # Ad content features
    'headline_length': 56,
    'headline_score': 0.92,
    'description_length': 228,
    'description_score': 0.90,
    'has_price': 1,
    'has_year': 1,
    'has_urgency': 0,
    'emotional_score': 0.75,

    # Image features
    'image_quality_score': 0.88,
    'image_count': 3,
    'has_interior_photo': 1,
    'has_exterior_photo': 1,

    # Vehicle features
    'price': 135000,
    'price_score': 85,
    'brand_popularity': 0.85,
    'model_demand': 0.78,

    # Targeting features
    'audience_size': 45000,
    'targeting_precision': 0.75,
    'age_range_width': 27,
    'location_radius': 30,

    # Historical features
    'historical_ctr': 0.035,
    'similar_ads_ctr': 0.033,

    # Platform features
    'platform_facebook': 1,
    'platform_instagram': 0,
    'platform_google': 0
}
```

**Target**: `ctr` (0.0 - 1.0)

**Model**: Neural Network (TensorFlow/Keras)
```python
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(n_features,)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='mean_squared_error',
    metrics=['mae']
)
```

---

### 4.3 Conversion Rate Model (Logistic Regression)

**Objetivo**: Predizer taxa de conversão

**Features**:
```python
features = {
    # Lead quality features
    'lead_score': 0.75,
    'price_affordability': 0.82,
    'financing_available': 1,

    # Vehicle attractiveness
    'vehicle_score': 85,
    'price_competitiveness': 1,  # below market

    # Ad relevance
    'ctr': 0.035,
    'click_to_lead_conversion_historical': 0.28,

    # Dealer features
    'dealer_rating': 4.5,
    'response_time_avg': 15,  # minutes
    'has_online_scheduling': 1
}
```

**Target**: `conversion_rate` (0.0 - 1.0)

**Model**: Logistic Regression
```python
model = LogisticRegression(
    penalty='l2',
    C=1.0,
    random_state=42
)
```

---

### 4.4 ROI Prediction Model (Gradient Boosting)

**Objetivo**: Predizer ROI da campanha

**Features**: Todas as features acima + mais contextuais

**Model**: XGBoost ou LightGBM

---

## 5. Feature Store (Redis)

### Estrutura de Features

```python
# Vehicle Features
feature_store.set(
    key=f"vehicle:{vehicle_id}:features",
    value={
        'price_score': 85,
        'brand_score': 0.85,
        'model_score': 0.78,
        'demand_index': 0.78,
        'last_updated': '2026-03-17T10:00:00Z'
    },
    ttl=86400  # 24 hours
)

# User Preferences
feature_store.set(
    key=f"dealership:{dealership_id}:preferences",
    value={
        'preferred_platforms': ['facebook', 'instagram'],
        'avg_budget_daily': 150,
        'target_audience_segments': ['familias'],
        'last_updated': '2026-03-17T10:00:00Z'
    },
    ttl=604800  # 7 days
)

# Model Predictions (Cache)
feature_store.set(
    key=f"prediction:{model_name}:{vehicle_id}:{hash(features)}",
    value={
        'ctr_pred': 0.035,
        'conversion_pred': 0.028,
        'roi_pred': 30.2,
        'confidence': 0.85,
        'model_version': 'v1.2.0'
    },
    ttl=3600  # 1 hour
)
```

---

## 6. Vector Store (pgvector)

### Armazenamento de Embeddings

```sql
-- Criar tabela para embeddings
CREATE TABLE vehicle_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID REFERENCES vehicles(id),
    embedding vector(1536),  -- OpenAI embedding dimension
    embedding_model VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Criar índice para busca semântica
CREATE INDEX idx_vehicle_embeddings_embedding
ON vehicle_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Busca Semântica

```sql
-- Encontrar veículos similares
SELECT
    v.id,
    v.title,
    v.brand,
    v.model,
    v.price,
    1 - (e.embedding <=> $1) as similarity
FROM vehicle_embeddings e
JOIN vehicles v ON e.vehicle_id = v.id
WHERE e.embedding <=> $1 < 0.2  -- Cosine distance threshold
ORDER BY e.embedding <=> $1
LIMIT 10;
```

---

## 7. Pipeline de ML

### Training Pipeline

```python
# 1. Data Collection
def collect_training_data():
    # Historical ads data
    # Vehicle data
    # Market data
    # Performance metrics
    return df

# 2. Feature Engineering
def engineer_features(df):
    # Create features
    # Handle missing values
    # Encode categoricals
    # Scale numericals
    return X, y

# 3. Model Training
def train_model(X, y, model_type):
    if model_type == 'xgboost':
        model = train_xgboost(X, y)
    elif model_type == 'neural_network':
        model = train_nn(X, y)
    # Save model
    return model

# 4. Evaluation
def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    metrics = {
        'mae': mean_absolute_error(y_test, predictions),
        'rmse': sqrt(mean_squared_error(y_test, predictions)),
        'r2': r2_score(y_test, predictions)
    }
    return metrics

# 5. Deployment
def deploy_model(model, model_name):
    # Save to model registry
    # Update API endpoint
    # Monitor performance
    pass
```

---

## 8. Monitoramento de Modelos

### Métricas de Monitoramento

```python
# Model Performance Metrics
metrics = {
    'prediction_accuracy': 0.85,
    'mae': 0.023,
    'rmse': 0.031,
    'drift_detected': False,

    # Feature Importance
    'feature_importance': {
        'price_score': 0.25,
        'headline_score': 0.20,
        'brand_popularity': 0.15,
        # ...
    },

    # Data Drift
    'feature_drift': {
        'price_distribution': 0.03,  # KL divergence
        'audience_size': 0.05
    }
}
```

### Retraining Trigger

- Automatic: Weekly if drift > threshold
- Manual: Admin triggered
- Continuous: Online learning (future)

---

## 9. Exemplos de Uso

### Exemplo 1: Análise Completa de Veículo

```python
from ai_service import AnalyzerAgent, ScorerAgent

# Analyze vehicle
analyzer = AnalyzerAgent()
analysis = await analyzer.analyze_vehicle(
    vehicle_id="uuid",
    include_market_data=True,
    include_competitor_analysis=True
)

# Score vehicle
scorer = ScorerAgent()
score = await scorer.score_vehicle(
    vehicle_id="uuid",
    analysis=analysis
)

# Results
print(f"Score: {score.total_score}")
print(f"Price Position: {analysis.price_analysis.position}")
print(f"Target Audience: {analysis.target_audience}")
```

### Exemplo 2: Geração de Anúncio

```python
from ai_service import GeneratorAgent

generator = GeneratorAgent()

ad_content = await generator.generate_ad(
    vehicle_id="uuid",
    platform="facebook",
    target_audience=["familias", "profissionais"],
    tone="professional",
    max_headlines=3,
    max_descriptions=2
)

# Select best headline
best_headline = max(ad_content.headlines, key=lambda x: x.score)
print(f"Best Headline: {best_headline.text}")
print(f"Score: {best_headline.score}")
```

### Exemplo 3: Previsão de Performance

```python
from ai_service import PredictorAgent

predictor = PredictorAgent()

predictions = await predictor.predict_performance(
    vehicle_id="uuid",
    ad_content=ad_content,
    targeting=targeting,
    platform="facebook",
    budget_daily=150,
    duration_days=30
)

print(f"Expected CTR: {predictions.ctr.avg}")
print(f"Expected Conversions: {predictions.conversions.avg}")
print(f"Expected ROI: {predictions.roi.avg}")
```

---

## 10. Próximos Passos

1. ✅ Estrutura do AI Agent definida
2. ⏳ Implementar Agent Orchestrator
3. ⏳ Criar prompt templates
4. ⏳ Treinar modelos de ML
5. ⏳ Implementar Feature Store
6. ⏳ Setup Vector Store com pgvector
7. ⏳ Criar pipeline de treinamento
8. ⏳ Implementar monitoramento de modelos
9. ⏳ Testes A/B de predictions
10. ⏳ Documentação e tutoriais
