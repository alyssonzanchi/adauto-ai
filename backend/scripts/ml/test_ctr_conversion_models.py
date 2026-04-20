"""
Script para testar CTR e Conversion Models
"""
import asyncio
from datetime import datetime
from app.services.ml.ctr_model import CTRModel
from app.services.ml.conversion_model import ConversionModel


# Veículo de teste
SAMPLE_VEHICLE = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
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
    "images": [{"url": "image1.jpg"}] * 5,
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
        "navigation": True,
    }
}

# Conteúdo do anúncio
SAMPLE_AD_CONTENT = {
    "headline": "Honda Civic 2021 - Impecável! Único Dono",
    "description": "Honda Civic Touring 2021, único dono, 25.000km. Carro impecável, todas as revisões na concessionária. Aceita financiamento.",
    "images": [{"url": f"image{i}.jpg"} for i in range(5)],
    "cta": "Entre em contato agora!"
}

# Lead de teste
SAMPLE_LEAD = {
    "name": "João Silva",
    "phone": "+55 11 98765-4321",
    "email": "joao@email.com",
    "type": "warm",
    "source": "organic",
    "response_time": 15,  # minutes
    "engagement_score": 0.7
}

# Interação de teste
SAMPLE_INTERACTION = {
    "view_count": 150,
    "unique_views": 120,
    "repeat_views": 30,
    "days_since_listing": 15,
    "image_views": 80,
    "gallery_views": 50,
    "phone_clicks": 12,
    "avg_session_duration": 180,  # seconds
    "total_session_duration": 27000,
    "bounce_rate": 0.35,
    "avg_click_depth": 3.5,
    "avg_time_on_page": 120,
    "avg_scroll_depth": 0.75,
    "form_submissions": 3,
    "test_drive_requests": 1,
    "financing_inquiries": 0,
    "lead_source": "organic",
    "lead_type": "warm",
    "device_type": "mobile",
    "os": "ios",
    "browser": "safari",
    "last_interaction": datetime(2024, 4, 20, 14, 30)
}


async def main():
    print("=" * 80)
    print("Teste dos CTR e Conversion Models - Semana 7: ML Models")
    print("=" * 80)
    print()

    # Test 1: CTR Model
    print("📊 Test 1: CTR Model (Click-Through Rate)")
    print("-" * 80)
    ctr_model = CTRModel()

    # Predição básica
    print("1.1. Predição Básica (apenas veículo):")
    prediction = await ctr_model.predict(SAMPLE_VEHICLE)
    print(f"   CTR Predito: {prediction['predicted_ctr']:.2%}")
    print(f"   Categoria: {prediction['ctr_bucket']}")
    print(f"   Confiança: {prediction['confidence']:.2%}")
    print()

    # Predição com ad content
    print("1.2. Predição com Ad Content:")
    prediction = await ctr_model.predict(
        SAMPLE_VEHICLE,
        ad_content=SAMPLE_AD_CONTENT
    )
    print(f"   CTR Predito: {prediction['predicted_ctr']:.2%}")
    print(f"   Categoria: {prediction['ctr_bucket']}")
    print(f"   Confiança: {prediction['confidence']:.2%}")
    print()

    # Predição completa
    print("1.3. Predição Completa (veículo + ad + interação):")
    prediction = await ctr_model.predict(
        SAMPLE_VEHICLE,
        ad_content=SAMPLE_AD_CONTENT,
        interaction_data=SAMPLE_INTERACTION
    )
    print(f"   CTR Predito: {prediction['predicted_ctr']:.2%}")
    print(f"   Categoria: {prediction['ctr_bucket']}")
    print(f"   Confiança: {prediction['confidence']:.2%}")
    print(f"   Sugestões de Otimização:")
    for i, suggestion in enumerate(prediction['optimization_suggestions'], 1):
        print(f"     {i}. {suggestion}")
    print()

    # Test 2: Conversion Model
    print("💰 Test 2: Conversion Model (Taxa de Conversão)")
    print("-" * 80)
    conversion_model = ConversionModel()

    # Predição básica
    print("2.1. Predição Básica (apenas veículo):")
    prediction = await conversion_model.predict(SAMPLE_VEHICLE)
    print(f"   Conversão Predita: {prediction['predicted_conversion_rate']:.2%}")
    print(f"   Probabilidade: {prediction['conversion_probability']}")
    print(f"   Score do Lead: {prediction['lead_quality_score']}/100")
    print(f"   Confiança: {prediction['confidence']:.2%}")
    print()

    # Predição com lead
    print("2.2. Predição com Lead Data:")
    prediction = await conversion_model.predict(
        SAMPLE_VEHICLE,
        lead_data=SAMPLE_LEAD
    )
    print(f"   Conversão Predita: {prediction['predicted_conversion_rate']:.2%}")
    print(f"   Probabilidade: {prediction['conversion_probability']}")
    print(f"   Score do Lead: {prediction['lead_quality_score']}/100")
    print(f"   Confiança: {prediction['confidence']:.2%}")
    print()

    # Predição completa
    print("2.3. Predição Completa (veículo + lead + interação):")
    prediction = await conversion_model.predict(
        SAMPLE_VEHICLE,
        lead_data=SAMPLE_LEAD,
        interaction_data=SAMPLE_INTERACTION
    )
    print(f"   Conversão Predita: {prediction['predicted_conversion_rate']:.2%}")
    print(f"   Probabilidade: {prediction['conversion_probability']}")
    print(f"   Score do Lead: {prediction['lead_quality_score']}/100")
    print(f"   Confiança: {prediction['confidence']:.2%}")
    print()

    # Test 3: Cenários de Lead
    print("🎯 Test 3: Cenários de Lead Qualidade")
    print("-" * 80)

    scenarios = [
        ("Lead Quente", "hot", "paid", 5),
        ("Lead Morno", "warm", "organic", 20),
        ("Lead Frio", "cold", "referral", 120)
    ]

    for name, lead_type, source, response_time in scenarios:
        lead = SAMPLE_LEAD.copy()
        lead["type"] = lead_type
        lead["source"] = source
        lead["response_time"] = response_time

        prediction = await conversion_model.predict(
            SAMPLE_VEHICLE,
            lead_data=lead
        )

        print(f"   {name} ({lead_type}, {source}, {response_time}min):")
        print(f"     Conversão: {prediction['predicted_conversion_rate']:.2%}")
        print(f"     Score: {prediction['lead_quality_score']}/100")
        print()

    # Test 4: Batch predictions
    print("📦 Test 4: Predições em Lote")
    print("-" * 80)

    vehicles = [SAMPLE_VEHICLE] * 3
    ctr_predictions = await ctr_model.predict_batch(vehicles)
    conversion_predictions = await conversion_model.predict_batch(vehicles)

    print(f"✅ Processados {len(ctr_predictions)} veículos (CTR)")
    for i, pred in enumerate(ctr_predictions, 1):
        print(f"   Veículo {i}: CTR {pred['predicted_ctr']:.2%} ({pred['ctr_bucket']})")
    print()

    print(f"✅ Processados {len(conversion_predictions)} veículos (Conversion)")
    for i, pred in enumerate(conversion_predictions, 1):
        print(f"   Veículo {i}: Conversão {pred['predicted_conversion_rate']:.2%} ({pred['conversion_probability']})")
    print()

    # Test 5: Integração dos 3 modelos
    print("🤖 Test 5: Integração Price + CTR + Conversion")
    print("-" * 80)

    from app.services.ml.price_model import PriceModel

    price_model = PriceModel()

    price_pred = await price_model.predict(SAMPLE_VEHICLE)
    ctr_pred = await ctr_model.predict(SAMPLE_VEHICLE, ad_content=SAMPLE_AD_CONTENT)
    conv_pred = await conversion_model.predict(SAMPLE_VEHICLE, lead_data=SAMPLE_LEAD)

    print("Análise Completa do Veículo:")
    print(f"   Preço Predito: R$ {price_pred['predicted_price']:,.2f}")
    print(f"   Score de Preço: {price_pred['price_score']}/100 ({price_pred['price_position']})")
    print()
    print(f"   CTR Esperado: {ctr_pred['predicted_ctr']:.2%} ({ctr_pred['ctr_bucket']})")
    print()
    print(f"   Conversão Esperada: {conv_pred['predicted_conversion_rate']:.2%} ({conv_pred['conversion_probability']})")
    print(f"   Score do Lead: {conv_pred['lead_quality_score']}/100")
    print()

    # Calcular métricas combinadas
    expected_clicks = 1000 * ctr_pred['predicted_ctr']  # 1000 impressões
    expected_conversions = expected_clicks * conv_pred['predicted_conversion_rate']
    expected_revenue = expected_conversions * price_pred['predicted_price']

    print("Projeções (para 1000 impressões):")
    print(f"   Cliques Esperados: {expected_clicks:.0f}")
    print(f"   Conversões Esperadas: {expected_conversions:.2f}")
    print(f"   Receita Esperada: R$ {expected_revenue:,.2f}")
    print()

    # Final
    print("=" * 80)
    print("✅ Todos os testes concluídos com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
