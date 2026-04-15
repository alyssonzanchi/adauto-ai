"""
AI Service for vehicle analysis (Mock implementation).
Real AI implementation will be added in Week 5.
"""
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime

from app.models.enums import BodyType, FuelType


class AIService:
    """
    Service for AI-powered vehicle analysis.

    This is a mock implementation for testing.
    Real AI service will be implemented in Week 5 using Claude API.
    """

    async def analyze_vehicle(self, vehicle_data: Dict) -> Dict:
        """
        Analyze a vehicle and provide AI insights.

        Args:
            vehicle_data: Vehicle data dictionary

        Returns:
            Dictionary with AI analysis results
        """
        price = float(vehicle_data.get("price", 0))
        year = vehicle_data.get("year", 2020)
        mileage = vehicle_data.get("mileage", 50000)
        brand = vehicle_data.get("brand", "").lower()
        model = vehicle_data.get("model", "").lower()
        body_type = vehicle_data.get("body_type", BodyType.SEDAN)
        fuel_type = vehicle_data.get("fuel_type", FuelType.FLEX)
        features = vehicle_data.get("features", {})

        # Calculate market price (mock algorithm)
        price_market = self._calculate_market_price(
            price, year, mileage, brand, model, body_type
        )

        # Calculate price score
        price_score = self._calculate_price_score(price, price_market)

        # Determine price position
        price_position = self._get_price_position(price, price_market)

        # Generate selling points
        selling_points = self._generate_selling_points(
            year, mileage, features, vehicle_data
        )

        # Generate target audience
        target_audience = self._generate_target_audience(
            body_type, brand, model, price
        )

        # Generate suggested improvements
        suggested_improvements = self._generate_suggested_improvements(
            vehicle_data
        )

        # Estimate performance metrics
        estimated_ctr = self._estimate_ctr(selling_points, price_score)
        estimated_conversion = self._estimate_conversion(price_score, features)

        return {
            "price_market": float(price_market),
            "price_score": price_score,
            "price_position": price_position,
            "selling_points": selling_points,
            "target_audience": target_audience,
            "suggested_improvements": suggested_improvements,
            "estimated_ctr": estimated_ctr,
            "estimated_conversion": estimated_conversion,
            "analysis_version": "mock-v1.0.0",
            "analyzed_at": datetime.utcnow().isoformat(),
        }

    def _calculate_market_price(
        self,
        price: float,
        year: int,
        mileage: int,
        brand: str,
        model: str,
        body_type: BodyType
    ) -> Decimal:
        """
        Calculate estimated market price (mock algorithm).

        Args:
            price: Listed price
            year: Vehicle year
            mileage: Mileage
            brand: Brand name
            model: Model name
            body_type: Body type

        Returns:
            Estimated market price
        """
        # Base depreciation: 15% per year
        current_year = datetime.now().year
        age = current_year - year
        depreciation = 1 - (0.15 * age)

        # Mileage adjustment: 1% per 10,000 km above average
        avg_mileage = 15000 * age
        mileage_adjustment = 1.0
        if mileage > avg_mileage:
            excess_mileage = mileage - avg_mileage
            mileage_adjustment = 1 - (excess_mileage / 10000 * 0.01)

        # Brand premium (mock)
        brand_premium = 1.0
        premium_brands = ["bmw", "mercedes", "audi", "lexus", "volvo", "jaguar"]
        if brand in premium_brands:
            brand_premium = 1.1

        # Body type adjustment
        body_adjustment = {
            BodyType.SUV: 1.05,
            BodyType.PICKUP: 1.08,
            BodyType.SEDAN: 1.0,
            BodyType.HATCH: 0.95,
            BodyType.COUPE: 1.02,
        }.get(body_type, 1.0)

        # Calculate market price
        market_price = price * depreciation * mileage_adjustment * brand_premium * body_adjustment

        # Ensure it's within reasonable bounds
        market_price = max(price * 0.7, min(price * 1.3, market_price))

        return Decimal(str(round(market_price, 2)))

    def _calculate_price_score(self, price: float, market_price: Decimal) -> int:
        """
        Calculate price score (0-100).

        Score based on how competitive the price is compared to market.

        Args:
            price: Listed price
            market_price: Estimated market price

        Returns:
            Score from 0 to 100
        """
        market = float(market_price)
        diff_percent = ((price - market) / market) * 100

        # Score based on price difference
        if diff_percent <= -10:  # 10%+ below market
            return min(100, 85 + int(abs(diff_percent) / 2))
        elif diff_percent <= -5:  # 5-10% below market
            return 85
        elif diff_percent <= 5:  # Within 5% of market
            return 75
        elif diff_percent <= 10:  # 5-10% above market
            return 65
        elif diff_percent <= 20:  # 10-20% above market
            return 50
        else:  # More than 20% above market
            return max(0, 50 - int((diff_percent - 20) / 2))

    def _get_price_position(self, price: float, market_price: Decimal) -> str:
        """
        Get price position description.

        Args:
            price: Listed price
            market_price: Estimated market price

        Returns:
            Price position string
        """
        market = float(market_price)
        diff_percent = ((price - market) / market) * 100

        if diff_percent <= -10:
            return "great_deal"
        elif diff_percent <= -5:
            return "good_price"
        elif diff_percent <= 5:
            return "fair_price"
        elif diff_percent <= 10:
            return "above_market"
        elif diff_percent <= 20:
            return "expensive"
        else:
            return "overpriced"

    def _generate_selling_points(
        self,
        year: int,
        mileage: int,
        features: Dict,
        vehicle_data: Dict
    ) -> list:
        """
        Generate selling points for the vehicle.

        Args:
            year: Vehicle year
            mileage: Mileage
            features: Vehicle features
            vehicle_data: Full vehicle data

        Returns:
            List of selling points
        """
        points = []

        # Age-based points
        age = datetime.now().year - year
        if age <= 1:
            points.append("seminovo_zero_km")
        elif age <= 3:
            points.append("veiculo_recente")

        # Mileage-based points
        avg_mileage = 15000 * age
        if mileage < avg_mileage * 0.5:
            points.append("baixa_quilometragem")
        elif mileage < avg_mileage:
            points.append("quilometragem_abaixo_media")

        # Feature-based points
        if features:
            security = features.get("security", [])
            comfort = features.get("comfort", [])
            technology = features.get("technology", [])

            if "airbags" in security or "controle_estabilidade" in security:
                points.append("seguranca_avancada")
            if len(security) >= 3:
                points.append("completo_seguranca")

            if "ar_condicionado" in comfort and "direcao_eletrica" in comfort:
                points.append("conforto_destaque")
            if "bancos_couro" in comfort:
                points.append("acabamento_premium")

            if "central_multimidia" in technology or "android_auto" in technology:
                points.append("tecnologia_moderna")
            if "gps" in technology:
                points.append("navegacao_integrada")

        # Ownership
        ownership = vehicle_data.get("ownership")
        if ownership == "unico_dono":
            points.append("unico_dono")

        # Dealership trust
        points.append("garantia_concessionaria")

        return points[:6]  # Limit to 6 points

    def _generate_target_audience(
        self,
        body_type: BodyType,
        brand: str,
        model: str,
        price: float
    ) -> list:
        """
        Generate target audience for the vehicle.

        Args:
            body_type: Vehicle body type
            brand: Brand name
            model: Model name
            price: Vehicle price

        Returns:
            List of audience segments
        """
        audience = []

        # Body type-based audience
        if body_type == BodyType.SUV:
            audience.extend(["familias", "aventureiros"])
        elif body_type == BodyType.SEDAN:
            audience.extend(["profissionais_liberais", "executivos"])
        elif body_type == BodyType.HATCH:
            audience.extend(["jovens", "motoristas_urbanos"])
        elif body_type == BodyType.PICKUP:
            audience.extend(["profissionais", "entusiastas_offroad"])
        elif body_type == BodyType.COUPE:
            audience.extend(["entusiastas", "motoristas_esportivos"])

        # Price-based audience
        if price < 50000:
            audience.append("primeira_compra")
        elif price < 100000:
            audience.append("classe_media")
        else:
            audience.append("classe_media_alta")

        return list(set(audience))  # Remove duplicates

    def _generate_suggested_improvements(self, vehicle_data: Dict) -> list:
        """
        Generate suggestions to improve the listing.

        Args:
            vehicle_data: Vehicle data

        Returns:
            List of suggestions
        """
        suggestions = []

        # Check images
        images = vehicle_data.get("images", [])
        if len(images) < 10:
            suggestions.append("adicionar_mais_fotos")
        if len(images) < 5:
            suggestions.append("fotos_interiores")

        # Check description
        description = vehicle_data.get("description", "")
        if not description or len(description) < 200:
            suggestions.append("descricao_detalhada")

        # Check video
        if not vehicle_data.get("video_url"):
            suggestions.append("video_apresentacao")

        # Check features completeness
        features = vehicle_data.get("features", {})
        if not features or len(features) < 2:
            suggestions.append("listar_completar_features")

        # Check mileage
        mileage = vehicle_data.get("mileage", 0)
        if mileage > 100000:
            suggestions.append("destacar_manutencao")

        # Check year
        year = vehicle_data.get("year", 2020)
        if year < datetime.now().year - 5:
            suggestions.append("destacar_conservation_state")

        return suggestions[:5]  # Limit to 5 suggestions

    def _estimate_ctr(self, selling_points: list, price_score: int) -> float:
        """
        Estimate click-through rate.

        Args:
            selling_points: List of selling points
            price_score: Price score

        Returns:
            Estimated CTR (0-1)
        """
        base_ctr = 0.025  # 2.5% baseline

        # Boost for selling points
        points_boost = min(len(selling_points) * 0.003, 0.015)

        # Boost for price score
        price_boost = max(0, (price_score - 50) * 0.0005)

        ctr = base_ctr + points_boost + price_boost
        return round(min(ctr, 0.08), 3)  # Cap at 8%

    def _estimate_conversion(self, price_score: int, features: Dict) -> float:
        """
        Estimate conversion rate.

        Args:
            price_score: Price score
            features: Vehicle features

        Returns:
            Estimated conversion rate (0-1)
        """
        base_conv = 0.020  # 2.0% baseline

        # Price score impact
        price_boost = max(0, (price_score - 50) * 0.0004)

        # Features completeness boost
        features_count = sum(len(v) if isinstance(v, list) else 1 for v in features.values())
        features_boost = min(features_count * 0.001, 0.010)

        conv = base_conv + price_boost + features_boost
        return round(min(conv, 0.05), 3)  # Cap at 5%


# Global AI service instance
ai_service = AIService()
