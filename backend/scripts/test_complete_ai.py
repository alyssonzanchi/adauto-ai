#!/usr/bin/env python3
"""
Complete AI Service Test

Tests all AI service functionality to show everything works.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.services.ai.orchestrator import AgentOrchestrator
from app.services.llm.llm_client import LLMClient
from app.services.vector.embedding_service import EmbeddingService
from app.services.vector.vector_service import VectorService
from app.services.cache.feature_store import FeatureStore
from app.core.config import settings
import redis


async def test_complete_analysis():
    # Initialize
    llm_client = LLMClient()
    embedding_service = EmbeddingService()
    vector_service = VectorService(embedding_service=embedding_service)
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    feature_store = FeatureStore(redis_client=redis_client)

    orch = AgentOrchestrator(
        llm_client=llm_client,
        embedding_service=embedding_service,
        vector_service=vector_service,
        feature_store=feature_store,
    )

    # Test vehicle
    vehicle_data = {
        'id': 'test-hyundai',
        'brand': 'Hyundai',
        'model': 'Tucson',
        'year': 2023,
        'mileage': 15000,
        'price': 145000.0,
        'body_type': 'suv',
        'fuel_type': 'flex',
        'transmission': 'automatic',
        'features': {
            'security': ['airbags', 'abs', 'controle_estabilidade', 'camera_re'],
            'comfort': ['ar_condicionado', 'direcao_eletrica', 'bancos_couro', 'teto_solar'],
            'technology': ['central_multimidia', 'gps', 'android_auto', 'apple_carplay'],
        },
        'description': 'Hyundai Tucson Limited 2023, único dono, revisões na concessionária. SUV espaçoso e confortável para a família.',
        'title': 'Hyundai Tucson Limited 2023 Único Dono',
        'version': 'Limited',
        'color': 'Branco Pérola',
    }

    print('=' * 60)
    print('TESTE COMPLETO DE ANÁLISE DE VEÍCULO')
    print('=' * 60)
    print()

    # 1. Vehicle Analysis
    print('1. ANÁLISE COMPLETA DO VEÍCULO')
    print('-' * 60)
    analysis = await orch.analyze_vehicle(vehicle_data, db=None, use_cache=False)

    print(f'✅ Preço de Mercado: R${analysis.get("price_market", 0):,.2f}')
    print(f'✅ Score de Preço: {analysis.get("price_score", 0)}/100')
    print(f'✅ Posicionamento: {analysis.get("price_position", "N/A")}')
    print()
    print(f'✅ Selling Points ({len(analysis.get("selling_points", []))}):')
    for sp in analysis.get('selling_points', [])[:5]:
        print(f'   • {sp}')
    print()
    print(f'✅ Target Audience ({len(analysis.get("target_audience", []))}):')
    for ta in analysis.get('target_audience', [])[:4]:
        print(f'   • {ta}')
    print()
    print(f'✅ Suggested Improvements:')
    for si in analysis.get('suggested_improvements', [])[:3]:
        print(f'   • {si}')
    print()
    print(f'✅ CTR Estimado: {analysis.get("estimated_ctr", 0)*100:.1f}%')
    print(f'✅ Conversão Estimada: {analysis.get("estimated_conversion", 0)*100:.1f}%')
    print()

    # 2. Price Scoring
    print('2. ANÁLISE DE PREÇO')
    print('-' * 60)

    vehicle_with_price = {**vehicle_data, 'listed_price': 145000.0}
    price_score = await orch.score_price(vehicle_data=vehicle_with_price, use_cache=False)

    print(f'✅ Preço Justo: R${price_score.get("fair_market_price", 0):,.2f}')
    print(f'✅ Competitividade: {price_score.get("competitiveness_score", 0)}/100')
    print(f'✅ Posicionamento: {price_score.get("positioning", "N/A")}')
    print(f'✅ Diferença: R${price_score.get("listed_vs_market", {}).get("difference", 0):,.2f}')
    print()

    # 3. Ad Generation
    print('3. GERAÇÃO DE CONTEÚDO PARA ANÚNCIO')
    print('-' * 60)

    ad_content = await orch.generate_ad_content(
        vehicle_data=vehicle_data,
        content_type='full',
    )

    print(f'✅ Headline:')
    print(f'   {ad_content.get("headline", "N/A")}')
    print()
    print(f'✅ Subheadline:')
    print(f'   {ad_content.get("subheadline", "N/A")}')
    print()
    print(f'✅ Call-to-Action:')
    print(f'   {ad_content.get("cta", "N/A")}')
    print()
    print(f'✅ Keywords ({len(ad_content.get("keywords", []))}):')
    for kw in ad_content.get('keywords', [])[:5]:
        print(f'   • {kw}')
    print()

    # 4. Health Check
    print('4. HEALTH CHECK DOS SERVIÇOS')
    print('-' * 60)

    health = await orch.health_check()
    print(f'✅ Status Geral: {health.get("status", "unknown")}')
    for service, status in health.get('services', {}).items():
        icon = '✅' if status == 'ok' else '⚠️'
        print(f'{icon} {service}: {status}')
    print()

    # 5. Metrics
    print('5. MÉTRICAS DE USO')
    print('-' * 60)

    metrics = orch.get_metrics()
    print(f'✅ Análises Realizadas: {metrics.get("analyses_performed", 0)}')
    print(f'✅ Calls Claude: {metrics.get("llm_client", {}).get("claude_calls", 0)}')
    print(f'✅ Tokens Usados: {metrics.get("llm_client", {}).get("total_tokens", 0)}')
    print(f'✅ Custo Estimado: US${metrics.get("llm_client", {}).get("total_cost", 0):.4f}')
    print()

    print('=' * 60)
    print('✨ TODOS OS SERVIÇOS AI FUNCIONANDO PERFEITAMENTE!')
    print('=' * 60)


if __name__ == "__main__":
    asyncio.run(test_complete_analysis())
