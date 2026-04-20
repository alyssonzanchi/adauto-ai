# Semana 7: ML Models - Modelos de Machine Learning

## 📋 Visão Geral

**Status**: ⏳ Planejamento (Início: 20/04/2026)
**Duração Estimada**: 7-10 dias
**Fase**: Fase 2 - AI Agent Service (Semanas 5-8)

---

## 🎯 Objetivos da Semana 7

Implementar modelos de Machine Learning para previsões de preço, CTR e conversão, complementando o sistema de IA baseado em LLMs.

### Objetivos Específicos:

1. **Price Scoring Model (XGBoost)**
   - Prever preço justo de mercado
   - Score de competitividade
   - Feature engineering avançado

2. **CTR Prediction Model**
   - Prever click-through rate
   - Features de anúncios
   - Histórico de performance

3. **Conversion Rate Model**
   - Prever taxa de conversão
   - Features de leads
   - Análise de intenção

4. **Training Pipeline**
   - Coleta e preparação de dados
   - Feature engineering
   - Treinamento e validação
   - Deploy de modelos

---

## 📁 Estrutura de Arquivos

### Novos Diretórios

```
backend/
├── app/services/ml/
│   ├── __init__.py
│   ├── base_model.py              # BaseModel class
│   ├── price_model.py             # XGBoost Price Model
│   ├── ctr_model.py               # CTR Prediction
│   ├── conversion_model.py        # Conversion Prediction
│   ├── feature_engineering.py     # Feature extraction
│   └── model_registry.py          # Model versioning
│
├── app/ml/
│   ├── __init__.py
│   ├── training/
│   │   ├── __init__.py
│   │   ├── data_loader.py         # Load training data
│   │   ├── preprocessor.py        # Data preprocessing
│   │   ├── trainer.py             # Training pipeline
│   │   └── evaluator.py           # Model evaluation
│   ├── features/
│   │   ├── __init__.py
│   │   ├── vehicle_features.py    # Vehicle features
│   │   ├── market_features.py     # Market features
│   │   ├── temporal_features.py   # Time-based features
│   │   └── interaction_features.py # User interaction features
│   └── models/
│       ├── __init__.py
│       ├── price_predictor.pkl    # Trained models
│       ├── ctr_predictor.pkl
│       └── conversion_predictor.pkl
│
├── scripts/ml/
│   ├── train_models.py            # Training script
│   ├── evaluate_models.py         # Evaluation script
│   ├── generate_features.py       # Feature generation
│   └── batch_predict.py           # Batch prediction
│
└── tests/services/ml/
    ├── test_price_model.py
    ├── test_ctr_model.py
    ├── test_conversion_model.py
    └── test_feature_engineering.py
```

---

## 🔧 Componentes a Implementar

### 1. Feature Engineering

#### Vehicle Features (`app/ml/features/vehicle_features.py`)

**Features Principais:**
- **Básicas**: brand, model, year, mileage, color
- **Técnicas**: transmission, fuel_type, body_type, doors, engine
- **Conforto**: air_conditioning, power_windows, central_locking
- **Segurança**: airbags, abs, esp, rear_camera
- **Tecnologia**: bluetooth, usb, android_auto, apple_carplay
- **Mercado**: price, price_per_km, depreciation_rate, days_on_market

**Features Derivadas:**
```python
- age_months = current_date - model_year
- mileage_per_year = mileage / age_months * 12
- price_position = price / median_price(model, year)
- rarity_score = 1 / count_similar_vehicles
- feature_score = count(features) / max_features
```

#### Market Features (`app/ml/features/market_features.py`)

**Features de Mercado:**
- **Demanda**: search_volume(model), view_count(model)
- **Oferta**: inventory_count(model), new_listings(model)
- **Sazonalidade**: month, quarter, is_holiday_season
- **Tendências**: price_change_30d, price_change_90d
- **Geografia**: region_price_index, demand_by_state

#### Temporal Features (`app/ml/features/temporal_features.py`)

**Features Temporais:**
- **Data**: day_of_week, day_of_month, month, quarter
- **Sazonalidade**: is_summer, is_winter, is_year_end
- **Ciclos**: days_since_listing, weekend_boost

### 2. Price Scoring Model (XGBoost)

**Arquivo**: `app/services/ml/price_model.py`

**Target Variables:**
- `fair_market_price` (regressão)
- `price_score` (classificação: 0-100)
- `price_position` (classificação: great_deal, good_price, fair_price, overpriced)

**Features:**
- 50+ features de veículo
- 20+ features de mercado
- 10+ features temporais
- Total: ~80 features

**Model**: XGBoost Regressor + Classifier

**Métricas:**
- MAE < R$ 5.000
- RMSE < R$ 8.000
- R² > 0.85
- Accuracy (position) > 80%

### 3. CTR Prediction Model

**Arquivo**: `app/services/ml/ctr_model.py`

**Target Variables:**
- `predicted_ctr` (regressão: 0-1)
- `ctr_bucket` (classificação: very_low, low, medium, high, very_high)

**Features:**
- **Anúncio**: headline_quality, description_quality, image_count, image_quality
- **Veículo**: price_position, rarity_score, feature_score
- **Mercado**: demand_score, supply_score, seasonality
- **Histórico**: avg_ctr_brand, avg_ctr_model, avg_ctr_similar

**Model**: Neural Network (MLP) ou XGBoost

**Métricas:**
- MAE < 0.02
- RMSE < 0.03
- R² > 0.70

### 4. Conversion Rate Model

**Arquivo**: `app/services/ml/conversion_model.py`

**Target Variables:**
- `predicted_conversion_rate` (regressão: 0-1)
- `lead_quality_score` (regressão: 0-100)
- `conversion_probability` (classificação: low, medium, high)

**Features:**
- **Veículo**: price_position, condition_score, mileage_score
- **Anúncio**: ctr, views, engagement_rate
- **Lead**: lead_source, lead_type, device_type
- **Contexto**: time_of_day, day_of_week, season

**Model**: XGBoost Classifier + Regressor

**Métricas:**
- AUC-ROC > 0.75
- Precision > 0.70
- Recall > 0.60

---

## 🔄 Training Pipeline

### 1. Data Collection

**Fontes de Dados:**
- **Vehicles table**: Dados de veículos
- **Ads table**: Dados de anúncios
- **Metrics table**: Métricas históricas
- **Leads table**: Dados de leads
- **External APIs**: Fipe, Mercado Livre, Webmotors

**Coleta:**
```python
# scripts/ml/collect_training_data.py
# Exporta dados para CSV/Parquet
# Features + labels
```

### 2. Data Preprocessing

**Passos:**
1. Limpeza de dados (missing values, outliers)
2. Encoding de variáveis categóricas
3. Feature scaling (StandardScaler)
4. Train/test split (80/20)
5. Cross-validation (5-fold)

### 3. Training

**Hyperparameter Tuning:**
```python
# XGBoost params
{
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.05, 0.1],
    'subsample': [0.8, 0.9, 1.0],
    'colsample_bytree': [0.8, 0.9, 1.0]
}
```

**Training Script:**
```bash
python scripts/ml/train_models.py \
    --model price \
    --data data/training_data.csv \
    --output models/price_predictor.pkl \
    --eval
```

### 4. Evaluation

**Métricas:**
- Regression: MAE, RMSE, R², MAPE
- Classification: Accuracy, Precision, Recall, F1, AUC-ROC
- Business: lift, gain chart, calibration

**Validation:**
- Time-based split (validar com dados recentes)
- Cross-validation
- Holdout set (últimos 30 dias)

### 5. Model Registry

**Versionamento:**
```python
# app/services/ml/model_registry.py
class ModelRegistry:
    def save_model(model, metadata)
    def load_model(model_name, version)
    def get_model_info(model_name)
    def list_models()
```

**Metadata:**
```json
{
    "model_name": "price_predictor",
    "version": "1.0.0",
    "trained_at": "2026-04-20",
    "features": ["brand", "model", "year", ...],
    "metrics": {"mae": 4200, "r2": 0.87},
    "params": {"n_estimators": 200, ...}
}
```

---

## 🔌 API Integration

### Endpoints ML

#### POST `/api/v1/ml/predict-price`
```json
{
    "vehicle_data": {
        "brand": "Honda",
        "model": "Civic",
        "year": 2021,
        "mileage": 25000,
        ...
    }
}

Response:
{
    "predicted_price": 138500.00,
    "price_range": [132000, 145000],
    "confidence": 0.87,
    "score": 85,
    "position": "good_price"
}
```

#### POST `/api/v1/ml/predict-ctr`
```json
{
    "vehicle_id": "uuid",
    "ad_content": {...}
}

Response:
{
    "predicted_ctr": 0.045,
    "ctr_bucket": "high",
    "confidence": 0.76,
    "optimization_suggestions": [
        "improve_headline",
        "add_more_images"
    ]
}
```

#### POST `/api/v1/ml/predict-conversion`
```json
{
    "vehicle_id": "uuid",
    "lead_data": {...}
}

Response:
{
    "predicted_conversion_rate": 0.028,
    "conversion_probability": "high",
    "confidence": 0.82,
    "lead_quality_score": 75
}
```

### Integration com AI Service

**Agent Orchestrator Update:**
```python
# app/services/ai/orchestrator.py

class AgentOrchestrator:
    def __init__(self):
        # ... existing code
        self.price_model = PriceModel()
        self.ctr_model = CTRModel()
        self.conversion_model = ConversionModel()

    async def analyze_vehicle(self, vehicle_data):
        # ML prediction
        ml_price = await self.price_model.predict(vehicle_data)

        # LLM analysis
        llm_analysis = await self.analyzer_agent.analyze(vehicle_data)

        # Combine results
        return {
            "ml_prediction": ml_price,
            "llm_analysis": llm_analysis,
            "combined_score": self._combine_scores(ml_price, llm_analysis)
        }
```

---

## 📊 Dependências

### Pacotes Python

**requirements.txt (adicionar):**
```txt
# Machine Learning
xgboost==2.0.3              # Gradient boosting
scikit-learn==1.3.2         # ML utilities
numpy==1.24.3               # Numerical computing
pandas==2.0.3               # Data manipulation
joblib==1.3.2               # Model persistence

# Feature Engineering
featuretools==1.30.0        # Automated feature engineering
category-encoders==2.6.3    # Categorical encoding

# Deep Learning (opcional)
tensorflow==2.15.0          # Neural networks
# ou
torch==2.1.0                # PyTorch

# Model Monitoring
evidently==0.4.5            # Model monitoring
mlflow==2.9.0               # Experiment tracking
```

---

## 📈 Plano de Implementação

### Dia 1-2: Feature Engineering
- [ ] Criar estrutura de diretórios ML
- [ ] Implementar `vehicle_features.py`
- [ ] Implementar `market_features.py`
- [ ] Implementar `temporal_features.py`
- [ ] Testes de features

### Dia 3-4: Price Model
- [ ] Implementar `price_model.py`
- [ ] Criar dataset de treinamento
- [ ] Treinar modelo XGBoost
- [ ] Avaliar performance
- [ ] Deploy e testes

### Dia 5-6: CTR & Conversion Models
- [ ] Implementar `ctr_model.py`
- [ ] Implementar `conversion_model.py`
- [ ] Criar datasets de treinamento
- [ ] Treinar modelos
- [ ] Avaliar performance

### Dia 7: Training Pipeline
- [ ] Implementar `training/trainer.py`
- [ ] Implementar `training/evaluator.py`
- [ ] Criar scripts de treinamento
- [ ] Automatizar pipeline

### Dia 8-9: API Integration
- [ ] Criar endpoints ML
- [ ] Integrar com AI Orchestrator
- [ ] Testes E2E
- [ ] Documentação

### Dia 10: Validation & Documentation
- [ ] Testes completos
- [ ] Validação de performance
- [ ] Documentação
- [ ] Guia de operação

---

## 🧪 Testes

### Unit Tests
```python
# tests/services/ml/test_price_model.py
def test_price_model_prediction():
    model = PriceModel()
    result = model.predict(sample_vehicle)
    assert result["predicted_price"] > 0
    assert 0 <= result["score"] <= 100

def test_feature_engineering():
    features = VehicleFeatures().extract(sample_vehicle)
    assert len(features) == 50
    assert "age_months" in features
```

### Integration Tests
```python
# tests/api/test_ml_integration.py
async def test_predict_price_endpoint():
    response = await client.post("/api/v1/ml/predict-price", json=...)
    assert response.status_code == 200
    assert "predicted_price" in response.json()
```

### Performance Tests
- Latência < 100ms por predição
- Batch prediction (100 vehicles) < 5s
- Memory usage < 500MB

---

## 📝 Critérios de Sucesso

### Funcionais
- [ ] Price model com MAE < R$ 5.000
- [ ] CTR model com MAE < 0.02
- [ ] Conversion model com AUC > 0.75
- [ ] Todos modelos treinados e salvos
- [ ] API endpoints funcionando
- [ ] Integração com AI service

### Performance
- [ ] Predição < 100ms (p95)
- [ ] Batch prediction < 5s (100 vehicles)
- [ ] Cache hit rate > 70%

### Qualidade
- [ ] Test coverage > 80%
- [ ] Documentação completa
- [ ] Monitoramento configurado
- [ ] Model registry funcional

---

## 🚀 Scripts Utilitários

### Treinar Modelos
```bash
# Treinar todos os modelos
python scripts/ml/train_models.py --all

# Treinar modelo específico
python scripts/ml/train_models.py --model price --data data.csv

# Com hyperparameter tuning
python scripts/ml/train_models.py --model price --tune
```

### Gerar Features
```bash
# Gerar features para todos os veículos
python scripts/ml/generate_features.py --all

# Gerar features para veículo específico
python scripts/ml/generate_features.py --vehicle-id uuid
```

### Batch Prediction
```bash
# Predizer preço para todos os veículos
python scripts/ml/batch_predict.py --model price

# Exportar resultados
python scripts/ml/batch_predict.py --model price --output predictions.csv
```

---

## 💰 Custos

### Treinamento
- **Dados**: 1.000-10.000 vehicles (synthetic ou real)
- **Tempo**: 30min - 2h por modelo
- **Compute**: CPU (local) ou GPU (cloud)

### Inferência
- **CPU**: < 100ms por predição
- **Custo**: ~R$0,001 por predição (negligível)

### Armazenamento
- **Modelos**: ~50MB cada
- **Features**: ~1MB por vehicle
- **Total**: < 1GB

---

## 🔄 Rollback Strategy

### Feature Flags
```python
# app/core/config.py
ENABLE_ML_MODELS: bool = True
USE_ML_PRICE_PREDICTION: bool = True
USE_ML_CTR_PREDICTION: bool = True
USE_ML_CONVERSION_PREDICTION: bool = True
```

### Rollback
```bash
# Desabilitar ML models
ENABLE_ML_MODELS=false

# Usar apenas LLM
# Volta para comportamento da Semana 5
```

---

## 📚 Referências

- **Roadmap**: `docs/referencias/roadmap.md` (Fase 2)
- **AI Service**: `historico/semana5-ai-service/`
- **Database**: `docs/dia2-arquitetura/database-schema.md`

---

## 🎓 Próximos Passos (Semana 8)

### Predictor & Optimizer Agents
- PredictorAgent (performance prediction)
- OptimizerAgent (ad optimization)
- EvaluatorAgent (content quality)
- A/B testing integration

---

**Status da Semana 7**: ⏳ **PLANEJADO**

**Início**: 20/04/2026
**Próxima Fase**: Semana 8 - Predictor & Optimizer Agents
