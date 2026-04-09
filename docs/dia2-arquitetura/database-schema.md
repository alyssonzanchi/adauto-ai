# Database Schema - Car Ads Platform

## Overview

Este documento descreve o schema completo do banco de dados PostgreSQL, incluindo todas as tabelas, relacionamentos, índices e enums.

---

## 1. Enumerations (Tipos Definidos)

### Status Types
```sql
-- Tipos de status para revendas
CREATE TYPE dealership_status AS ENUM (
    'active',      -- Revenda ativa
    'suspended',   -- Revenda suspensa (pagamento, etc.)
    'pending'      -- Aguardando aprovação
);

-- Tipos de usuário
CREATE TYPE user_role AS ENUM (
    'admin',       -- Administrador do sistema
    'manager',     -- Gerente da revenda
    'user'         -- Usuário comum
);

-- Tipos de status de usuário
CREATE TYPE user_status AS ENUM (
    'active',      -- Usuário ativo
    'inactive',    -- Usuário inativo
    'pending'      -- Aguardando confirmação
);

-- Tipos de combustível
CREATE TYPE fuel_type AS ENUM (
    'gasoline',    -- Gasolina
    'ethanol',     -- Etanol
    'diesel',      -- Diesel
    'flex',        -- Flex (gasolina/etanol)
    'electric',    -- Elétrico
    'hybrid'       -- Híbrido
);

-- Tipos de transmissão
CREATE TYPE transmission_type AS ENUM (
    'manual',      -- Manual
    'automatic',   -- Automática
    'cvt',         -- CVT
    'dct'          -- Dual Clutch Transmission
);

-- Tipos de carroceria
CREATE TYPE body_type AS ENUM (
    'sedan',       -- Sedan
    'hatch',       -- Hatchback
    'suv',         -- SUV
    'pickup',      -- Picape
    'coupe',       -- Coupé
    'convertible', -- Conversível
    'van',         -- Van/Minivan
    'wagon'        -- Perua
);

-- Tipos de status de veículo
CREATE TYPE vehicle_status AS ENUM (
    'active',      -- Veículo ativo, pode ser anunciado
    'sold',        -- Veículo vendido
    'pending',     -- Aguardando documentação/fotos
    'inactive'     -- Inativo, não será anunciado
);

-- Plataformas de anúncio
CREATE TYPE ad_platform AS ENUM (
    'facebook',    -- Facebook Ads
    'google',      -- Google Ads
    'instagram',   -- Instagram Ads
    'tiktok',      -- TikTok Ads
    'linkedin'     -- LinkedIn Ads
);

-- Tipos de status de anúncio
CREATE TYPE ad_status AS ENUM (
    'draft',       -- Rascunho
    'scheduled',   -- Agendado
    'active',      -- Ativo nas plataformas
    'paused',      -- Pausado
    'completed',   -- Completado (data final atingida)
    'cancelled'    -- Cancelado
);

-- Tipos de status de conexão
CREATE TYPE connection_status AS ENUM (
    'active',      -- Conexão ativa
    'expired',     -- Token expirado
    'error',       -- Erro na conexão
    'pending'      -- Aguardando autorização
);

-- Tipos de otimização
CREATE TYPE optimization_type AS ENUM (
    'budget',      -- Otimização de orçamento
    'creative',    -- Otimização de criativo
    'targeting',   -- Otimização de segmentação
    'bid'          -- Otimização de lance
);

-- Tipos de previsão
CREATE TYPE prediction_type AS ENUM (
    'ctr',          -- Click-through rate
    'conversion',   -- Taxa de conversão
    'clicks',       -- Número de cliques
    'impressions',  -- Número de impressões
    'roi',          -- Retorno sobre investimento
    'cost_per_lead' -- Custo por lead
);
```

---

## 2. Core Tables

### 2.1 Dealerships (Revendas)

Tabela principal de revendas de carros.

```sql
CREATE TABLE dealerships (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Informações básicas
    name VARCHAR(255) NOT NULL,
    trade_name VARCHAR(255),           -- Nome fantasia
    document_id VARCHAR(50) UNIQUE NOT NULL,  -- CNPJ
    state_registration VARCHAR(50),    -- Inscrição estadual

    -- Contato
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    whatsapp VARCHAR(20),
    website VARCHAR(255),

    -- Endereço (JSONB para flexibilidade)
    address JSONB,
    /*
    Formato esperado:
    {
        "street": "Rua Exemplo",
        "number": "123",
        "complement": "Sala 1",
        "neighborhood": "Centro",
        "city": "São Paulo",
        "state": "SP",
        "zip_code": "01234-567",
        "country": "BR",
        "latitude": -23.5505,
        "longitude": -46.6333
    }
    */

    -- Configurações
    status dealership_status DEFAULT 'active',
    settings JSONB DEFAULT '{}',
    /*
    {
        "timezone": "America/Sao_Paulo",
        "currency": "BRL",
        "notifications_enabled": true,
        "auto_optimization": true,
        "max_daily_budget": 1000
    }
    */

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE  -- Soft delete
);

-- Índices
CREATE INDEX idx_dealerships_status ON dealerships(status);
CREATE INDEX idx_dealerships_email ON dealerships(email);
CREATE INDEX idx_dealerships_document ON dealerships(document_id);
CREATE INDEX idx_dealerships_location ON dealerships USING GIN ((address->>'city'));

-- Triggers para updated_at
CREATE TRIGGER update_dealerships_updated_at
    BEFORE UPDATE ON dealerships
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 2.2 Users (Usuários)

Tabela de usuários do sistema (login).

```sql
CREATE TABLE users (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relacionamento
    dealership_id UUID NOT NULL REFERENCES dealerships(id) ON DELETE CASCADE,

    -- Informações pessoais
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),

    -- Autenticação
    password_hash VARCHAR(255) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,

    -- Permissões
    role user_role DEFAULT 'user',
    permissions JSONB DEFAULT '[]',
    /*
    ["vehicles:create", "vehicles:edit", "ads:publish", "metrics:view"]
    */

    -- Status
    status user_status DEFAULT 'active',

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Índices
CREATE INDEX idx_users_dealership ON users(dealership_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);

-- Trigger
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 2.3 Vehicles (Veículos)

Tabela principal de veículos.

```sql
CREATE TABLE vehicles (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relacionamento
    dealership_id UUID NOT NULL REFERENCES dealerships(id) ON DELETE CASCADE,

    -- Informações básicas
    title VARCHAR(500) NOT NULL,
    description TEXT,

    -- Características do veículo
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,              -- Ano de fabricação
    model_year INTEGER,                 -- Ano do modelo
    version VARCHAR(100),               -- Versão/Edição

    -- Especificações
    color VARCHAR(50),
    mileage INTEGER,                    -- Quilometragem
    mileage_unit VARCHAR(10) DEFAULT 'km',
    plate VARCHAR(20),                  -- Placa
    chassis VARCHAR(50) UNIQUE,         -- Chassi
    doors INTEGER,                      -- Número de portas
    seats INTEGER,                      -- Número de lugares

    -- Tipos
    fuel_type fuel_type,
    transmission transmission_type,
    body_type body_type,

    -- Preço
    price DECIMAL(12, 2) NOT NULL,
    price_market DECIMAL(12, 2),        -- Preço de mercado (AI)
    price_score INTEGER,                -- Score de preço (0-100)
    price_position VARCHAR(20),         -- 'below', 'fair', 'above'

    -- Features (Opcionais)
    features JSONB DEFAULT '{}',
    /*
    {
        "security": ["airbags", "abs", "controle_estabilidade"],
        "comfort": ["ar_condicionado", "direcao_eletrica", "bancos_couro"],
        "technology": ["central_multimidia", "gps", "android_auto"],
        "extras": ["rodas_liga_leve", "piloto_automatico", "teto_solar"]
    }
    */

    -- Mídia
    images TEXT[],                      -- URLs das imagens
    main_image TEXT,                    -- URL da imagem principal
    video_url TEXT,                     -- URL do vídeo (opcional)

    -- Documentação
    document_urls TEXT[],               -- URLs de documentos
    ownership VARCHAR(50),              -- 'unico_dono', 'duas_donas', etc.

    -- Status
    status vehicle_status DEFAULT 'active',
    sold_at TIMESTAMP WITH TIME ZONE,   -- Data da venda
    sold_price DECIMAL(12, 2),          -- Preço de venda

    -- AI Analysis
    ai_analysis JSONB,
    /*
    {
        "score": 85,
        "selling_points": ["unico_dono", "revisoes_concessionaria"],
        "target_audience": ["familias", "profissionais_liberais"],
        "suggested_improvements": ["mais_fotos_interior"],
        "estimated_ctr": 0.035,
        "estimated_conversion": 0.028,
        "model_version": "v1.2.0"
    }
    */

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Índices
CREATE INDEX idx_vehicles_dealership ON vehicles(dealership_id);
CREATE INDEX idx_vehicles_status ON vehicles(status);
CREATE INDEX idx_vehicles_brand_model ON vehicles(brand, model);
CREATE INDEX idx_vehicles_year ON vehicles(year);
CREATE INDEX idx_vehicles_price ON vehicles(price);
CREATE INDEX idx_vehicles_mileage ON vehicles(mileage);
CREATE INDEX idx_vehicles_features ON vehicles USING GIN (features);
CREATE INDEX idx_vehicles_created_at ON vehicles(created_at DESC);

-- Índices全文 search (opcional, requer extensão)
-- CREATE INDEX idx_vehicles_search ON vehicles USING GIN(to_tsvector('portuguese', title || ' ' || COALESCE(description, '')));

-- Trigger
CREATE TRIGGER update_vehicles_updated_at
    BEFORE UPDATE ON vehicles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 2.4 Ads (Anúncios)

Tabela de anúncios patrocinados.

```sql
CREATE TABLE ads (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relacionamento
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,

    -- Plataforma
    platform ad_platform NOT NULL,
    platform_ad_id VARCHAR(255),        -- ID do anúncio na plataforma externa

    -- Status
    status ad_status DEFAULT 'draft',

    -- Conteúdo do anúncio
    title VARCHAR(500),
    description TEXT,
    headline VARCHAR(255),              -- Primary text/headline
    call_to_action VARCHAR(100),

    -- Mídia
    images TEXT[],                      -- Criativos (image URLs)
    video_url TEXT,

    -- Segmentação
    target_audience JSONB,
    /*
    {
        "age_min": 25,
        "age_max": 55,
        "genders": ["male", "female"],
        "locations": [
            {"city": "São Paulo", "radius": 30}
        ],
        "interests": ["automotive", "suv", "off-road"],
        "behaviors": ["car_buyers", "luxury_shoppers"],
        "custom_audiences": ["website_visitors", "lookalike_1"]
    }
    */

    -- Orçamento
    budget_daily DECIMAL(10, 2),
    budget_total DECIMAL(10, 2),
    bid_amount DECIMAL(10, 2),          -- Lance máximo (CPC, CPM, etc.)
    bid_strategy VARCHAR(50),           -- 'lowest_cost', 'target_cost', etc.

    -- Datas
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,

    -- AI Generated
    ai_generated BOOLEAN DEFAULT false,
    ai_suggestions JSONB,               -- Sugestões da IA
    /*
    {
        "headlines": ["Opção 1", "Opção 2", "Opção 3"],
        "descriptions": ["Desc 1", "Desc 2"],
        "ctas": ["Agendar Test-Drive", "Saber Mais"],
        "estimated_ctr": {"min": 0.035, "max": 0.041},
        "estimated_conversions": {"min": 35, "max": 55}
    }
    */

    -- Performance agregada
    total_impressions INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    total_spend DECIMAL(10, 2) DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Índices
CREATE INDEX idx_ads_vehicle ON ads(vehicle_id);
CREATE INDEX idx_ads_platform ON ads(platform);
CREATE INDEX idx_ads_status ON ads(status);
CREATE INDEX idx_ads_dates ON ads(start_date, end_date);
CREATE INDEX idx_ads_created_at ON ads(created_at DESC);

-- Trigger
CREATE TRIGGER update_ads_updated_at
    BEFORE UPDATE ON ads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 2.5 Ad Metrics (Métricas de Anúncios)

Tabela de métricas diárias por anúncio.

```sql
CREATE TABLE ad_metrics (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relacionamento
    ad_id UUID NOT NULL REFERENCES ads(id) ON DELETE CASCADE,

    -- Data da métrica
    date DATE NOT NULL,

    -- Plataforma
    platform ad_platform NOT NULL,

    -- Métricas básicas
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    ctr DECIMAL(5, 4),                 -- Click-through rate

    -- Métricas de custo
    spend DECIMAL(10, 2) DEFAULT 0,
    cost_per_click DECIMAL(10, 2),      -- CPC
    cost_per_thousand DECIMAL(10, 2),   -- CPM
    cost_per_conversion DECIMAL(10, 2), -- CPA/CPL

    -- Métricas de conversão
    conversions INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5, 4),
    qualified_leads INTEGER DEFAULT 0,

    -- Revenue e ROI
    revenue DECIMAL(12, 2),             -- Receita gerada
    roi DECIMAL(10, 2),                 -- Return on investment
    roas DECIMAL(10, 2),                -- Return on ad spend

    -- Engajamento
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,

    -- Dados brutos da API
    raw_data JSONB,
    /*
    {
        "facebook": { ... },
        "google": { ... }
    }
    */

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint
    CONSTRAINT unique_ad_metric UNIQUE(ad_id, date, platform)
);

-- Índices
CREATE INDEX idx_ad_metrics_ad_date ON ad_metrics(ad_id, date DESC);
CREATE INDEX idx_ad_metrics_platform ON ad_metrics(platform, date DESC);
CREATE INDEX idx_ad_metrics_spend ON ad_metrics(spend);
CREATE INDEX idx_ad_metrics_ctr ON ad_metrics(ctr);
CREATE INDEX idx_ad_metrics_conversions ON ad_metrics(conversions);
```

### 2.6 Ad Platform Accounts (Contas de Plataformas)

Tabela de contas conectadas do Facebook/Google Ads.

```sql
CREATE TABLE ad_platform_accounts (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relacionamento
    dealership_id UUID NOT NULL REFERENCES dealerships(id) ON DELETE CASCADE,

    -- Plataforma
    platform ad_platform NOT NULL,

    -- Credenciais
    account_id VARCHAR(255) NOT NULL,   -- ID da conta na plataforma
    account_name VARCHAR(255),          -- Nome da conta
    business_id VARCHAR(255),           -- ID do Business Manager

    -- Tokens OAuth (criptografados)
    access_token TEXT,                  -- Token de acesso
    refresh_token TEXT,                 -- Token de refresh
    token_expires_at TIMESTAMP WITH TIME ZONE,

    -- Configurações
    status connection_status DEFAULT 'active',
    auto_sync BOOLEAN DEFAULT true,
    sync_interval INTEGER DEFAULT 3600,  -- Segundos entre syncs

    -- Metadata da plataforma
    platform_data JSONB,
    /*
    {
        "facebook": {
            "account_id": "act_123456",
            "business_id": "123456",
            "currency": "BRL",
            "timezone": "America/Sao_Paulo"
        }
    }
    */

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_sync_at TIMESTAMP WITH TIME ZONE
);

-- Índices
CREATE INDEX idx_ad_platform_accounts_dealership ON ad_platform_accounts(dealership_id);
CREATE INDEX idx_ad_platform_accounts_platform ON ad_platform_accounts(platform);
CREATE INDEX idx_ad_platform_accounts_status ON ad_platform_accounts(status);

-- Unique constraint
CREATE CONSTRAINT unique_platform_account UNIQUE(dealership_id, platform, account_id);

-- Trigger
CREATE TRIGGER update_ad_platform_accounts_updated_at
    BEFORE UPDATE ON ad_platform_accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 2.7 Ad Optimizations (Otimizações Automáticas)

Histórico de otimizações feitas pelo AI.

```sql
CREATE TABLE ad_optimizations (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relacionamento
    ad_id UUID NOT NULL REFERENCES ads(id) ON DELETE CASCADE,

    -- Tipo de otimização
    type optimization_type NOT NULL,

    -- Descrição
    description TEXT,

    -- Ação tomada
    action_taken JSONB,
    /*
    {
        "field": "budget_daily",
        "old_value": 100,
        "new_value": 150,
        "reason": "ctr_above_threshold"
    }
    */

    -- Resultado
    result JSONB,
    /*
    {
        "previous_ctr": 0.025,
        "new_ctr": 0.032,
        "improvement": 0.28,
        "status": "successful"
    }
    */

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_ad_optimizations_ad ON ad_optimizations(ad_id);
CREATE INDEX idx_ad_optimizations_type ON ad_optimizations(type);
CREATE INDEX idx_ad_optimizations_created_at ON ad_optimizations(created_at DESC);
```

### 2.8 ML Predictions (Previsões de ML)

Tabela de previsões feitas pelos modelos de ML.

```sql
CREATE TABLE ml_predictions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relacionamentos
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    ad_id UUID REFERENCES ads(id) ON DELETE CASCADE,

    -- Tipo de previsão
    prediction_type prediction_type NOT NULL,

    -- Previsão
    predicted_value DECIMAL(10, 2),
    confidence DECIMAL(5, 4),          -- 0.0 a 1.0

    -- Features usadas
    features JSONB,
    /*
    {
        "price": 135000,
        "mileage": 15000,
        "year": 2024,
        "brand_score": 0.85,
        "historical_ctr": 0.035
    }
    */

    -- Informações do modelo
    model_version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50),             -- 'xgboost', 'neural_network', etc.

    -- Avaliação da previsão
    actual_value DECIMAL(10, 2),        -- Valor real (para feedback)
    error DECIMAL(10, 2),               -- Erro absoluto

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_ml_predictions_vehicle ON ml_predictions(vehicle_id);
CREATE INDEX idx_ml_predictions_ad ON ml_predictions(ad_id);
CREATE INDEX idx_ml_predictions_type ON ml_predictions(prediction_type);
CREATE INDEX idx_ml_predictions_model ON ml_predictions(model_version);
CREATE INDEX idx_ml_predictions_created_at ON ml_predictions(created_at DESC);
```

### 2.9 Sessions (Sessões de Usuário)

Tabela de controle de sessões (opcional, pode usar Redis apenas).

```sql
CREATE TABLE sessions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relacionamento
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Token
    token VARCHAR(255) UNIQUE NOT NULL,

    -- Informações da sessão
    ip_address INET,
    user_agent TEXT,
    device_type VARCHAR(50),            -- 'desktop', 'mobile', 'tablet'

    -- Localização
    location JSONB,
    /*
    {
        "country": "BR",
        "state": "SP",
        "city": "São Paulo"
    }
    */

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

-- Cleanup job para remover sessões expiradas
-- DELETE FROM sessions WHERE expires_at < NOW();
```

---

## 3. Funções e Triggers

### Função Auxiliar: update_updated_at_column()

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';
```

### Trigger Automático para price_score

```sql
-- Trigger para atualizar price_score quando preço mudar
CREATE OR REPLACE FUNCTION update_vehicle_price_score()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.price <> OLD.price THEN
        -- Chamar função de AI para recalcular score
        -- Isso pode ser feito via application layer
        NEW.price_score = NULL;  -- Sinaliza para recalcular
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_update_vehicle_price_score
    BEFORE UPDATE OF price ON vehicles
    FOR EACH ROW
    EXECUTE FUNCTION update_vehicle_price_score();
```

---

## 4. Views Materializadas (Analytics)

### View: Daily Metrics Summary

```sql
CREATE MATERIALIZED VIEW daily_metrics_summary AS
SELECT
    date,
    platform,
    COUNT(DISTINCT ad_id) as active_ads,
    SUM(impressions) as total_impressions,
    SUM(clicks) as total_clicks,
    SUM(spend) as total_spend,
    SUM(conversions) as total_conversions,
    AVG(ctr) as avg_ctr,
    AVG(conversion_rate) as avg_conversion_rate,
    SUM(revenue) as total_revenue,
    AVG(roi) as avg_roi
FROM ad_metrics
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY date, platform
ORDER BY date DESC;

-- Refresh a cada hora
CREATE INDEX idx_daily_metrics_summary_date ON daily_metrics_summary(date);
```

### View: Top Performing Vehicles

```sql
CREATE MATERIALIZED VIEW top_performing_vehicles AS
SELECT
    v.id as vehicle_id,
    v.title,
    v.brand,
    v.model,
    v.price,
    COUNT(a.id) as total_ads,
    SUM(am.spend) as total_spend,
    SUM(am.conversions) as total_conversions,
    AVG(am.ctr) as avg_ctr,
    SUM(am.revenue) as total_revenue,
    AVG(am.roi) as avg_roi
FROM vehicles v
JOIN ads a ON v.id = a.vehicle_id
JOIN ad_metrics am ON a.id = am.ad_id
WHERE v.status = 'active'
  AND am.date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY v.id, v.title, v.brand, v.model, v.price
ORDER BY avg_roi DESC
LIMIT 100;

-- Refresh diário
```

---

## 5. Database Extensions

```sql
-- Extensão para dados geográficos
CREATE EXTENSION IF NOT EXISTS postgis;

-- Extensão para busca vetorial (AI/ML)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgvector;

-- Extensão para UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Extensão para full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Extensão para statistics
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

---

## 6. Performance Considerations

### Partitioning (para tabelas grandes)

```sql
-- Exemplo: Partition ad_metrics por mês
CREATE TABLE ad_metrics_y2024m01 PARTITION OF ad_metrics
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE ad_metrics_y2024m02 PARTITION OF ad_metrics
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- ... e assim por diante
```

### Connection Pooling

Usar **pg_bouncer** para pool de conexões:

```ini
[databases]
car_ads_db = host=localhost dbname=car_ads_db

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 50
```

---

## 7. Backup Strategy

### Physical Backup (pg_basebackup)

```bash
pg_basebackup -h localhost -D /var/lib/postgresql/backup -U replicator -P -v -R -X stream -C -S pgbackup_slot
```

### Logical Backup (pg_dump)

```bash
# Backup completo
pg_dump car_ads_db > car_ads_backup_$(date +%Y%m%d).sql

# Backup schema only
pg_dump --schema-only car_ads_db > schema_backup.sql

# Backup data only
pg_dump --data-only car_ads_db > data_backup.sql
```

---

## 8. Migration Commands

### Criar migration

```bash
alembic revision --autogenerate -m "Create initial schema"
```

### Aplicar migrations

```bash
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1
```

---

## 9. Diagrama ER Simplificado

```
┌─────────────┐
│dealerships  │
│─────┬───────│
│PK   │id     │
│     │name   │
│     │email  │
└─────┴───────┘
      │1
      │
      │N
┌─────▼──────────┐         ┌──────────────────┐
│users           │         │ad_platform_      │
│─────┬──────────│         │accounts          │
│PK   │id        │         │─────┬────────────│
│FK   │dealership│         │PK   │id          │
│     │_id      │         │FK   │dealership  │
│     │email    │         │     │_id         │
│     │role     │         │     │platform    │
└─────┴──────────┘         └─────┴────────────┘
                                      │1
                                      │
                                      │N
                              ┌───────▼──────────┐
                              │ads               │
                              │─────┬────────────│
                              │PK   │id          │
                              │FK   │vehicle_id  │
                              │     │platform    │
                              │     │status      │
                              └───────┴──────────┘
                                       │1
                                       │
                                       │N
                              ┌────────▼───────────────┐
                              │ad_metrics              │
                              │─────────────┬──────────│
                              │PK           │id        │
                              │FK           │ad_id     │
                              │             │date      │
                              │             │impressions│
                              └────────────────────────┘

┌─────────────┐
│vehicles     │
│─────┬───────│
│PK   │id     │
│FK   │dealership│
│     │_id    │
│     │brand  │
│     │model  │
│     │price  │
└─────┴───────┘
      │1
      │
      │N
┌─────▼─────────────────────────────┐
│ml_predictions                     │
│────────────┬──────────────────────│
│PK          │id                    │
│FK          │vehicle_id            │
│FK          │ad_id                 │
│            │prediction_type       │
│            │predicted_value       │
└────────────────────────────────────┘
```

---

## 10. Próximos Passos

1. ✅ Schema do banco de dados definido
2. ⏳ Criar migrations (Alembic)
3. ⏳ Implementar models (SQLAlchemy)
4. ⏳ Criar repositórios
5. ⏳ Implementar serviços de negócio
6. ⏳ Criar seeds para desenvolvimento
7. ⏳ Testar performance e otimizar queries
8. ⏳ Setup de backup e monitoramento
