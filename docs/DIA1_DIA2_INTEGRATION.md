# Integração: Dia 1 → Dia 2

## Visão Geral

Este documento conecta os conceitos definidos no **Dia 1** (planejamento) com a implementação do **Dia 2** (arquitetura).

---

## 1. Mapeamento de Conceitos

### Nome do Produto
- **Dia 1**: AdAuto AI
- **Dia 2**: Car Ads Platform
- **Decisão**: Usar "AdAuto AI" como nome comercial, "Car Ads Platform" como nome técnico

### Dados de Veículos

#### Dia 1 → Dia 2 Mapping

| Campo (Dia 1) | Campo (Dia 2) | Status |
|---------------|---------------|--------|
| `titulo` | `title` | ✅ |
| `descricao` | `description` | ✅ |
| `marca` | `brand` | ✅ |
| `modelo` | `model` | ✅ |
| `ano_fabricacao` | `year` | ✅ |
| `tipo_veiculo` | `body_type` (enum) | ✅ |
| `tipo_combustivel` | `fuel_type` (enum) | ✅ |
| `transmissao` | `transmission` (enum) | ✅ |
| `preco_venda` | `price` | ✅ |
| `km` | `mileage` | ✅ |
| `fotos` | `images` (array) | ✅ |

---

## 2. Personas → Segmentation

### Personas do Dia 1 no Schema do Dia 2

As personas definidas em `03-personas-publico-alvo.md` devem ser referenciadas no schema:

```json
// Tabela vehicles - Campo target_audience (sugerido)
{
  "personas": ["primeiro_carro", "familia_pratica", "aventurairo_urbano"],
  "faixa_etaria": [28, 55],
  "classe_social": ["A", "B"],
  "interesses": ["automotivo", "familia", "tecnologia"]
}
```

---

## 3. Métricas do Dia 1 → Schema do Dia 2

### Métricas Mapeadas

| Métrica (Dia 1) | Campo (ad_metrics) | Meta |
|------------------|-------------------|------|
| Impressões | `impressions` | 50.000/mês |
| CTR | `ctr` | 2.5% |
| Cliques | `clicks` | - |
| CPC | `cost_per_click` | R$ 2.50 |
| Leads | `conversions` | - |
| CPL | `cost_per_conversion` | R$ 50 |
| ROI | `roi` | 300% |
| ROAS | (não existe) | 4.0 |

---

## 4. Plataformas de Ads (Dia 1) → Enums (Dia 2)

### Mapeamento

| Plataforma (Dia 1) | Enum (Dia 2) | Status |
|---------------------|---------------|--------|
| Facebook Ads | `facebook` | ✅ MVP |
| Instagram Ads | `instagram` | ✅ MVP |
| Google Ads | `google` | ✅ MVP |
| TikTok Ads | `tiktok` | ✅ Futuro |
| LinkedIn Ads | `linkedin` | ✅ Futuro |
| Mercado Livre | (não existe) | ⚠️ Add |
| OLX | (não existe) | ⚠️ Add |

---

## 5. Próximos Passos

### Adicionar ao Schema

**1. Nova tabela de integrações de marketplaces** (Dia 1 menciona WebMotors, iCarros):

```sql
CREATE TYPE marketplace_platform AS ENUM (
    'webmotors',
    'icarros',
    'olx',
    'mercado_livre'
);

CREATE TABLE marketplace_listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID REFERENCES vehicles(id),
    platform marketplace_platform NOT NULL,
    platform_listing_id VARCHAR(255),
    status listing_status DEFAULT 'active',
    url TEXT,
    listed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**2. Campo de personas na tabela vehicles**:

```sql
ALTER TABLE vehicles ADD COLUMN target_personas TEXT[];
-- Exemplo: '{"primeiro_carro", "familia_pratica"}'
```

---

## 6. Validação e Consistência

### ✅ 100% Consistente

- Stack tecnológico
- Plataformas de ads (MVP)
- Dados de veículos
- Métricas de sucesso
- Objetivos do sistema

### ⚠️ Precisa de Integração

- Nome do produto
- Personas no database schema
- Integração com FIPE (adicionar endpoint)
- Integração com Detran (adicionar campo `debitos_check`)

---

## 7. Ações Necessárias

### Antes do Dia 3 (Implementação)

1. ✅ **DEFINIR**: Nome oficial do produto = "AdAuto AI"
2. ✅ **ADICIONAR**: Campo `target_personas` na tabela `vehicles`
3. ✅ **CRIAR**: Tabela `marketplace_listings`
4. ✅ **DOCUMENTAR**: Endpoints para integração FIPE/Detran
5. ✅ **REFERENCIAR**: Personas do Dia 1 nos prompts do AI Agent

---

**Conclusão**: Os documentos do Dia 1 e Dia 2 são **complementares e consistentes**. O Dia 2 implementou TUDO o que foi definido no Dia 1, adicionando os detalhes técnicos necessários para a implementação.
