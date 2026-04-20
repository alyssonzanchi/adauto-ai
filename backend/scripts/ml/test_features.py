"""
Script para testar extração de features
"""
import asyncio
import json
from datetime import datetime
from app.ml.features import VehicleFeatures, MarketFeatures, TemporalFeatures, FeatureEngineer


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
    "images": [
        {"url": "image1.jpg"},
        {"url": "image2.jpg"},
        {"url": "image3.jpg"}
    ],
    "features": {
        "air_conditioning": True,
        "power_windows": True,
        "central_locking": True,
        "cruise_control": True,
        "sunroof": True,
        "leather_seats": True,
        "electric_seats": False,
        "airbags": True,
        "abs": True,
        "esp": True,
        "traction_control": True,
        "rear_camera": True,
        "parking_sensors": True,
        "bluetooth": True,
        "usb": True,
        "android_auto": True,
        "apple_carplay": True,
        "navigation": True,
        "premium_sound": True
    },
    "dealership_id": "dealership-uuid-123"
}


async def main():
    print("=" * 80)
    print("Teste de Extração de Features - Semana 7: ML Models")
    print("=" * 80)
    print()

    # Test 1: Vehicle Features
    print("📊 Test 1: Vehicle Features")
    print("-" * 80)
    vehicle_extractor = VehicleFeatures()
    vehicle_features = vehicle_extractor.extract(SAMPLE_VEHICLE)
    print(f"✅ Extraídas {len(vehicle_features)} features de veículo")
    print(f"   Features principais: {list(vehicle_features.keys())[:10]}")
    print()

    # Test 2: Temporal Features
    print("📅 Test 2: Temporal Features")
    print("-" * 80)
    temporal_extractor = TemporalFeatures()
    temporal_features = temporal_extractor.extract(SAMPLE_VEHICLE)
    print(f"✅ Extraídas {len(temporal_features)} features temporais")
    print(f"   Features principais: {list(temporal_features.keys())[:10]}")
    print()

    # Test 3: Market Features (sem DB)
    print("📈 Test 3: Market Features (sem DB)")
    print("-" * 80)
    market_extractor = MarketFeatures(db_session=None)
    market_features = await market_extractor.extract(SAMPLE_VEHICLE)
    print(f"✅ Extraídas {len(market_features)} features de mercado")
    print(f"   Features principais: {list(market_features.keys())[:10]}")
    print()

    # Test 4: Feature Engineer (todas as features)
    print("🔧 Test 4: Feature Engineer (todas as features)")
    print("-" * 80)
    engineer = FeatureEngineer(db_session=None)
    all_features = await engineer.extract_features(SAMPLE_VEHICLE)
    print(f"✅ Extraídas {len(all_features)} features no total")
    print()

    # Test 5: Contagem de features por categoria
    print("📊 Test 5: Contagem de Features por Categoria")
    print("-" * 80)
    counts = engineer.get_feature_counts()
    total_features = sum(counts.values())
    print(f"✅ Total de features: {total_features}")
    for category, count in counts.items():
        print(f"   {category}: {count} features")
    print()

    # Test 6: Validação de features
    print("✅ Test 6: Validação de Features")
    print("-" * 80)
    validation = engineer.validate_features(all_features)
    print(f"✅ Features válidas: {validation['is_valid']}")
    if validation['invalid_values']:
        print(f"   ⚠️  Valores inválidos: {validation['invalid_values']}")
    else:
        print("   ✅ Nenhum valor inválido")
    print()

    # Test 7: Resumo das features
    print("📝 Test 7: Resumo das Features")
    print("-" * 80)
    summary = engineer.summarize_features(all_features)
    print("   Veículo:")
    print(f"     Idade: {summary['vehicle']['age_years']:.1f} anos")
    print(f"     Quilometragem: {summary['vehicle']['mileage']:,} km")
    print(f"     Preço: R$ {summary['vehicle']['price']:,.2f}")
    print(f"     Condição: {summary['vehicle']['condition']:.2%}")
    print()
    print("   Mercado:")
    print(f"     Demanda: {summary['market']['demand']:.2%}")
    print(f"     Oferta: {summary['market']['supply']:.2%}")
    print(f"     Concorrência: {summary['market']['competition']} veículos")
    print()
    print("   Timing:")
    print(f"     Dias listado: {summary['timing']['days_listed']}")
    print(f"     Fim de semana: {'Sim' if summary['timing']['is_weekend'] else 'Não'}")
    print(f"     Período de pagamento: {'Sim' if summary['timing']['is_payday'] else 'Não'}")
    print(f"     Estação: {summary['timing']['season']}")
    print()
    print("   Scores:")
    print(f"     Equipamentos: {summary['scores']['feature_richness']:.2%}")
    print(f"     Segurança: {summary['scores']['safety']:.2%}")
    print(f"     Tecnologia: {summary['scores']['technology']:.2%}")
    print()

    # Test 8: Preparar para modelo ML
    print("🤖 Test 8: Preparar para Modelo ML")
    print("-" * 80)
    feature_array = engineer.prepare_for_model(all_features)
    print(f"✅ Array numpy criado: {feature_array.shape}")
    print(f"   Tipo: {feature_array.dtype}")
    print(f"   Primeiros 10 valores: {feature_array[:10]}")
    print()

    # Test 9: Exemplo de features específicas
    print("🎯 Test 9: Features Específicas")
    print("-" * 80)
    print("   Features de Marca:")
    for key in all_features:
        if key.startswith("brand_") and all_features[key] == 1:
            print(f"     {key}: {all_features[key]}")
    print()
    print("   Features de Condição:")
    print(f"     is_new: {all_features.get('is_new', 0)}")
    print(f"     is_semi_new: {all_features.get('is_semi_new', 0)}")
    print(f"     is_used: {all_features.get('is_used', 0)}")
    print(f"     low_mileage: {all_features.get('low_mileage', 0)}")
    print()
    print("   Features de Preço:")
    print(f"     price: R$ {all_features.get('price', 0):,.2f}")
    print(f"     price_per_km: R$ {all_features.get('price_per_km', 0):.2f}")
    print(f"     depreciation_rate: {all_features.get('depreciation_rate', 0):.2%}")
    print()

    # Final
    print("=" * 80)
    print("✅ Todos os testes concluídos com sucesso!")
    print(f"📊 Total de features extraídas: {len(all_features)}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
