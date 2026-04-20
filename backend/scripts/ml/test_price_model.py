"""
Script para testar Price Model
"""
import asyncio
from datetime import datetime
from app.services.ml.price_model import PriceModel
from app.ml.training.trainer import ModelTrainer


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
    "images": [{"url": "image1.jpg"}],
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
    print("Teste do Price Model - Semana 7: ML Models")
    print("=" * 80)
    print()

    # Test 1: Predição com fallback
    print("📊 Test 1: Predição de Preço (Fallback)")
    print("-" * 80)
    model = PriceModel()
    prediction = await model.predict(SAMPLE_VEHICLE)

    print(f"✅ Preço atual: R$ {SAMPLE_VEHICLE['price']:,.2f}")
    print(f"   Preço predito: R$ {prediction['predicted_price']:,.2f}")
    print(f"   Range: R$ {prediction['price_range'][0]:,.2f} - R$ {prediction['price_range'][1]:,.2f}")
    print(f"   Score: {prediction['price_score']}/100")
    print(f"   Posição: {prediction['price_position']}")
    print(f"   Confiança: {prediction['confidence']:.2%}")
    print()

    # Test 2: Diferentes cenários de preço
    print("💰 Test 2: Cenários de Preço")
    print("-" * 80)

    scenarios = [
        ("Muito barato", 100000),
        ("Preço justo", 135000),
        ("Caro", 160000),
        ("Muito caro", 180000)
    ]

    for scenario, price in scenarios:
        vehicle = SAMPLE_VEHICLE.copy()
        vehicle["price"] = price
        prediction = await model.predict(vehicle)
        print(f"   {scenario} (R$ {price:,.2f}):")
        print(f"     Score: {prediction['price_score']}/100")
        print(f"     Posição: {prediction['price_position']}")
        print()

    # Test 3: Batch predictions
    print("📦 Test 3: Predições em Lote")
    print("-" * 80)
    vehicles = [SAMPLE_VEHICLE] * 5
    predictions = await model.predict_batch(vehicles)
    print(f"✅ Processados {len(predictions)} veículos")
    for i, pred in enumerate(predictions[:3]):
        print(f"   Veículo {i+1}: R$ {pred['predicted_price']:,.2f} ({pred['price_position']})")
    print()

    # Test 4: Treinar modelo (synthetic data)
    print("🤖 Test 4: Treinar Modelo (Dados Sintéticos)")
    print("-" * 80)
    trainer = ModelTrainer()
    print("Treinando modelo XGBoost com 1000 amostras sintéticas...")
    metrics = await trainer.train_price_model_synthetic(n_samples=1000, model_version="test_1.0")

    print(f"✅ Modelo treinado!")
    print(f"   Train R²: {metrics['train_r2']:.4f}")
    print(f"   Test R²: {metrics['val_r2']:.4f}")
    print(f"   Test MAE: R$ {metrics['val_mae']:,.2f}")
    print()

    # Test 5: Predição com modelo treinado
    print("🎯 Test 5: Predição com Modelo Treinado")
    print("-" * 80)
    trained_model = PriceModel()
    success = trained_model.load_model("backend/app/ml/models/price_predictor_test_1.0.pkl")

    if success:
        prediction = await trained_model.predict(SAMPLE_VEHICLE)
        print(f"✅ Predição com modelo treinado:")
        print(f"   Preço predito: R$ {prediction['predicted_price']:,.2f}")
        print(f"   Range: R$ {prediction['price_range'][0]:,.2f} - R$ {prediction['price_range'][1]:,.2f}")
        print(f"   Score: {prediction['price_score']}/100")
        print(f"   Posição: {prediction['price_position']}")
        print(f"   Confiança: {prediction['confidence']:.2%}")
    else:
        print("⚠️  Não foi possível carregar o modelo treinado")
    print()

    # Test 6: Feature importance
    if "feature_importance" in metrics:
        print("📊 Test 6: Importância das Features (Top 10)")
        print("-" * 80)
        top_features = sorted(
            metrics["feature_importance"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        for feature, importance in top_features:
            bar = "█" * int(importance * 100)
            print(f"   {feature:40s} {importance:.4f} {bar}")
        print()

    # Final
    print("=" * 80)
    print("✅ Todos os testes concluídos com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
