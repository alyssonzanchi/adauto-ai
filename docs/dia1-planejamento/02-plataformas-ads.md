# Plataformas de Anúncios - Especificações Técnicas

**Data**: 16/03/2026
**Versão**: 1.0

---

## 1. Visão Geral

Este documento define as plataformas de anúncios integradas ao sistema, especificações técnicas, requisitos de API e prioridade de implementação.

---

## 2. Plataformas do MVP

### 2.1 Facebook Ads

#### Descrição
Plataforma de publicidade da Meta com alcance massivo e segmentação avançada.

#### Capacidades
- **Formatos de Anúncio**:
  - Imagem única
  - Carrossel (múltiplas imagens)
  - Vídeo
  - Collection (catálogo)

- **Tipos de Campanha**:
  - Awareness (Consciência)
  - Traffic (Tráfego)
  - Leads (Geração de Leads)
  - Conversions (Conversões)

- **Segmentação**:
  - Localização (país, estado, cidade, raio)
  - Faixa etária
  - Gênero
  - Interesses (automobilismo, marcas específicas)
  - Comportamentos (compradores de carros, intenção de compra)
  - Lookalike Audiences (semelhantes aos clientes atuais)
  - Custom Audiences (baseada em dados)

#### API Facebook Marketing

**Endpoint Base**: `https://graph.facebook.com/v19.0/`

**Principais Recursos**:
```javascript
// Criar Campanha
POST /act_{ad_account_id}/campaigns
{
  "name": "Campanha Veículo XYZ",
  "objective": "CONVERSIONS",
  "status": "PAUSED",
  "special_ad_categories": [],
  "buying_type": "AUCTION"
}

// Criar Conjunto de Anúncios
POST /act_{ad_account_id}/adsets
{
  "name": "Conjunto - São Paulo",
  "campaign_id": "{campaign_id}",
  "targeting": {
    "geo_locations": { "cities": [{ "key": "São Paulo" }] },
    "age_min": 25,
    "age_max": 55,
    "interests": [{ "id": "6003139267462", "name": "Automotive industry" }]
  },
  "optimization_goal": "CONVERSIONS",
  "billing_event": "IMPRESSIONS",
  "bid_amount": 100,
  "daily_budget": "5000"
}

// Criar Anúncio
POST /act_{ad_account_id}/ads
{
  "name": "Anúncio - Honda Civic 2022",
  "adset_id": "{adset_id}",
  "creative": {
    "object_story_spec": {
      "page_id": "{page_id}",
      "link_data": {
        "image_hash": "{image_hash}",
        "link": "https://revenda.com/veiculo/123",
        "message": "Honda Civic 2022 impecável!",
        "call_to_action": { "type": "SHOP_NOW" }
      }
    }
  },
  "status": "PAUSED"
}
```

#### Autenticação
- **Tipo**: OAuth 2.0
- **Permissions Necessárias**:
  - `ads_management`
  - `ads_read`
  - `business_management`
  - `pages_read_engagement`
  - `pages_manage_ads`

#### Limites de Rate Limiting
- **Rate Limit**: 200 chamadas por hora por ad account
- **Batch API**: Até 50 operações por batch

---

### 2.2 Instagram Ads

#### Descrição
Plataforma visual integrada ao Facebook Ads, ideal para showcase de veículos.

#### Capacidades
- **Formatos de Anúncio**:
  - Stories (anúncios em tela cheia verticais)
  - Feed (quadrado ou retrato)
  - Reels (vídeos curtos)
  - Explore

- **Tipos de Campanha**:
  - Mesmos objetivos do Facebook Ads
  - Foco em engagement e descoberta

- **Segmentação**:
  - Herdada do Facebook Ads
  - Filtros específicos para Instagram
  - Interesses visuais e lifestyle

#### API Instagram Graph

**Endpoint Base**: `https://graph.facebook.com/v19.0/`

**Principais Recursos**:
```javascript
// Instagram Business Account está vinculado ao Facebook Page
GET /{page_id}?fields=instagram_business_account

// Criar anúncio específico para Instagram
// Usa a mesma API do Facebook Ads com platform_customizations
{
  "platform_customizations": {
    "instagram": {
      "revert_to_default_feed_if_missing": true
    }
  }
}
```

#### Autenticação
- **Vinculada ao Facebook Page**
- **Requer Instagram Business Account**
- **Mesmas permissões do Facebook Ads**

#### Considerações
- Formatos visuais requerem imagens/vídeos de alta qualidade
- Stories: proporção 9:16
- Feed: proporção 1:1 ou 4:5
- Reels: proporção 9:16, vídeo mínimo 3 segundos

---

### 2.3 Google Ads

#### Descrição
Plataforma de publicidade do Google com alcance em busca, display e YouTube.

#### Capacidades
- **Formatos de Anúncio**:

  **Search Ads (Pesquisa)**:
  - Texto com até 3 headlines (30 chars cada)
  - 2 descrições (90 chars cada)
  - Extensions (sitelinks, callouts, structured snippets)

  **Display Ads (Gráfico)**:
  - Imagens responsivas
  - Banner HTML5
  - Imagem quadrada ou retangular

  **Performance Max**:
  - Formato automático otimizado pelo Google
  - Abrange todos os canais (Search, Display, YouTube, Gmail, Maps)

- **Tipos de Campanha**:
  - Search (Pesquisa)
  - Display
  - Performance Max
  - Video (YouTube)

- **Segmentação**:
  - Palavras-chave (intenção de compra)
  - Localização geográfica
  - Faixa etária, gênero, renda
  - Interesses e tópicos
  - Remarketing/Remarketing dinâmico
  - In-Market Audiences (compradores de carros)

#### API Google Ads

**Endpoint Base**: `https://googleads.googleapis.com/v17/`

**Principais Recursos**:
```javascript
// Criar Campanha Search
POST /googleads.googleapis.com/v17/customers/{customer_id}/campaigns:mutate
{
  "operations": [{
    "create": {
      "name": "Campanha - Carros Usados",
      "advertising_channel_type": "SEARCH",
      "status": "PAUSED",
      "manual_cpc": {
        "enhanced_cpc_enabled": true
      },
      "campaign_budget": "customers/{customer_id}/campaignBudgets/{budget_id}",
      "target_cpa": {
        "target_cpa_micros": 50000000
      },
      "network_settings": {
        "target_google_search": true,
        "target_search_network": false,
        "target_content_network": false
      },
      "location_settings": {
        "geo_target_constant": "geoTargetConstants/1011746" // São Paulo
      },
      "start_date": "20260316",
      "end_date": "20260416"
    }
  }]
}

// Criar Grupo de Anúncios (Ad Group)
POST /googleads.googleapis.com/v17/customers/{customer_id}/adGroups:mutate
{
  "operations": [{
    "create": {
      "campaign": "customers/{customer_id}/campaigns/{campaign_id}",
      "name": "Ad Group - Hatchbacks",
      "status": "PAUSED",
      "type": "SEARCH_STANDARD",
      "cpc_bid_micros": 2000000
    }
  }]
}

// Criar Anúncio Search Expandido
POST /googleads.googleapis.com/v17/customers/{customer_id}/adGroupAds:mutate
{
  "operations": [{
    "create": {
      "ad_group": "customers/{customer_id}/adGroups/{ad_group_id}",
      "status": "PAUSED",
      "ad": {
        "expanded_search_ad": {
          "headlines": [
            { "text": "Honda Civic 2022" },
            { "text": "Único Dono" },
            { "text": "Financiamento Facilitado" }
          ],
          "descriptions": [
            { "text": "Hatch completo com menos de 30km. Aceita troca." },
            { "text": "Garantia de fábrica. Documentos em dia. Agende!" }
          ],
          "final_urls": ["https://revenda.com/veiculo/123"]
        }
      }
    }
  }]
}
```

#### Autenticação
- **Tipo**: OAuth 2.0 com Google Cloud
- **Scopes Necessários**:
  - `https://www.googleapis.com/auth/adwords`
- **Service Account** alternativa para automação

#### Limites de Rate Limiting
- **Quota**: 5000 unidades por dia (gratuito)
- **Custo por operação**: varia conforme o tipo de chamada

---

## 3. Plataformas Futuras (Post-MVP)

### 3.1 TikTok Ads

**Prioridade**: Alta
**Motivo**: Público jovem crescente buscando primeiros carros

**Capacidades**:
- Vertical Video Ads (9:16)
- Spark Ads (amplificar conteúdo orgânico)
- Segmentação por interesses e comportamentos

**Desafios**:
- API menos madura que Facebook/Google
- Público menos qualificado para carros usados
- Requer criativos em vídeo de alta qualidade

**API**: TikTok For Business Ads API

---

### 3.2 LinkedIn Ads

**Prioridade**: Média
**Motivo**: Segmentação por cargo/renda para carros de luxo

**Capacidades**:
- Sponsored Content
- Message Ads
- Segmentação por job title, empresa, indústria

**Desafios**:
- CPC muito elevado
- Público limitado para carros populares

**API**: Marketing Developer Platform

---

### 3.3 Mercado Livre Ads

**Prioridade**: Alta
**Motivo**: Maior marketplace da América Latina

**Capacidades**:
- Ads dentro do marketplace
- Intenção de compra alta
- Segmentação por categorias

**API**: Mercado Livre Advertising API

---

### 3.4 OLX Ads

**Prioridade**: Média
**Motivo**: Principal site de classificados do Brasil

**API**: OLX Pro API

---

## 4. Comparativo de Plataformas

| Plataforma | CPC Médio | Taxa de Conversão | Complexidade API | Prioridade MVP |
|------------|-----------|-------------------|------------------|----------------|
| Facebook Ads | R$ 1,50 - 3,00 | 2-4% | Média | Sim |
| Instagram Ads | R$ 2,00 - 4,00 | 1,5-3% | Média | Sim |
| Google Ads Search | R$ 3,00 - 8,00 | 5-8% | Alta | Sim |
| TikTok Ads | R$ 1,00 - 2,00 | 1-2% | Média | Não |
| LinkedIn Ads | R$ 8,00 - 15,00 | 3-5% | Média | Não |
| Mercado Livre | R$ 2,00 - 5,00 | 4-6% | Baixa | Não |

---

## 5. Requisitos de Integração

### 5.1 Contas de Desenvolvimento

**Facebook/Instagram**:
- Facebook Developer Account
- App criado no Facebook Developers
- App ID e App Secret
- Business Manager Account configurado
- Ad Account de teste

**Google Ads**:
- Google Cloud Project
- Google Ads Manager Account de teste
- Client Customer ID de teste
- Service Account ou OAuth Client

### 5.2 Webhooks

**Facebook/Instagram**:
- Webhook para mudanças de status de anúncios
- Webhook para atualizações de lead (Lead Ads)

**Google Ads**:
- Google Cloud Pub/Sub para notificações em tempo real

### 5.3 Pré-requisitos de Imagens/Vídeos

**Facebook/Instagram**:
- Imagens: JPG/PNG, máximo 30MB, recomendação 1080x1080
- Vídeos: MP4/MOV, máximo 4GB, recomendação 1080x1080 ou 1080x1920

**Google Ads**:
- Imagens: JPG/PNG, máximo 150KB, resolução mínima 600x314
- Vídeos: YouTube vinculado para Display Ads

---

## 6. Cronograma de Implementação

### Fase 1 (MVP) - Dia 6
- [ ] Setup Facebook Marketing API
- [ ] Setup Google Ads API
- [ ] Autenticação OAuth para ambas
- [ ] Wrappers base para criação de campanhas
- [ ] Upload de criativos

### Fase 2 (MVP) - Dia 8
- [ ] Criação completa de campanhas
- [ ] Recuperação de métricas
- [ ] Atualização de status (pause/resume)

### Fase 3 (Post-MVP)
- [ ] Integração TikTok Ads
- [ ] Integração Mercado Livre
- [ ] Integração OLX

---

**Próximo Documento**: [03-personas-publico-alvo.md](./03-personas-publico-alvo.md)
