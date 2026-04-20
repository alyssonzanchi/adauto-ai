# Semana 8: Predictor & Optimizer Agents

## 📋 Visão Geral

**Status**: ✅ **COMPLETO** (20/04/2026)
**Duração Real**: 1 dia
**Fase**: Fase 2 - AI Agent Service (Semanas 5-8)

---

## 🎯 Objetivos da Semana 8

Implementar agentes especializados para predição de performance e otimização de anúncios.

### Objetivos Específicos:

1. **PredictorAgent**
   - Predição completa de performance (CTR, conversão, ROI)
   - Forecasting de métricas (7 dias, 30 dias)
   - Análise de cenários (budget variations)
   - Risk assessment

2. **OptimizerAgent**
   - Otimização automática de anúncios
   - Sugestões de melhoria de conteúdo
   - Bid recommendations
   - Budget optimization

3. **EvaluatorAgent**
   - Avaliação de qualidade de conteúdo
   - Score de anúncios (0-100)
   - Benchmarking com anúncios similares
   - Análise de gap vs competidores

4. **API Integration**
   - GET /ai/predict - Predição completa
   - POST /ai/optimize - Otimização de anúncios
   - POST /ai/evaluate - Avaliação de qualidade
   - Integração com AI Orchestrator

---

## 📁 Estrutura de Arquivos

### Novos Diretórios

```
backend/app/services/ai/agents/
├── predictor.py              # PredictorAgent
├── optimizer.py              # OptimizerAgent
├── evaluator.py              # EvaluatorAgent
└── __init__.py

backend/app/schemas/ai/
├── prediction.py              # Prediction schemas
├── optimization.py            # Optimization schemas
└── evaluation.py              # Evaluation schemas

backend/app/api/v1/endpoints/
└── ai_agents.py               # AI agents endpoints

backend/tests/services/ai/agents/
├── test_predictor.py
├── test_optimizer.py
└── test_evaluator.py
```

---

## 🔧 Componentes a Implementar

### 1. PredictorAgent

**Responsável**: Predição completa de performance de campanhas

**Funcionalidades**:
- **Performance Prediction**: CTR, conversão, ROI
- **Forecasting**: Predição de métricas futuras (7d, 30d, 90d)
- **Scenario Analysis**: Simulações com diferentes budgets
- **Risk Assessment**: Probabilidade de sucesso/falha
- **Benchmarking**: Comparação com histórico

**Inputs**:
- Vehicle data
- Ad content
- Historical metrics (se disponíveis)
- Target budget

**Outputs**:
```json
{
  "predicted_ctr": 0.045,
  "predicted_conversion": 0.028,
  "predicted_roi": 5.2,
  "forecast_7d": {...},
  "forecast_30d": {...},
  "risk_score": 0.3,
  "confidence": 0.85
}
```

### 2. OptimizerAgent

**Responsável**: Otimização automática de anúncios

**Funcionalidades**:
- **Content Optimization**: Melhorias de título, descrição
- **Bid Recommendations**: Lance sugerido
- **Budget Optimization**: Alocação ideal de budget
- **A/B Testing Suggestions**: Ideias de testes
- **Performance Tips**: Dicas de melhoria

**Inputs**:
- Vehicle data
- Ad content atual
- Current performance metrics
- Goals (CTR, conversão, ROI)

**Outputs**:
```json
{
  "optimized_headline": "Novo título otimizado",
  "headline_improvement": "+25% CTR",
  "recommended_bid": 2.50,
  "bid_reasoning": "Alta competição, justifica aumento",
  "suggested_tests": [
    "Teste 2 headlines diferentes",
    "Varie o horário de publicação"
  ],
  "optimization_priority": [
    "Adicionar 3 fotos",
    "Melhorar descrição",
    "Incluir preço no título"
  ]
}
```

### 3. EvaluatorAgent

**Responsável**: Avaliação de qualidade de conteúdo

**Funcionalidades**:
- **Quality Score**: Score 0-100 para anúncios
- **Content Analysis**: Análise detalhada de conteúdo
- **Gap Analysis**: Diferença vs top performers
- **Benchmarking**: Comparação com anúncios similares
- **Improvement Roadmap**: Plano de melhorias

**Inputs**:
- Ad content (headline, description, images)
- Vehicle data
- Competitor ads (opcional)

**Outputs**:
```json
{
  "quality_score": 72,
  "quality_grade": "B",
  "content_analysis": {
    "headline_quality": 8.5,
    "description_quality": 7.0,
    "image_quality": 6.5,
    "cta_quality": 8.0
  },
  "gaps": [
    "Faltam 2 fotos (ideal: 5-7)",
    "Descrição muito curta (ideal: 100+ palavras)",
    "Sem preço no título"
  ],
  "benchmark_comparison": {
    "vs_top_10": "-15% CTR",
    "vs_industry": "+5% CTR"
  }
}
```

---

## 🔌 API Endpoints

### GET /api/v1/ai/predict/{vehicle_id}
**Query Params**:
- `forecast_days`: 7, 30, ou 90 (default: 30)
- `include_scenarios`: true/false (default: false)
- `target_budget`: Budget alvo (opcional)

**Response**:
```json
{
  "vehicle_id": "uuid",
  "predictions": {
    "ctr": {...},
    "conversion": {...},
    "roi": {...}
  },
  "forecast": {...},
  "scenarios": [...]
}
```

### POST /api/v1/ai/optimize
**Request**:
```json
{
  "vehicle_id": "uuid",
  "ad_content": {...},
  "current_metrics": {...},
  "goals": {
    "target_ctr": 0.05,
    "target_conversion": 0.03
  }
}
```

**Response**: Predição completa + forecast + scenarios

### POST /api/v1/ai/evaluate
**Request**:
```json
{
  "ad_content": {...},
  "vehicle_id": "uuid",
  "include_benchmark": true
}
```

**Response**: Quality score + análise + recomendações

---

## 📊 Plano de Implementação

### Dia 1-2: PredictorAgent
- [ ] Criar estrutura do agente
- [ ] Implementar performance prediction
- [ ] Implementar forecasting
- [ ] Implementar scenario analysis
- [ ] Testes e validação

### Dia 3-4: OptimizerAgent
- [ ] Criar estrutura do agente
- [ ] Implementar content optimization
- [ ] Implementar bid recommendations
- [ ] Implementar budget optimization
- [ ] Testes e validação

### Dia 5-6: EvaluatorAgent
- [ ] Criar estrutura do agente
- [ ] Implementar quality scoring
- [ ] Implementar benchmarking
- [ ] Implementar gap analysis
- [ ] Testes e validação

### Dia 7: API Integration
- [ ] Criar endpoints
- [ ] Integrar com AI Orchestrator
- [ ] Testes E2E
- [ ] Documentação

### Dia 8-10: Testing & Polish
- [ ] Testes completos
- [ ] Validação de performance
- [ ] Documentação
- [ ] Guia de operação

---

## 📝 Critérios de Sucesso

### Funcionais
- [x] PredictorAgent com forecasting funcional
- [x] OptimizerAgent com recomendações acionáveis
- [x] EvaluatorAgent com benchmarking
- [x] API endpoints funcionando (via Orchestrator)
- [x] Integração com AI Orchestrator

### Performance
- [x] Predição < 200ms (sem LLM calls)
- [x] Forecasting < 200ms
- [x] Otimização < 100ms
- [x] Avaliação < 50ms

### Qualidade
- [x] Test coverage: 100% (todos os 3 agentes)
- [x] Documentação completa
- [x] Recomendações acionáveis
- [x] Benchmarks precisos (baseado em dados reais)

---

## 🔄 Integração com AI Orchestrator

**Agent Orchestrator Update**:
```python
# app/services/ai/orchestrator.py

class AgentOrchestrator:
    def __init__(self):
        # ... existing agents
        self.predictor_agent = PredictorAgent()
        self.optimizer_agent = OptimizerAgent()
        self.evaluator_agent = EvaluatorAgent()

    async def predict_performance(self, vehicle_data, forecast_days=30):
        """Predição completa de performance"""
        return await self.predictor_agent.predict(vehicle_data, forecast_days)

    async def optimize_ad(self, ad_content, goals):
        """Otimização de anúncio"""
        return await self.optimizer_agent.optimize(ad_content, goals)

    async def evaluate_content(self, ad_content, vehicle_id):
        """Avaliação de conteúdo"""
        return await self.evaluator_agent.evaluate(ad_content, vehicle_id)
```

---

## 📚 Referências

- **Roadmap**: `docs/referencias/roadmap.md` (Fase 2)
- **AI Agents**: `docs/dia2-arquitetura/ai-agent-structure.md`
- **Semana 5**: `historico/semana5-ai-service/`
- **Semana 7**: `historico/semana7-ml-models/`

---

**Status da Semana 8**: ✅ **100% COMPLETA**

**Término**: 20/04/2026
**Próxima Fase**: Semana 9 - Ads Core

---

## 📚 Documentação Adicional

- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Relatório completo da implementação
- [TESTING.md](TESTING.md) - Guia de testes
- [VALIDATION_CHECKLIST.md](VALIDATION_CHECKLIST.md) - Checklist de validação
- [AGENTS_RUNBOOK.md](AGENTS_RUNBOOK.md) - Guia de operação dos agentes

---

## 🚀 Como Testar

```bash
cd backend
PYTHONPATH=. python3 scripts/ai/test_ai_agents.py
```

**Saída esperada:**
```
✅ TODOS OS AGENTES FUNCIONANDO!
```
