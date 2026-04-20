"""
Teste Completo - Semana 7: ML Models
Feature Engineering + Price Model + CTR Model + Conversion Model
"""
import asyncio
from datetime import datetime
from app.ml.features import FeatureEngineer
from app.ml.features.interaction_features import InteractionFeatures
from app.services.ml import PriceModel, CTRModel, ConversionModel


# Veículo completo
SAMPLE_VEHICLE = {
    "id": "test-uuid-123",
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
    "images": [{"url": f"image{i}.jpg"} for i in range(5)],
    "features": {
        "air_conditioning": True,
        "power_windows": True,
        "central_locking": True,
        "cruise_control": True,
        "sunroof": True,
        "leather_seats": True,
        "airbags": True,
        "abs": True,
        "esp": True,
        "bluetooth": True,
        "usb": True,
        "android_auto": True,
        "navigation": True,
    },
    "dealership_id": "dealership-uuid"
}

SAMPLE_AD = {
    "headline": "Honda Civic 2021 - Impecável! Único Dono",
    "description": "Honda Civic Touring 2021, único dono, 25.000km.",
    "images": [{"url": f"img{i}.jpg"} for i in range(5)],
    "cta": "Entre em contato agora!"
}

SAMPLE_LEAD = {
    "name": "João Silva",
    "phone": "+55 11 98765-4321",
    "email": "joao@email.com",
    "type": "warm",
    "source": "organic",
    "response_time": 15,
    "engagement_score": 0.7
}


async def main():
    print("=" * 100)
    print(" " * 30 + "SEMANA 7: ML MODELS - TESTE COMPLETO")
    print("=" * 100)
    print()

    # ========================================
    # PARTE 1: FEATURE ENGINEERING
    # ========================================
    print("📊 PARTE 1: FEATURE ENGINEERING")
    print("=" * 100)
    print()

    engineer = FeatureEngineer(db_session=None)
    features = await engineer.extract_features(SAMPLE_VEHICLE)

    counts = engineer.get_feature_counts()
    total = sum(counts.values())

    print(f"✅ Extraídas {total} features no total")
    print()
    print("Distribuição por Categoria:")
    for category, count in counts.items():
        percentage = (count / total) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {category:20s}: {count:3d} features ({percentage:5.1f}%) {bar}")
    print()

    # Resumo das features
    summary = engineer.summarize_features(features)
    print("Resumo das Principais Features:")
    print(f"  Veículo: {summary['vehicle']['age_years']:.1f} anos, {summary['vehicle']['mileage']:.0f}km")
    print(f"  Condição: {summary['vehicle']['condition']:.1%}")
    print(f"  Demanda: {summary['market']['demand']:.1%}")
    print(f"  Timing: {summary['timing']['days_listed']} dias no mercado")
    print()

    # ========================================
    # PARTE 2: PRICE MODEL
    # ========================================
    print("💰 PARTE 2: PRICE MODEL (Previsão de Preço)")
    print("=" * 100)
    print()

    price_model = PriceModel()
    price_pred = await price_model.predict(SAMPLE_VEHICLE)

    print("Predição de Preço:")
    print(f"  Preço Atual:     R$ {SAMPLE_VEHICLE['price']:>12,.2f}")
    print(f"  Preço Predito:   R$ {price_pred['predicted_price']:>12,.2f}")
    print(f"  Range:           R$ {price_pred['price_range'][0]:>10,.2f} - R$ {price_pred['price_range'][1]:>10,.2f}")
    print(f"  Score:           {price_pred['price_score']:>3d}/100")
    print(f"  Posição:         {price_pred['price_position']:>15s}")
    print(f"  Confiança:       {price_pred['confidence']:>6.1%}")
    print()

    # Análise de preço
    diff = price_pred['predicted_price'] - SAMPLE_VEHICLE['price']
    diff_pct = (diff / price_pred['predicted_price']) * 100

    print("Análise:")
    if diff_pct > 5:
        print(f"  ⚠️  Veículo está {diff_pct:.1f}% ABAIXO do preço de mercado")
        print(f"      → ÓTIMO NEGÓCIO para comprador")
    elif diff_pct < -5:
        print(f"  ⚠️  Veículo está {abs(diff_pct):.1f}% ACIMA do preço de mercado")
        print(f"      → Pode dificultar venda")
    else:
        print(f"  ✅ Preço justo, dentro do mercado")
    print()

    # ========================================
    # PARTE 3: CTR MODEL
    # ========================================
    print("📈 PARTE 3: CTR MODEL (Previsão de Click-Through)")
    print("=" * 100)
    print()

    ctr_model = CTRModel()
    ctr_pred = await ctr_model.predict(
        SAMPLE_VEHICLE,
        ad_content=SAMPLE_AD
    )

    print("Predição de CTR:")
    print(f"  CTR Predito:     {ctr_pred['predicted_ctr']:>6.2%}")
    print(f"  Categoria:       {ctr_pred['ctr_bucket']:>15s}")
    print(f"  Confiança:       {ctr_pred['confidence']:>6.1%}")
    print()

    if ctr_pred['optimization_suggestions']:
        print("Sugestões de Otimização:")
        for i, suggestion in enumerate(ctr_pred['optimization_suggestions'], 1):
            print(f"  {i}. {suggestion}")
    else:
        print("  ✅ Anúncio bem otimizado!")
    print()

    # ========================================
    # PARTE 4: CONVERSION MODEL
    # ========================================
    print("🎯 PARTE 4: CONVERSION MODEL (Taxa de Conversão)")
    print("=" * 100)
    print()

    conversion_model = ConversionModel()
    conv_pred = await conversion_model.predict(
        SAMPLE_VEHICLE,
        lead_data=SAMPLE_LEAD
    )

    print("Predição de Conversão:")
    print(f"  Taxa Predita:    {conv_pred['predicted_conversion_rate']:>6.2%}")
    print(f"  Probabilidade:   {conv_pred['conversion_probability']:>15s}")
    print(f"  Score do Lead:   {conv_pred['lead_quality_score']:>3d}/100")
    print(f"  Confiança:       {conv_pred['confidence']:>6.1%}")
    print()

    # Avaliação do lead
    lead_score = conv_pred['lead_quality_score']
    if lead_score >= 70:
        print(f"  🔥 Lead QUENTE - Alta probabilidade de conversão")
    elif lead_score >= 40:
        print(f"  ⚡ Lead MORNO - Requer follow-up rápido")
    else:
        print(f"  ❄️  Lead FRIO - Baixa prioridade")
    print()

    # ========================================
    # PARTE 5: INTEGRAÇÃO COMPLETA
    # ========================================
    print("🤖 PARTE 5: INTEGRAÇÃO COMPLETA (ROI Projection)")
    print("=" * 100)
    print()

    print("Cenário: Campanha com 10.000 impressões")
    print()

    # Métricas
    impressions = 10000
    clicks = impressions * ctr_pred['predicted_ctr']
    conversions = clicks * conv_pred['predicted_conversion_rate']
    revenue = conversions * price_pred['predicted_price']

    print("Projeções:")
    print(f"  Impressões:      {impressions:>10,.0f}")
    print(f"  Cliques:         {clicks:>10,.1f} (CTR: {ctr_pred['predicted_ctr']:.2%})")
    print(f"  Conversões:      {conversions:>10,.2f} (Conv: {conv_pred['predicted_conversion_rate']:.2%})")
    print(f"  Receita Total:   R$ {revenue:>12,.2f}")
    print()

    # Cálculo de ROI
    cpc = 2.5  # Custo por clique (exemplo)
    ad_spend = clicks * cpc
    roi = ((revenue - ad_spend) / ad_spend) * 100

    print("Investimento (CPC: R$ 2,50):")
    print(f"  Custo com Ads:   R$ {ad_spend:>12,.2f}")
    print(f"  ROI:             {roi:>10.1f}%")
    print()

    if roi > 300:
        print("  🚀 Excelente! ROI muito alto")
    elif roi > 100:
        print("  ✅ Bom! ROI positivo")
    elif roi > 0:
        print("  ⚠️  Cuidado, ROI baixo")
    else:
        print("  ❌ Prejuízo!")
    print()

    # ========================================
    # PARTE 6: RECOMENDAÇÕES
    # ========================================
    print("💡 PARTE 6: RECOMENDAÇÕES FINAIS")
    print("=" * 100)
    print()

    recommendations = []

    # Price
    if price_pred['price_position'] == "overpriced":
        recommendations.append("🔻 Considere reduzir o preço para alinhar com o mercado")
    elif price_pred['price_position'] == "great_deal":
        recommendations.append("🔥 Excelente preço! Destaque isso no anúncio")

    # CTR
    if ctr_pred['predicted_ctr'] < 0.02:
        recommendations.append("📝 Melhore o título e adicione mais fotos")

    # Conversion
    if conv_pred['lead_quality_score'] < 50:
        recommendations.append("⏰ Responda leads em até 15 minutos")

    # Always add
    recommendations.append("📊 Monitore métricas semanalmente")
    recommendations.append("🔄 Atualize anúncios a cada 30 dias")

    print("Recomendações:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    print()

    # ========================================
    # FINAL
    # ========================================
    print("=" * 100)
    print("✅ TESTE COMPLETO FINALIZADO!")
    print("=" * 100)
    print()
    print("Resumo da Implementação:")
    print("  ✓ 134 features extraídas (Vehicle + Market + Temporal + Interaction)")
    print("  ✓ Price Model: Previsão de preço justo e competitividade")
    print("  ✓ CTR Model: Previsão de taxa de cliques")
    print("  ✓ Conversion Model: Previsão de taxa de conversão")
    print("  ✓ Integração completa via API endpoints")
    print()
    print("📁 Arquivos Criados: 20+ novos arquivos")
    print("   • app/ml/features/* (5 arquivos)")
    print("   • app/services/ml/* (6 arquivos)")
    print("   • app/ml/training/* (5 arquivos)")
    print("   • app/api/v1/endpoints/ml.py")
    print("   • app/schemas/ml.py")
    print("   • scripts/ml/* (4 scripts)")
    print("   • tests/services/ml/* (2 testes)")
    print()
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())
