# Semana 8: Predictor & Optimizer Agents - Guia de Operação

## 📋 Visão Geral

Este documento é um guia prático para operar e utilizar os agentes AI implementados na Semana 8.

---

## 🤖 Os 3 Agentes

### 1. PredictorAgent

**Responsável**: Predizer performance de anúncios

**Capabilities:**
- Performance prediction (CTR, conversão, preço)
- Forecasting (7d, 30d, 90d)
- Scenario analysis (budget variations)
- Risk assessment

**Use Cases:**
- Estimar performance de novos anúncios
- Forecast de métricas futuras
- Análise de risco de campanhas
- Comparação de cenários de budget

### 2. OptimizerAgent

**Responsável**: Otimizar anúncios existentes

**Capabilities:**
- Content optimization (headline, description, images, CTA)
- Bid recommendations
- Budget optimization
- A/B testing suggestions
- Priority improvements

**Use Cases:**
- Melhorar anúncios com baixa performance
- Calcular lances ideais
- Otimizar alocação de budget
- Gerar ideias de testes A/B

### 3. EvaluatorAgent

**Responsável**: Avaliar qualidade de conteúdo

**Capabilities:**
- Quality scoring (0-100)
- Content analysis detalhada
- Benchmarking vs indústria
- Gap analysis
- Improvement roadmap

**Use Cases:**
- Auditar qualidade de anúncios
- Comparar com benchmarks
- Identificar gaps de conteúdo
- Gerar plano de melhorias

---

## 🚀 Quick Start

### Instalação

```bash
cd backend
pip install -r requirements.txt
```

### Teste Rápido

```bash
PYTHONPATH=. python3 scripts/ai/test_ai_agents.py
```

### Uso Básico

```python
import asyncio
from app.services.ai.orchestrator import get_orchestrator

async def main():
    orchestrator = get_orchestrator()

    # Predict
    prediction = await orchestrator.predict_performance(
        vehicle_data=vehicle_data,
        forecast_days=30
    )

    # Optimize
    optimization = await orchestrator.optimize_ad(
        vehicle_data=vehicle_data,
        ad_content=ad_content,
        current_metrics=current_metrics,
        goals=goals
    )

    # Evaluate
    evaluation = await orchestrator.evaluate_content(
        ad_content=ad_content,
        vehicle_id=vehicle_id
    )

asyncio.run(main())
```

---

## 📖 Guia Detalhado

### PredictorAgent

#### Input

```python
{
    "vehicle_data": {
        "id": "uuid",
        "brand": "Honda",
        "model": "Civic Touring",
        "model_year": 2021,
        "mileage": 25000,
        "price": 138500.00,
        "days_since_listing": 37,
        "image_count": 5
    },
    "forecast_days": 30,  # 7, 30, ou 90
    "include_scenarios": False,  # True para análise de cenários
    "target_budget": 1000.00  # Obrigatório se include_scenarios=True
}
```

#### Output

```python
{
    "predictions": {
        "ctr": {
            "predicted_ctr": 0.045,  # 4.5%
            "ctr_bucket": "medium",  # very_low, low, medium, high, very_high
            "confidence": 0.75
        },
        "conversion": {
            "predicted_conversion_rate": 0.028,  # 2.8%
            "conversion_range": "2-4%",
            "confidence": 0.70
        },
        "price": {
            "predicted_price": 90250.00,
            "price_position": "fair_price",  # great_deal, good_price, fair_price, expensive, overpriced
            "confidence": 0.85
        }
    },
    "forecast": {
        "period_days": 30,
        "daily_predictions": [
            {
                "day": 1,
                "date": "2026-04-21",
                "impressions": 100,
                "clicks": 4.5,
                "conversions": 0.13,
                "ctr": 0.045,
                "conversion_rate": 0.028
            },
            # ... 30 dias
        ],
        "totals": {
            "impressions": 3000,
            "clicks": 107.3,
            "conversions": 2.4,
            "avg_ctr": 0.0358,
            "avg_conversion_rate": 0.028
        }
    },
    "risk_assessment": {
        "risk_score": 0.60,  # 0 = baixo, 1 = alto
        "risk_level": "high",  # low, medium, high
        "risk_factors": [
            "Preço acima do mercado pode dificultar venda",
            "CTR abaixo da média esperada"
        ]
    },
    "confidence": 0.767  # Média das confidências
}
```

#### Interpretação

**CTR Prediction:**
- `predicted_ctr`: Taxa de cliques esperada (0-1)
- `ctr_bucket`: Categoria (very_low a very_high)
- `confidence`: Quão confiável é a predição (0-1)

**Conversion Prediction:**
- `predicted_conversion_rate`: Taxa de conversão esperada (0-1)
- `conversion_range`: Range humano-legível
- `confidence`: Confiança da predição

**Price Prediction:**
- `predicted_price`: Preço de venda estimado
- `price_position`: Posição vs mercado
- `confidence`: Confiança da predição

**Forecast:**
- `daily_predictions`: Lista de predições diárias
- `totals`: Soma do período
  - `impressions`: Total de visualizações
  - `clicks`: Total de cliques
  - `conversions`: Total de conversões
  - `avg_ctr`: CTR médio do período
  - `avg_conversion_rate`: Conversão média do período

**Risk Assessment:**
- `risk_score`: Score de risco (0-1)
- `risk_level`: Nível de risco
- `risk_factors`: Lista de fatores de risco

---

### OptimizerAgent

#### Input

```python
{
    "vehicle_data": {
        "brand": "Honda",
        "model": "Civic",
        "price": 138500,
        "price_position": "fair_price",
        "demand_score": 0.5
    },
    "ad_content": {
        "headline": "Honda Civic 2021 - Seminovo",
        "description": "Honda Civic Touring 2021, apenas 25.000km.",
        "images": [{"url": "img1.jpg"}],
        "cta": "Entre em contato"
    },
    "current_metrics": {
        "ctr": 0.035,
        "conversion_rate": 0.025,
        "impressions": 1000,
        "clicks": 35
    },
    "goals": {
        "target_ctr": 0.05,
        "target_conversion": 0.035,
        "target_budget": 1000.00
    }
}
```

#### Output

```python
{
    "content_optimization": {
        "recommendations": [
            {
                "type": "headline",
                "issue": "Headline muito curto",
                "suggestion": "Tente 'Honda Civic 2021' → 'Honda Civic Touring 2021 - Impecável!'",
                "expected_improvement": "+15-25% CTR"
            },
            {
                "type": "headline",
                "issue": "Preço não mencionado",
                "suggestion": "Adicione preço: 'Honda Civic 2021 - R$ 138.500'",
                "expected_improvement": "+20% CTR"
            },
            {
                "type": "description",
                "issue": "Descrição muito curta",
                "suggestion": "Expanda descrição para 100+ palavras com detalhes",
                "expected_improvement": "+10% conversão"
            },
            {
                "type": "images",
                "issue": "Poucas imagens (1)",
                "suggestion": "Adicione 5-7 fotos (interior, exterior, detalhes)",
                "expected_improvement": "+30% CTR"
            }
        ],
        "priority_order": ["headline", "images", "description", "cta"]
    },
    "bid_recommendations": {
        "recommended_bid": 2.50,
        "min_bid": 1.75,
        "max_bid": 3.75,
        "reasoning": "Preço justo, manter lance padrão",
        "bid_strategy": "moderate"  # conservative, moderate, aggressive
    },
    "budget_optimization": {
        "recommendations": [
            {
                "action": "optimize_schedule",
                "reason": "Otimizar horários de exibição",
                "suggestion": "Concentrar budget entre 8h-12h e 18h-22h",
                "expected_impact": "+15-25% eficiência"
            }
        ],
        "optimal_daily_budget": 33.33  # R$ 1000 / 30 dias
    },
    "suggested_tests": [
        {
            "test_type": "headline",
            "test_name": "Variação de headline com preço",
            "variants": [
                "Honda Civic 2021 - Seminovo",
                "Honda Civic 2021 - Seminovo - R$ 138.500",
                "Honda Civic - Oferta!"
            ],
            "success_metric": "ctr",
            "expected_winner": "Com preço no título"
        },
        {
            "test_type": "images",
            "test_name": "Ordem das imagens",
            "variants": [
                "Imagem principal: foto frontal",
                "Imagem principal: foto lateral",
                "Imagem principal: foto interior"
            ],
            "success_metric": "ctr",
            "duration_days": 7
        },
        {
            "test_type": "cta",
            "test_name": "Variação de CTA",
            "variants": [
                "Entre em contato",
                "Agende test-drive",
                "Chame no WhatsApp"
            ],
            "success_metric": "conversion_rate",
            "expected_winner": "Chame no WhatsApp"
        }
    ],
    "optimization_priority": [
        "🔥 ADICIONAR MAIS FOTOS - Prioridade máxima",
        "⚡ ADICIONAR PREÇO NO TÍTULO",
        "⚡ EXPANDIR DESCRIÇÃO - Adicionar mais detalhes",
        "💡 ADICIONAR CALL-TO-ACTION"
    ]
}
```

#### Interpretação

**Content Optimization:**
- `recommendations`: Lista de recomendações específicas
  - `type`: Tipo de conteúdo (headline, description, images, cta)
  - `issue`: Problema identificado
  - `suggestion`: Sugestão concreta
  - `expected_improvement`: Impacto esperado

**Bid Recommendations:**
- `recommended_bid`: Lance ideal (CPC em R$)
- `min_bid`: Lance mínimo
- `max_bid`: Lance máximo
- `reasoning`: Justificativa
- `bid_strategy`: Estratégia (conservative, moderate, aggressive)

**Budget Optimization:**
- `recommendations`: Lista de recomendações de budget
- `optimal_daily_budget`: Budget diário ideal

**A/B Tests:**
- `suggested_tests`: Lista de testes sugeridos
  - `test_type`: Tipo de teste
  - `test_name`: Nome do teste
  - `variants`: Variantes para testar
  - `success_metric`: Métrica de sucesso
  - `expected_winner`: Variante vencedora esperada

**Priority Improvements:**
- `optimization_priority`: Lista ordenada de melhorias
  - 🔥 Alta prioridade (impacto imediato)
  - ⚡ Média prioridade (impacto significativo)
  - 💡 Baixa prioridade (nice to have)

---

### EvaluatorAgent

#### Input

```python
{
    "ad_content": {
        "headline": "Honda Civic 2021",
        "description": "Carro impecável.",
        "images": [{"url": "img1.jpg"}],
        "cta": "Contato"
    },
    "vehicle_id": "uuid",
    "include_benchmark": True
}
```

#### Output

```python
{
    "quality_score": 34.0,
    "quality_grade": "D",
    "content_analysis": {
        "headline_quality": 4.0,  # 0-10
        "description_quality": 0.5,  # 0-10
        "image_quality": 4.5,  # 0-10
        "cta_quality": 6.0,  # 0-10
        "word_count": 8,
        "character_count": 59
    },
    "gaps": [
        "Headline precisa melhorar (length, clareza)",
        "Descrição muito curta ou pobre",
        "Poucas imagens (1) - ideal: 5-7",
        "CTA fraco ou ausente"
    ],
    "benchmark_comparison": {
        "vs_industry": {
            "score_diff": -31.0,
            "percentage_diff": -47.7
        },
        "vs_top_10": {
            "score_diff": -46.0,
            "percentage_diff": -57.5
        },
        "industry_average": 65.0,
        "top_10_percent": 80.0,
        "percentile": 20.9
    },
    "recommendations": [
        "🔥 Prioridade alta: Revisar completamente o anúncio",
        "📝 Melhore o título (30-60 caracteres, inclua preço)",
        "📝 Expanda a descrição (100+ palavras com detalhes)",
        "📸 Adicione mais fotos (5-7, boa qualidade)",
        "🎯 Adicione call-to-action claro"
    ]
}
```

#### Interpretação

**Quality Score:**
- `quality_score`: Score geral (0-100)
- `quality_grade`: Nota (A+, A, B, C, D)
  - A+: 90-100 (Excelente)
  - A: 80-89 (Muito bom)
  - B: 70-79 (Bom)
  - C: 60-69 (Aceitável)
  - D: 0-59 (Ruim)

**Content Analysis:**
- Component scores (0-10 cada):
  - `headline_quality`: Qualidade do título
  - `description_quality`: Qualidade da descrição
  - `image_quality`: Qualidade das imagens
  - `cta_quality`: Qualidade do CTA
- `word_count`: Número de palavras
- `character_count`: Número de caracteres

**Gaps:**
- Lista de problemas identificados
- Específicos por componente

**Benchmark Comparison:**
- `vs_industry`: Comparação com média da indústria
  - `score_diff`: Diferença de score
  - `percentage_diff`: Diferença percentual
- `vs_top_10`: Comparação com top 10%
- `industry_average`: Média da indústria (65)
- `top_10_percent`: Score top 10% (80)
- `percentile`: Percentil (0-100)

**Recommendations:**
- Lista de melhorias priorizadas
- Específicas e acionáveis

---

## 💡 Casos de Uso

### Caso 1: Novo Anúncio

**Objetivo**: Estimar performance de um novo anúncio

```python
# 1. Prever performance
prediction = await orchestrator.predict_performance(
    vehicle_data=vehicle_data,
    forecast_days=30
)

# 2. Avaliar se vale a pena
if prediction['risk_assessment']['risk_score'] > 0.7:
    print("Alto risco! Considerar ajustar preço ou melhorar conteúdo")
else:
    print("Risco aceitável. Prosseguir com anúncio.")

# 3. Ver forecast
forecast = prediction['forecast']
print(f"Expected conversions in 30 days: {forecast['totals']['conversions']:.1f}")
```

### Caso 2: Otimizar Anúncio Existente

**Objetivo**: Melhorar performance de anúncio com baixa conversão

```python
# 1. Avaliar anúncio atual
evaluation = await orchestrator.evaluate_content(
    ad_content=ad_content,
    vehicle_id=vehicle_id
)

# 2. Se score baixo, otimizar
if evaluation['quality_score'] < 60:
    optimization = await orchestrator.optimize_ad(
        vehicle_data=vehicle_data,
        ad_content=ad_content,
        current_metrics=current_metrics,
        goals={"target_ctr": 0.05}
    )

    # 3. Aplicar recomendações
    print("Top 3 recomendações:")
    for rec in optimization['optimization_priority'][:3]:
        print(f"  - {rec}")
```

### Caso 3: A/B Testing

**Objetivo**: Gerar ideias de testes A/B

```python
# 1. Obter sugestões de testes
optimization = await orchestrator.optimize_ad(
    vehicle_data=vehicle_data,
    ad_content=ad_content,
    current_metrics=current_metrics,
    goals={}
)

# 2. Iterar sobre testes sugeridos
for test in optimization['suggested_tests']:
    print(f"Test: {test['test_name']}")
    print(f"  Type: {test['test_type']}")
    print(f"  Variants: {test['variants']}")
    print(f"  Expected winner: {test.get('expected_winner', 'Unknown')}")
    print()
```

### Caso 4: Análise de Cenários

**Objetivo**: Comparar diferentes budgets

```python
# 1. Prever com cenários
prediction = await orchestrator.predict_performance(
    vehicle_data=vehicle_data,
    forecast_days=30,
    include_scenarios=True,
    target_budget=1000.00
)

# 2. Comparar cenários
for scenario in prediction['scenarios']:
    print(f"{scenario['name']}:")
    print(f"  Budget: {scenario['budget_multiplier']*100}%")
    print(f"  Expected clicks: {scenario['expected_clicks']:.1f}")
    print()
```

---

## 🔧 Troubleshooting

### Problema: Predição muito baixa

**Sintoma**: CTR < 1% ou conversão < 1%

**Causas possíveis:**
- Preço muito acima do mercado
- Poucas imagens
- Descrição muito curta
- Anúncio velho (>60 dias)

**Solução:**
```python
# 1. Ver price position
if prediction['predictions']['price']['price_position'] == 'overpriced':
    print("Considerar reduzir preço")

# 2. Avaliar conteúdo
evaluation = await orchestrator.evaluate_content(
    ad_content=ad_content,
    vehicle_id=vehicle_id
)
print(f"Quality score: {evaluation['quality_score']}/100")

# 3. Otimizar
optimization = await orchestrator.optimize_ad(
    vehicle_data=vehicle_data,
    ad_content=ad_content,
    current_metrics=current_metrics,
    goals={}
)
```

### Problema: Score de qualidade baixo

**Sintoma**: Score < 50/100

**Causas possíveis:**
- Headline muito curto/longo
- Descrição muito curta
- Poucas imagens
- CTA fraco ou ausente

**Solução:**
```python
# 1. Ver gaps
evaluation = await orchestrator.evaluate_content(
    ad_content=ad_content,
    vehicle_id=vehicle_id
)

print("Gaps identificados:")
for gap in evaluation['gaps']:
    print(f"  - {gap}")

# 2. Seguir recomendações
print("\nRecomendações:")
for rec in evaluation['recommendations'][:5]:
    print(f"  - {rec}")
```

### Problema: Muitos fatores de risco

**Sintoma**: risk_factors tem 3+ itens

**Causas possíveis:**
- Preço acima do mercado
- CTR previsto baixo
- Anúncio velho
- Poucas imagens

**Solução:**
```python
# 1. Ver risk assessment
prediction = await orchestrator.predict_performance(
    vehicle_data=vehicle_data,
    forecast_days=30
)

risk = prediction['risk_assessment']
print(f"Risk level: {risk['risk_level']}")
print(f"Risk factors: {len(risk['risk_factors'])}")

# 2. Se alto risco, otimizar
if risk['risk_level'] == 'high':
    optimization = await orchestrator.optimize_ad(
        vehicle_data=vehicle_data,
        ad_content=ad_content,
        current_metrics=current_metrics,
        goals={}
    )
    print("\nTop prioridades:")
    for priority in optimization['optimization_priority'][:3]:
        print(f"  - {priority}")
```

---

## 📚 Referências

- **Implementação**: `historico/semana8-predictor-optimizer/IMPLEMENTATION_SUMMARY.md`
- **Testes**: `historico/semana8-predictor-optimizer/TESTING.md`
- **Roadmap**: `docs/referencias/roadmap.md`
- **Semana 5**: `historico/semana5-ai-service/`
- **Semana 7**: `historico/semana7-ml-models/`

---

**Última Atualização**: 20/04/2026
