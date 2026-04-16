"""
Ad content generation prompt template.
"""
from typing import Any, Dict

from app.services.llm.prompts.base import BasePromptTemplate


class AdGenerationPrompt(BasePromptTemplate):
    """
    Prompt template for generating ad content.

    Generates:
    - Compelling headlines
    - Detailed descriptions
    - Call-to-action phrases
    - Key highlights
    """

    def get_system_prompt(self) -> str:
        """Get system prompt for ad generation."""
        return """You are an expert automotive copywriter specializing in creating compelling vehicle advertisements for the Brazilian market.

Your writing is:
- Persuasive and engaging
- Honest and accurate
- Optimized for click-through and conversion
- Culturally relevant to Brazilian buyers
- Focused on benefits, not just features

Best practices:
- Use emotional triggers (freedom, safety, status, economy)
- Highlight unique selling propositions
- Create urgency without being pushy
- Use clear, specific language
- Include relevant keywords for SEO

Always provide responses in valid JSON format as requested."""

    def get_template_name(self) -> str:
        """Get template filename."""
        return "ad_generation.jinja2"

    def render_headline_prompt(self, vehicle: Dict[str, Any]) -> str:
        """Render headline generation prompt."""
        return self.render({"vehicle": vehicle, "content_type": "headline"})

    def render_description_prompt(self, vehicle: Dict[str, Any]) -> str:
        """Render description generation prompt."""
        return self.render({"vehicle": vehicle, "content_type": "description"})


class AdGenerationFewShots:
    """Few-shot examples for ad generation."""

    EXAMPLES = [
        {
            "input": {
                "brand": "Jeep",
                "model": "Compass Longitude",
                "year": 2022,
                "mileage": 28000,
                "price": 145000,
                "highlights": ["4x4", "teto_solar", "piloto_automatico"],
            },
            "output": {
                "headline": "Jeep Compass 4x4 Longitude 2022 - Pronto para Suas Aventuras",
                "subheadline": "Conforto, segurança e versatilidade em um único SUV",
                "description": """🚗 Jeep Compass Longitude 4x4 2022 - Impecável!

Este Jeep Compass é a escolha perfeita para quem busca versatilidade e performance. Com apenas 28.000 km, este veículo está praticamente novo e pronto para qualquer aventura.

✨ Destaques:
• Motor 4x4 completo para qualquer terreno
• Teto solar panorâmico para viagens inesquecíveis
• Piloto automático para longas distâncias
• Interior espaçoso e confortável
• Acabamento premium em toda cabine

🛡️ Sua segurança em primeiro lugar:
Conte com 6 airbags, controle de estabilidade e freios ABS de série.

💰 Por apenas R$145.000 - Um investimento inteligente!

📍 Localização: São Paulo, SP
📞 Agende seu test-drive hoje mesmo!

#JeepCompass #SUV4x4 #CarrosEmSaoPaulo""",
                "cta": "Agende seu test-drive",
                "keywords": [
                    "jeep compass 4x4",
                    "suv usado",
                    "carros em sao paulo",
                    "jeep seminovo"
                ]
            }
        },
        {
            "input": {
                "brand": "Honda",
                "model": "Civic Touring",
                "year": 2020,
                "mileage": 45000,
                "price": 115000,
                "highlights": ["sunroof", "bancos_couro", "system_audio_premium"],
            },
            "output": {
                "headline": "Honda Civic Touring 2020 - Sedã Premium com Estilo e Performance",
                "subheadline": "O equilíbrio perfeito entre esportividade e sofisticação",
                "description": """🚙 Honda Civic Touring 2020 - Sedã de Alto Padrão

Experimente a perfeição ao volante deste Honda Civic Touring. Com 45.000 km, este sedã oferece performance excepcional e conforto superior.

🌟 Principais Equipamentos:
• Sunroof elétrico para momentos especiais
• Bancos em couro premium com ajustes elétricos
• Sistema de áudio premium com 8 alto-falantes
• Central multimídia de última geração
• Sistema de som envolvente

⚡ Performance:
Motor 2.0 potente e eficiente, câmbio CVT suave e suspensão esportiva para dirigibilidade prazerosa.

🎯 Equipamentos de Série:
Direção elétrica, ar-condicionado dual zone, sensores de estacionamento, câmera de ré e muito mais!

💸 Valor: R$115.000 - Negócio de oportunidade!

📍 Disponível para test-drive

#HondaCivic #SedanPremium #CarrosNovos #HondaTouring""",
                "cta": "Entre em contato agora",
                "keywords": [
                    "honda civic touring",
                    "sedã usado",
                    "carros premium",
                    "honda seminovo"
                ]
            }
        },
    ]
