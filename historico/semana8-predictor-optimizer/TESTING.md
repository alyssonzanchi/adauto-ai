# Semana 8: Predictor & Optimizer Agents - Guia de Testes

## 📋 Visão Geral

Este documento descreve como testar os agentes AI implementados na Semana 8.

---

## 🚀 Teste Rápido (5 min)

### Pré-requisitos

1. Ambiente Python configurado
2. Dependências instaladas
3. Redis rodando (opcional, para cache)

### Executar Teste Completo

```bash
cd backend
PYTHONPATH=. python3 scripts/ai/test_ai_agents.py
```

**Saída esperada:**
```
================================================================================
Teste dos AI Agents - Semana 8: Predictor & Optimizer Agents
================================================================================

📊 PARTE 1: PREDICTOR AGENT (Predição de Performance)
⚡ PARTE 2: OPTIMIZER AGENT (Otimização de Anúncios)
🎯 PARTE 3: EVALUATOR AGENT (Avaliação de Conteúdo)
🤖 PARTE 4: INTEGRAÇÃO COMPLETA (AI Orchestrator)
✅ RESUMO DOS RESULTADOS - SEMANA 8
✅ TODOS OS AGENTES FUNCIONANDO!
================================================================================
```

---

## 🧪 Testes Individuais

### 1. PredictorAgent

**Objetivo:** Testar predição de performance e forecasting

```python
import asyncio
from app.services.ai.agents.predictor import PredictorAgent
from app.services.llm.llm_client import LLMClient

async def test_predictor():
    llm_client = LLMClient()
    predictor = PredictorAgent(llm_client)

    vehicle_data = {
        "id": "test-123",
        "brand": "Honda",
        "model": "Civic Touring",
        "model_year": 2021,
        "mileage": 25000,
        "price": 138500.00,
        "days_since_listing": 37,
        "image_count": 5
    }

    result = await predictor.execute({
        "vehicle_data": vehicle_data,
        "forecast_days": 30,
        "include_scenarios": False
    })

    print(f"CTR Predito: {result['predictions']['ctr']['predicted_ctr']:.2%}")
    print(f"Conversão Predita: {result['predictions']['conversion']['predicted_conversion_rate']:.2%}")
    print(f"Preço Predito: R$ {result['predictions']['price']['predicted_price']:,.2f}")
    print(f"Risco: {result['risk_assessment']['risk_level']}")

asyncio.run(test_predictor())
```

**Validações:**
- ✅ CTR entre 0.01 e 0.10 (1-10%)
- ✅ Conversão entre 0.01 e 0.10 (1-10%)
- ✅ Preço dentro de ±20% do preço original
- ✅ Risco é "low", "medium" ou "high"
- ✅ Forecast tem 30 dias de predições diárias

### 2. OptimizerAgent

**Objetivo:** Testar otimização de anúncios

```python
import asyncio
from app.services.ai.agents.optimizer import OptimizerAgent
from app.services.llm.llm_client import LLMClient

async def test_optimizer():
    llm_client = LLMClient()
    optimizer = OptimizerAgent(llm_client)

    vehicle_data = {
        "brand": "Honda",
        "model": "Civic",
        "price": 138500
    }

    ad_content = {
        "headline": "Honda Civic 2021 - Seminovo",
        "description": "Honda Civic Touring 2021, apenas 25.000km.",
        "images": [{"url": "img1.jpg"}],
        "cta": "Entre em contato"
    }

    result = await optimizer.execute({
        "vehicle_data": vehicle_data,
        "ad_content": ad_content,
        "current_metrics": {"ctr": 0.035, "conversion_rate": 0.025},
        "goals": {"target_ctr": 0.05, "target_conversion": 0.035}
    })

    print(f"Recomendações: {len(result['content_optimization']['recommendations'])}")
    print(f"Bid: R$ {result['bid_recommendations']['recommended_bid']:.2f}")
    print(f"Budget diário: R$ {result['budget_optimization']['optimal_daily_budget']:.2f}")

asyncio.run(test_optimizer())
```

**Validações:**
- ✅ Pelo menos 1 recomendação de conteúdo
- ✅ Bid entre R$ 1.00 e R$ 10.00
- ✅ Budget diário positivo
- ✅ Pelo menos 1 teste A/B sugerido
- ✅ Prioridades ordenadas

### 3. EvaluatorAgent

**Objetivo:** Testar avaliação de conteúdo

```python
import asyncio
from app.services.ai.agents.evaluator import EvaluatorAgent
from app.services.llm.llm_client import LLMClient

async def test_evaluator():
    llm_client = LLMClient()
    evaluator = EvaluatorAgent(llm_client)

    ad_content = {
        "headline": "Honda Civic 2021",
        "description": "Carro impecável.",
        "images": [{"url": "img1.jpg"}],
        "cta": "Contato"
    }

    result = await evaluator.execute({
        "ad_content": ad_content,
        "vehicle_id": "test-123",
        "include_benchmark": True
    })

    print(f"Score: {result['quality_score']}/100 ({result['quality_grade']})")
    print(f"Gaps: {len(result['gaps'])}")
    print(f"Recomendações: {len(result['recommendations'])}")

asyncio.run(test_evaluator())
```

**Validações:**
- ✅ Score entre 0 e 100
- ✅ Nota é A+, A, B, C ou D
- ✅ Pelo menos 1 gap identificado
- ✅ Pelo menos 1 recomendação
- ✅ Benchmark comparison presente

---

## 📊 Testes de Integração

### Teste Completo com Orchestrator

```python
import asyncio
from app.services.ai.orchestrator import get_orchestrator

async def test_orchestrator():
    orchestrator = get_orchestrator()

    # Vehicle data
    vehicle_data = {
        "id": "test-123",
        "brand": "Honda",
        "model": "Civic Touring",
        "model_year": 2021,
        "price": 138500
    }

    # Test prediction
    prediction = await orchestrator.predict_performance(
        vehicle_data=vehicle_data,
        forecast_days=30
    )
    print(f"✅ Prediction: CTR {prediction['predictions']['ctr']['predicted_ctr']:.2%}")

    # Test evaluation
    evaluation = await orchestrator.evaluate_content(
        ad_content={
            "headline": "Honda Civic 2021",
            "description": "Carro impecável",
            "images": [],
            "cta": ""
        },
        vehicle_id="test-123"
    )
    print(f"✅ Evaluation: Score {evaluation['quality_score']}/100")

asyncio.run(test_orchestrator())
```

---

## 🐛 Troubleshooting

### Erro: ModuleNotFoundError

**Problema:**
```
ModuleNotFoundError: No module named 'app'
```

**Solução:**
```bash
PYTHONPATH=. python3 scripts/ai/test_ai_agents.py
```

### Erro: TypeError - BasePromptTemplate

**Problema:**
```
TypeError: Can't instantiate abstract class BasePromptTemplate
```

**Solução:**
Verifique se `ai_agents.py` existe em `app/services/llm/prompts/`:
```bash
ls -la backend/app/services/llm/prompts/ai_agents.py
```

### Erro: ML Models Not Found

**Problema:**
```
ModuleNotFoundError: No module named 'app.services.ml'
```

**Solução:**
Os modelos ML da semana 7 devem estar instalados:
```bash
cd backend/app/services/ml
python -m pip install -r requirements.txt
```

### Erro: Redis Connection

**Problema:**
```
Error connecting to Redis
```

**Solução:**
Redis é opcional. Os agentes funcionam sem cache:
```python
# No código, ignore erros de cache
try:
    # cache operations
except Exception:
    pass  # continue without cache
```

---

## 📈 Performance Benchmarks

### Tempos de Execução Esperados

| Operação | Tempo | Nota |
|----------|-------|------|
| PredictorAgent.execute() | < 200ms | Sem LLM calls |
| OptimizerAgent.execute() | < 100ms | Apenas regras |
| EvaluatorAgent.execute() | < 50ms | Scoring local |
| Teste completo | < 1s | 3 agentes + ML predictions |

### Como Medir

```python
import time

start = time.time()
result = await predictor.execute(context)
elapsed = time.time() - start

print(f"Tempo: {elapsed*1000:.2f}ms")
assert elapsed < 0.2, "Muito lento!"
```

---

## ✅ Checklist de Validação

### PredictorAgent
- [ ] Prediz CTR (0-1)
- [ ] Prediz conversão (0-1)
- [ ] Prediz preço (valor numérico)
- [ ] Forecast tem N dias
- [ ] Risk score (0-1)
- [ ] Confidence score (0-1)

### OptimizerAgent
- [ ] Retorna recomendações de conteúdo
- [ ] Bid recommendations presentes
- [ ] Budget optimization calculado
- [ ] A/B tests sugeridos
- [ ] Priority improvements listadas

### EvaluatorAgent
- [ ] Quality score (0-100)
- [ ] Quality grade (A+/A/B/C/D)
- [ ] Content analysis completa
- [ ] Gaps identificados
- [ ] Benchmark comparison
- [ ] Recomendações geradas

---

## 🚀 Teste de Carga (Opcional)

### Simular 100 Veículos

```python
import asyncio
from app.services.ai.agents.predictor import PredictorAgent
from app.services.llm.llm_client import LLMClient
import time

async def load_test():
    predictor = PredictorAgent(LLMClient())

    start = time.time()
    for i in range(100):
        await predictor.execute({
            "vehicle_data": {
                "id": f"test-{i}",
                "brand": "Honda",
                "model": "Civic",
                "price": 100000 + i * 1000
            },
            "forecast_days": 30
        })

    elapsed = time.time() - start
    print(f"100 veículos em {elapsed:.2f}s")
    print(f"Média: {elapsed/100*1000:.2f}ms por veículo")

asyncio.run(load_test())
```

**Expected:**
- Total < 20s
- Média < 200ms por veículo

---

## 📝 Testes Manuais Adicionais

### Cenário 1: Anúncio Perfeito

```python
perfect_ad = {
    "headline": "Honda Civic Touring 2021 - Impecável! Único Dono - R$ 138.500",
    "description": "Honda Civic Touring 2021, apenas 25.000km, único dono, todas revisões na concessionária. Carro impecável, sem detalhes, garagem coberta. Ar condicionado digital, bancos de couro, teto solar, central multimidia de 8 polegadas com Android Auto e Apple CarPlay. 4 airbags, ABS, controle de estabilidade e tração.",
    "images": [{"url": f"img{i}.jpg"} for i in range(7)],
    "cta": "Chame no WhatsApp agora e agende seu test-drive!"
}
```

**Expected:**
- Score > 80/100
- Grade A ou A+
- Poucos gaps

### Cenário 2: Anúncio Ruim

```python
bad_ad = {
    "headline": "Carro",
    "description": "Vendo",
    "images": [],
    "cta": ""
}
```

**Expected:**
- Score < 30/100
- Grade D
- Muitos gaps

---

## 🔍 Debug Tips

### Ativar Logging Detalhado

```python
import logging

# Level DEBUG para ver tudo
logging.basicConfig(level=logging.DEBUG)

# Level INFO para resumo
logging.basicConfig(level=logging.INFO)
```

### Inspecionar Resultados

```python
import json

result = await predictor.execute(context)

# Pretty print JSON
print(json.dumps(result, indent=2))
```

---

## 📚 Referências

- **Código**: `backend/app/services/ai/agents/`
- **Testes**: `backend/scripts/ai/test_ai_agents.py`
- **Semana 5**: `historico/semana5-ai-service/TESTING.md`
- **Semana 7**: `historico/semana7-ml-models/TESTING.md`

---

**Última Atualização**: 20/04/2026
