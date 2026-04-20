"""
Script para testar AI Agents - Semana 8: Predictor & Optimizer Agents
"""
import asyncio
from datetime import datetime
from app.services.ai.agents.predictor import PredictorAgent
from app.services.ai.agents.optimizer import OptimizerAgent
from app.services.ai.agents.evaluator import EvaluatorAgent
from app.services.llm.llm_client import LLMClient


# Veículo de teste
SAMPLE_VEHICLE = {
    "id": "test-vehicle-123",
    "brand": "Honda",
    "model": "Civic Touring",
    "model_year": 2021,
    "year": 2021,
    "mileage": 25000,
    "color": "Branco",
    "transmission": "CVT",
    "fuel_type": "flex",
    "body_type": "sedan",
    "doors": 4,
    "engine_capacity": 2.0,
    "horsepower": 173,
    "price": 138500.00,
    "status": "available",
    "created_at": datetime(2024, 3, 15),
    "days_since_listing": 37,
    "image_count": 5,
    "features": {
        "air_conditioning": True,
        "power_windows": True,
        "central_locking": True,
        "cruise_control": True,
        "sunroof": True,
        "leather_seats": True,
        "airbags": True,
        "abs": True,
        "bluetooth": True,
        "usb": True,
    }
}

# Conteúdo do anúncio
SAMPLE_AD_CONTENT = {
    "headline": "Honda Civic 2021 - Seminovo",
    "description": "Honda Civic Touring 2021, apenas 25.000km. Carro impecável.",
    "images": [
        {"url": "img1.jpg"},
        {"url": "img2.jpg"},
        {"url": "img3.jpg"}
    ],
    "cta": "Entre em contato"
}

# Métricas atuais
SAMPLE_CURRENT_METRICS = {
    "ctr": 0.035,
    "conversion_rate": 0.025,
    "impressions": 1000,
    "clicks": 35,
    "conversions": 1
}

# Goals
SAMPLE_GOALS = {
    "target_ctr": 0.05,
    "target_conversion": 0.035,
    "target_budget": 1000.00
}


async def main():
    print("=" * 80)
    print("Teste dos AI Agents - Semana 8: Predictor & Optimizer Agents")
    print("=" * 80)
    print()

    # Initialize LLM client
    llm_client = LLMClient()

    # ========================================
    # PARTE 1: PREDICTOR AGENT
    # ========================================
    print("📊 PARTE 1: PREDICTOR AGENT (Predição de Performance)")
    print("=" * 80)
    print()

    predictor = PredictorAgent(llm_client)

    # Test 1: Predição básica (30 dias)
    print("1.1. Predição de Performance (30 dias):")
    print("-" * 80)
    prediction = await predictor._execute_with_metrics({
        "vehicle_data": SAMPLE_VEHICLE,
        "forecast_days": 30,
        "include_scenarios": False,
        "target_budget": 1000.0
    })

    print(f"   CTR Predito: {prediction['predictions']['ctr']['predicted_ctr']:.2%}")
    print(f"   Conversão Predita: {prediction['predictions']['conversion']['predicted_conversion_rate']:.2%}")
    print(f"   Preço Predito: R$ {prediction['predictions']['price']['predicted_price']:,.2f}")
    print()
    print("Forecast de 30 dias:")
    forecast = prediction['forecast']
    print(f"   Impressões totais: {forecast['totals']['impressions']:,}")
    print(f"   Cliques totais: {forecast['totals']['clicks']:.1f}")
    print(f"   Conversões totais: {forecast['totals']['conversions']:.1f}")
    print(f"   CTR médio: {forecast['totals']['avg_ctr']:.2%}")
    print()

    # Risk assessment
    risk = prediction['risk_assessment']
    print("Análise de Risco:")
    print(f"   Score de Risco: {risk['risk_score']:.2f}/1.00")
    print(f"   Nível: {risk['risk_level']}")
    if risk['risk_factors']:
        print("   Fatores de Risco:")
        for factor in risk['risk_factors']:
            print(f"     • {factor}")
    print()

    # ========================================
    # PARTE 2: OPTIMIZER AGENT
    # ========================================
    print()
    print("⚡ PARTE 2: OPTIMIZER AGENT (Otimização de Anúncios)")
    print("=" * 80)
    print()

    optimizer = OptimizerAgent(llm_client)

    print("2.1. Otimização de Conteúdo:")
    print("-" * 80)
    optimization = await optimizer._execute_with_metrics({
        "vehicle_data": SAMPLE_VEHICLE,
        "ad_content": SAMPLE_AD_CONTENT,
        "current_metrics": SAMPLE_CURRENT_METRICS,
        "goals": SAMPLE_GOALS
    })

    content_opt = optimization['content_optimization']
    print(f"   Recomendações: {len(content_opt['recommendations'])}")
    print()

    for i, rec in enumerate(content_opt['recommendations'][:5], 1):
        print(f"   {i}. {rec['issue']}")
        print(f"      Sugestão: {rec['suggestion']}")
        print(f"      Impacto esperado: {rec['expected_improvement']}")
    print()

    # Bid recommendations
    print("2.2. Recomendações de Lance:")
    print("-" * 80)
    bids = optimization['bid_recommendations']
    print(f"   Bid Recomendado: R$ {bids['recommended_bid']:.2f}")
    print(f"   Range: R$ {bids['min_bid']:.2f} - R$ {bids['max_bid']:.2f}")
    print(f"   Estratégia: {bids['bid_strategy']}")
    print(f"   Justificativa: {bids['reasoning']}")
    print()

    # Budget optimization
    print("2.3. Otimização de Budget:")
    print("-" * 80)
    budget = optimization['budget_optimization']
    print(f"   Budget diário ideal: R$ {budget['optimal_daily_budget']:.2f}")
    print()

    # A/B testing suggestions
    print("2.4. Sugestões de A/B Tests:")
    print("-" * 80)
    tests = optimization['suggested_tests']
    print(f"   Total de testes sugeridos: {len(tests)}")
    for i, test in enumerate(tests[:3], 1):
        print(f"   {i}. {test['test_name']}")
        print(f"      Tipo: {test['test_type']}")
        print(f"      Métrica: {test['success_metric']}")
        if test.get('expected_winner'):
            print(f"      Vencedor esperado: {test['expected_winner']}")
    print()

    # Priority improvements
    print("2.5. Melhorias Prioritárias:")
    print("-" * 80)
    priorities = optimization['optimization_priority']
    for i, priority in enumerate(priorities, 1):
        print(f"   {i}. {priority}")
    print()

    # ========================================
    # PARTE 3: EVALUATOR AGENT
    # ========================================
    print()
    print("🎯 PARTE 3: EVALUATOR AGENT (Avaliação de Conteúdo)")
    print("=" * 80)
    print()

    evaluator = EvaluatorAgent(llm_client)

    evaluation = await evaluator._execute_with_metrics({
        "ad_content": SAMPLE_AD_CONTENT,
        "vehicle_id": SAMPLE_VEHICLE["id"],
        "include_benchmark": True
    })

    # Quality score
    print("3.1. Score de Qualidade:")
    print("-" * 80)
    print(f"   Score Geral: {evaluation['quality_score']}/100")
    print(f"   Nota: {evaluation['quality_grade']}")
    print()

    # Content analysis
    print("3.2. Análise Detalhada:")
    print("-" * 80)
    analysis = evaluation['content_analysis']
    print(f"   Headline Quality: {analysis['headline_quality']}/10")
    print(f"   Description Quality: {analysis['description_quality']}/10")
    print(f"   Image Quality: {analysis['image_quality']}/10")
    print(f"   CTA Quality: {analysis['cta_quality']}/10")
    print(f"   Palavras: {analysis['word_count']}")
    print(f"   Caracteres: {analysis['character_count']}")
    print()

    # Gaps
    if evaluation['gaps']:
        print("3.3. Gaps Identificados:")
        print("-" * 80)
        for gap in evaluation['gaps']:
            print(f"   • {gap}")
        print()

    # Benchmark
    if evaluation['benchmark_comparison']:
        print("3.4. Comparação com Benchmark:")
        print("-" * 80)
        benchmark = evaluation['benchmark_comparison']
        print(f"   vs Indústria: {benchmark['vs_industry']['score_diff']:+.1f} ({benchmark['vs_industry']['percentage_diff']:+.1f}%)")
        print(f"   vs Top 10%: {benchmark['vs_top_10']['score_diff']:+.1f} ({benchmark['vs_top_10']['percentage_diff']:+.1f}%)")
        print(f"   Percentil: {benchmark['percentile']:.1f}")
        print()

    # Recommendations
    print("3.5. Recomendações de Melhoria:")
    print("-" * 80)
    recommendations = evaluation['recommendations']
    for i, rec in enumerate(recommendations[:7], 1):
        print(f"   {i}. {rec}")
    print()

    # ========================================
    # PARTE 4: INTEGRAÇÃO COMPLETA
    # ========================================
    print()
    print("🤖 PARTE 4: INTEGRAÇÃO COMPLETA (AI Orchestrator)")
    print("=" * 80)
    print()

    print("Usando Agent Orchestrator para coordenar todos os agentes:")
    print()

    # Aqui você usaria o orchestrator na prática
    print("from app.services.ai.orchestrator import get_orchestrator")
    print("orchestrator = get_orchestrator()")
    print()
    print("# Predição completa")
    print("prediction = await orchestrator.predict_performance(")
    print("    vehicle_data=vehicle_data,")
    print("    forecast_days=30,")
    print("    include_scenarios=True")
    print(")")
    print()
    print("# Otimização")
    print("optimization = await orchestrator.optimize_ad(")
    print("    vehicle_data=vehicle_data,")
    print("    ad_content=ad_content,")
    print("    current_metrics=current_metrics,")
    print("    goals=goals")
    print(")")
    print()
    print("# Avaliação")
    print("evaluation = await orchestrator.evaluate_content(")
    print("    ad_content=ad_content,")
    print("    vehicle_id=vehicle_id")
    print(")")
    print()

    # ========================================
    # RESUMO DOS RESULTADOS
    # ========================================
    print()
    print("=" * 80)
    print("✅ RESUMO DOS RESULTADOS - SEMANA 8")
    print("=" * 80)
    print()

    print("📊 PredictorAgent:")
    print(f"   • Forecasting de {forecast['period_days']} dias")
    print(f"   • {forecast['totals']['impressions']} impressões projetadas")
    print(f"   • Risco {risk['risk_level']} ({risk['risk_score']:.0%})")
    print()

    print("⚡ OptimizerAgent:")
    print(f"   • {len(content_opt['recommendations'])} recomendações de conteúdo")
    print(f"   • Bid estratégia: {bids['bid_strategy']}")
    print(f"   • {len(tests)} testes A/B sugeridos")
    print()

    print("🎯 EvaluatorAgent:")
    print(f"   • Score: {evaluation['quality_score']}/100 ({evaluation['quality_grade']})")
    print(f"   • {len(evaluation['gaps'])} gaps identificados")
    print(f"   • {len(evaluation['recommendations'])} recomendações")
    print()

    print("=" * 80)
    print("✅ TODOS OS AGENTES FUNCIONANDO!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
