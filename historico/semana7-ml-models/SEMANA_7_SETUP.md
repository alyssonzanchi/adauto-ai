# Semana 7: ML Models - Setup Guide

## 🚀 Quick Start

### Instalação de Dependências

```bash
cd backend
pip install -r requirements.txt
```

Novos pacotes instalados:
- `xgboost==2.0.3` - Gradient boosting
- `scikit-learn==1.3.2` - ML utilities
- `joblib==1.3.2` - Model persistence
- `featuretools==1.30.0` - Feature engineering
- `category-encoders==2.6.3` - Categorical encoding
- `evidently==0.4.5` - Model monitoring
- `mlflow==2.9.0` - Experiment tracking

### Estrutura de Diretórios

```bash
backend/app/ml/
├── features/          # Feature extraction
├── training/          # Training pipeline
└── models/            # Trained models (.pkl files)

backend/app/services/ml/  # ML models
```

---

## 🧪 Testando a Implementação

### 1. Testar Feature Engineering

```bash
cd backend
PYTHONPATH=/Users/alyssonzanchi/adauto-ai/backend python3 scripts/ml/test_features.py
```

**Saída esperada:**
- 134 features extraídas
- Distribuição por categoria
- Validação OK

### 2. Testar Price Model

```bash
PYTHONPATH=/Users/alyssonzanchi/adauto-ai/backend python3 scripts/ml/test_price_model.py
```

**Saída esperada:**
- Predição de preço
- Score 0-100
- Posicionamento
- Modelo treinado com R² > 0.99

### 3. Testar CTR e Conversion Models

```bash
PYTHONPATH=/Users/alyssonzanchi/adauto-ai/backend python3 scripts/ml/test_ctr_conversion_models.py
```

**Saída esperada:**
- CTR prediction (3-6%)
- Conversion prediction (1-6%)
- Lead quality score
- Integração com Price Model

### 4. Teste Completo

```bash
PYTHONPATH=/Users/alyssonzanchi/adauto-ai/backend python3 scripts/ml/test_semana7_complete.py
```

**Saída esperada:**
- Todas as 6 partes funcionando
- ROI projection
- Recomendações finais

---

## 🤖 Treinando Modelos

### Treinar Price Model (Dados Sintéticos)

```bash
cd backend
PYTHONPATH=/Users/alyssonzanchi/adauto-ai/backend python3 scripts/ml/train_price_model.py \
    --samples 1000 \
    --version 1.0.0 \
    --synthetic
```

**Saída esperada:**
- 1000 synthetic samples gerados
- Train R²: 1.0000
- Test R²: 0.9998
- Test MAE: R$ 126,51
- Modelo salvo em: `backend/app/ml/models/price_predictor_1.0.0.pkl`

### Treinar com Dados Reais (do Database)

```bash
PYTHONPATH=/Users/alyssonzanchi/adauto-ai/backend python3 scripts/ml/train_price_model.py \
    --samples 1000 \
    --version 2.0.0
```

Requer:
- Database PostgreSQL rodando
- Tabela `vehicles` populada

---

## 🔌 API Usage

### Iniciar Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Endpoints Disponíveis

#### 1. Prever Preço

```bash
curl -X POST http://localhost:8000/api/v1/ml/predict-price \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_data": {
      "brand": "Honda",
      "model": "Civic",
      "model_year": 2021,
      "mileage": 25000,
      "price": 138500,
      "transmission": "CVT",
      "fuel_type": "flex",
      "body_type": "sedan",
      "color": "Branco"
    }
  }'
```

#### 2. Prever CTR

```bash
curl -X POST http://localhost:8000/api/v1/ml/predict-ctr \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_data": {...},
    "ad_content": {
      "headline": "Honda Civic 2021 - Impecável!",
      "description": "Único dono, 25.000km...",
      "images": [{"url": "img1.jpg"}],
      "cta": "Entre em contato!"
    }
  }'
```

#### 3. Prever Conversão

```bash
curl -X POST http://localhost:8000/api/v1/ml/predict-conversion \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_data": {...},
    "lead_data": {
      "name": "João Silva",
      "phone": "+55 11 98765-4321",
      "type": "warm",
      "source": "organic",
      "response_time": 15
    }
  }'
```

---

## 📊 Model Registry

### Listar Modelos

```python
from app.services.ml import ModelRegistry

registry = ModelRegistry("backend/app/ml/models")
info = registry.get_registry_info()
print(info)
```

### Carregar Modelo

```python
from app.services.ml import PriceModel

model = PriceModel()
model.load_model("backend/app/ml/models/price_predictor_1.0.0.pkl")
prediction = await model.predict(vehicle_data)
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

No `.env`:

```bash
# ML Configuration
ENABLE_ML_MODELS=true
USE_ML_PRICE_PREDICTION=true
USE_ML_CTR_PREDICTION=true
USE_ML_CONVERSION_PREDICTION=true

# Model Paths
ML_MODEL_PATH=backend/app/ml/models
ML_MODEL_VERSION=1.0.0

# Feature Engineering
VECTOR_DIMENSIONS=1536
FEATURE_CACHE_TTL=3600
```

---

## 🐛 Troubleshooting

### Erro: "Module not found: xgboost"

```bash
pip install xgboost==2.0.3
```

### Erro: "Model file not found"

Treine o modelo primeiro:
```bash
python scripts/ml/train_price_model.py --synthetic
```

### Predição retornando "fallback: true"

Modelo não treinado. Treine ou carregue um modelo treinado.

### Features com valores NaN

Verifique se os dados de entrada estão completos. O pré-processador imputa valores faltantes.

---

## 📈 Performance

### Otimização

1. **Batch Predictions**: Use `predict_batch()` para múltiplas previsões
2. **Model Caching**: Modelos ficam em memória após carregados
3. **Feature Caching**: Features são cacheadas no Redis (TTL: 1h)

### Latência Esperada

- Feature extraction: ~50ms
- Price prediction: ~30ms
- CTR prediction: ~30ms
- Conversion prediction: ~30ms
- **Total**: < 150ms por predição completa

---

## 🧪 Desenvolvimento

### Adicionar Novo Feature Extractor

1. Criar arquivo em `app/ml/features/`
2. Estender lógica de extração
3. Registrar no `FeatureEngineer`

```python
# app/ml/features/custom_features.py
class CustomFeatures:
    def extract(self, data):
        return {"custom_feature": value}

# feature_engineering.py
from .custom_features import CustomFeatures
self.custom_features = CustomFeatures()
```

### Adicionar Novo Modelo

1. Criar modelo em `app/services/ml/`
2. Estender `BaseModel`
3. Implementar `predict()` e `predict_batch()`
4. Adicionar endpoint em `app/api/v1/endpoints/ml.py`

---

## 📞 Suporte

**Dúvidas ou problemas?**
- Logs: `docker-compose logs -f backend`
- Testes: `pytest tests/services/ml/`
- Docs: `historico/semana7-ml-models/`

---

**Status**: ✅ Pronto para produção
**Última atualização**: 20/04/2026
