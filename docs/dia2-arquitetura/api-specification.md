# API Specification - Car Ads Platform

## Overview

Este documento descreve todas as APIs do sistema, incluindo endpoints, request/response schemas, autenticação e exemplos de uso.

---

## Base URL

```
Production:  https://api.caradsplatform.com/api/v1
Staging:     https://api-staging.caradsplatform.com/api/v1
Development: http://localhost:8000/api/v1
```

---

## Autenticação

### JWT Token-based Authentication

Todos os endpoints (exceto auth) requerem um token JWT no header:

```http
Authorization: Bearer <token>
```

### Token Structure

```json
{
  "sub": "user_id",
  "dealership_id": "dealership_id",
  "role": "manager",
  "exp": 1234567890,
  "iat": 1234567890
}
```

---

## Response Format

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

---

## API Endpoints

### 1. Authentication APIs

#### POST /auth/register
Register a new dealership and user.

**Request Body:**
```json
{
  "dealership": {
    "name": "Auto Premium Ltda",
    "trade_name": "Auto Premium",
    "document_id": "12.345.678/0001-90",
    "email": "contato@autopremium.com.br",
    "phone": "+55 11 98765-4321",
    "whatsapp": "+55 11 98765-4321",
    "address": {
      "street": "Av. Paulista",
      "number": "1000",
      "complement": "Sala 101",
      "neighborhood": "Bela Vista",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01310-100",
      "latitude": -23.5505,
      "longitude": -46.6333
    }
  },
  "user": {
    "name": "João Silva",
    "email": "joao@autopremium.com.br",
    "password": "SecurePass123!",
    "role": "manager"
  }
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "dealership": {
      "id": "uuid",
      "name": "Auto Premium Ltda",
      "status": "pending",
      "created_at": "2026-03-17T10:00:00Z"
    },
    "user": {
      "id": "uuid",
      "name": "João Silva",
      "email": "joao@autopremium.com.br",
      "role": "manager"
    },
    "token": "jwt_token_here"
  },
  "message": "Registration successful. Please verify your email."
}
```

---

#### POST /auth/login
Login and get JWT token.

**Request Body:**
```json
{
  "email": "joao@autopremium.com.br",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "name": "João Silva",
      "email": "joao@autopremium.com.br",
      "role": "manager",
      "dealership": {
        "id": "uuid",
        "name": "Auto Premium Ltda"
      }
    },
    "token": "jwt_token_here",
    "refresh_token": "refresh_token_here",
    "expires_at": "2026-03-18T10:00:00Z"
  }
}
```

---

#### POST /auth/refresh
Refresh JWT token.

**Request Body:**
```json
{
  "refresh_token": "refresh_token_here"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "token": "new_jwt_token_here",
    "expires_at": "2026-03-18T10:00:00Z"
  }
}
```

---

#### POST /auth/logout
Logout and invalidate token.

**Request Headers:**
```http
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### 2. Vehicle APIs

#### GET /vehicles
List all vehicles with pagination and filters.

**Query Parameters:**
- `page` (integer, default: 1)
- `per_page` (integer, default: 20, max: 100)
- `search` (string) - Search in title, description
- `brand` (string) - Filter by brand
- `model` (string) - Filter by model
- `year_min` (integer) - Minimum year
- `year_max` (integer) - Maximum year
- `price_min` (decimal) - Minimum price
- `price_max` (decimal) - Maximum price
- `status` (string) - Filter by status
- `sort_by` (string) - Sort field (created_at, price, year, mileage)
- `sort_order` (string) - asc or desc

**Example:**
```http
GET /api/v1/vehicles?page=1&per_page=20&brand=Honda&price_min=50000&price_max=150000&sort_by=price&sort_order=asc
```

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "Honda Civic Touring 2024/2024 - Único Dono",
      "description": "Veículo impecável...",
      "brand": "Honda",
      "model": "Civic",
      "year": 2024,
      "version": "Touring 2.0 16V Flex Aut.",
      "color": "Branco Pérola",
      "mileage": 15000,
      "fuel_type": "flex",
      "transmission": "automatic",
      "body_type": "sedan",
      "price": 135000.00,
      "price_market": 140000.00,
      "price_score": 85,
      "main_image": "https://...",
      "status": "active",
      "ai_analysis": {
        "score": 85,
        "price_position": "below_market",
        "selling_points": ["unico_dono", "revisoes_concessionaria"]
      },
      "created_at": "2026-03-17T10:00:00Z",
      "ads_count": 2,
      "total_leads": 32
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "total_pages": 3
  }
}
```

---

#### POST /vehicles
Create a new vehicle.

**Request Body:**
```json
{
  "title": "Honda Civic Touring 2024/2024 - Único Dono",
  "description": "Veículo impecável, único dono...",
  "brand": "Honda",
  "model": "Civic",
  "year": 2024,
  "model_year": 2024,
  "version": "Touring 2.0 16V Flex Aut.",
  "color": "Branco Pérola",
  "mileage": 15000,
  "plate": "ABC1234",
  "fuel_type": "flex",
  "transmission": "automatic",
  "body_type": "sedan",
  "doors": 4,
  "seats": 5,
  "price": 135000.00,
  "features": {
    "security": ["airbags", "abs", "controle_estabilidade"],
    "comfort": ["ar_condicionado", "direcao_eletrica", "bancos_couro"],
    "technology": ["central_multimidia", "gps", "android_auto"],
    "extras": ["rodas_liga_leve", "piloto_automatico", "teto_solar"]
  },
  "ownership": "unico_dono",
  "images": [
    "https://s3.../img1.jpg",
    "https://s3.../img2.jpg"
  ]
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Honda Civic Touring 2024/2024 - Único Dono",
    "price": 135000.00,
    "status": "active",
    "created_at": "2026-03-17T10:00:00Z"
  },
  "message": "Vehicle created successfully"
}
```

---

#### GET /vehicles/{id}
Get vehicle details.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "dealership_id": "uuid",
    "title": "Honda Civic Touring 2024/2024",
    "description": "Veículo impecável...",
    "brand": "Honda",
    "model": "Civic",
    "year": 2024,
    "model_year": 2024,
    "version": "Touring 2.0 16V Flex Aut.",
    "color": "Branco Pérola",
    "mileage": 15000,
    "plate": "ABC1234",
    "doors": 4,
    "seats": 5,
    "fuel_type": "flex",
    "transmission": "automatic",
    "body_type": "sedan",
    "price": 135000.00,
    "price_market": 140000.00,
    "price_score": 85,
    "price_position": "below_market",
    "features": {
      "security": ["airbags", "abs"],
      "comfort": ["ar_condicionado"],
      "technology": ["android_auto"],
      "extras": ["teto_solar"]
    },
    "ownership": "unico_dono",
    "images": [
      {
        "url": "https://s3.../img1.jpg",
        "type": "front",
        "is_primary": true
      }
    ],
    "main_image": "https://s3.../img1.jpg",
    "status": "active",
    "ai_analysis": {
      "score": 85,
      "price_position": "below_market",
      "selling_points": ["unico_dono"],
      "target_audience": ["familias"],
      "suggested_improvements": ["mais_fotos"],
      "estimated_ctr": 0.035,
      "estimated_conversion": 0.028
    },
    "ads": [
      {
        "id": "uuid",
        "platform": "facebook",
        "status": "active"
      }
    ],
    "created_at": "2026-03-17T10:00:00Z",
    "updated_at": "2026-03-17T10:00:00Z"
  }
}
```

---

#### PUT /vehicles/{id}
Update vehicle information.

**Request Body:** (same as POST /vehicles, all fields optional)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Honda Civic Touring 2024/2024 - Atualizado",
    "updated_at": "2026-03-17T11:00:00Z"
  },
  "message": "Vehicle updated successfully"
}
```

---

#### DELETE /vehicles/{id}
Delete a vehicle (soft delete).

**Response (200):**
```json
{
  "success": true,
  "message": "Vehicle deleted successfully"
}
```

---

#### POST /vehicles/{id}/analyze
Trigger AI analysis for a vehicle.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "vehicle_id": "uuid",
    "analysis": {
      "score": 85,
      "price_position": "below_market",
      "price_range": {
        "min": 130000,
        "market": 140000,
        "max": 145000
      },
      "selling_points": [
        "unico_dono",
        "revisoes_concessionaria",
        "baixa_quilometragem"
      ],
      "target_audience": [
        "familias",
        "profissionais_liberais",
        "motoristas_exigentes"
      ],
      "suggested_improvements": [
        "adicionar_video",
        "fotos_interiores",
        "destacar_garantia"
      ],
      "estimated_performance": {
        "ctr": {
          "min": 0.030,
          "avg": 0.035,
          "max": 0.041
        },
        "conversion_rate": {
          "min": 0.025,
          "avg": 0.028,
          "max": 0.032
        },
        "cost_per_lead": {
          "min": 4.00,
          "avg": 4.50,
          "max": 5.20
        }
      }
    }
  },
  "message": "AI analysis completed"
}
```

---

#### POST /vehicles/{id}/images
Upload vehicle images.

**Request:** (multipart/form-data)
```
images: [file1, file2, file3]
main_image_index: 0
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "images": [
      {
        "url": "https://s3.../img1.jpg",
        "type": "front",
        "is_primary": true
      }
    ]
  },
  "message": "Images uploaded successfully"
}
```

---

### 3. Ads APIs

#### GET /ads
List all ads with filters.

**Query Parameters:**
- `page`, `per_page` (pagination)
- `vehicle_id` (UUID)
- `platform` (facebook, google, instagram)
- `status` (draft, active, paused, completed)
- `start_date` (ISO date)
- `end_date` (ISO date)
- `sort_by`, `sort_order`

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "vehicle": {
        "id": "uuid",
        "title": "Honda Civic Touring 2024",
        "main_image": "https://..."
      },
      "platform": "facebook",
      "platform_ad_id": "23845678901234567",
      "status": "active",
      "title": "Honda Civic Touring 2024 - Único Dono",
      "description": "Veículo impecável...",
      "call_to_action": "Agendar Test-Drive",
      "budget_daily": 150.00,
      "budget_total": 4500.00,
      "start_date": "2026-03-01T00:00:00Z",
      "end_date": "2026-03-31T23:59:59Z",
      "total_impressions": 45230,
      "total_clicks": 1580,
      "total_spend": 2340.50,
      "total_conversions": 45,
      "created_at": "2026-03-01T10:00:00Z",
      "published_at": "2026-03-01T10:05:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 24
  }
}
```

---

#### POST /ads
Create a new ad (draft).

**Request Body:**
```json
{
  "vehicle_id": "uuid",
  "platform": "facebook",
  "title": "Honda Civic Touring 2024 - Único Dono",
  "description": "Veículo impecável, único dono...",
  "headline": "Honda Civic Touring 2024",
  "call_to_action": "Agendar Test-Drive",
  "images": ["https://s3.../img1.jpg"],
  "target_audience": {
    "age_min": 25,
    "age_max": 55,
    "genders": ["male", "female"],
    "locations": [
      {"city": "São Paulo", "radius": 30}
    ],
    "interests": ["automotive", "honda", "sedan"]
  },
  "budget_daily": 150.00,
  "budget_total": 4500.00,
  "start_date": "2026-03-01T00:00:00Z",
  "end_date": "2026-03-31T23:59:59Z"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "draft",
    "platform": "facebook",
    "created_at": "2026-03-17T10:00:00Z"
  },
  "message": "Ad created successfully"
}
```

---

#### GET /ads/{id}
Get ad details.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "vehicle": {
      "id": "uuid",
      "title": "Honda Civic Touring 2024",
      "brand": "Honda",
      "model": "Civic",
      "year": 2024,
      "price": 135000.00,
      "main_image": "https://..."
    },
    "platform": "facebook",
    "platform_ad_id": "23845678901234567",
    "status": "active",
    "title": "Honda Civic Touring 2024 - Único Dono",
    "description": "Veículo impecável...",
    "headline": "Honda Civic Touring 2024",
    "call_to_action": "Agendar Test-Drive",
    "images": ["https://s3.../img1.jpg"],
    "target_audience": {
      "age_min": 25,
      "age_max": 55,
      "genders": ["male", "female"]
    },
    "budget_daily": 150.00,
    "budget_total": 4500.00,
    "start_date": "2026-03-01T00:00:00Z",
    "end_date": "2026-03-31T23:59:59Z",
    "ai_generated": true,
    "ai_suggestions": {
      "headlines": ["Opção 1", "Opção 2"],
      "estimated_ctr": {"min": 0.035, "max": 0.041}
    },
    "total_impressions": 45230,
    "total_clicks": 1580,
    "total_spend": 2340.50,
    "total_conversions": 45,
    "created_at": "2026-03-01T10:00:00Z",
    "published_at": "2026-03-01T10:05:00Z",
    "metrics": [
      {
        "date": "2026-03-17",
        "impressions": 1523,
        "clicks": 54,
        "ctr": 0.0354,
        "spend": 81.00,
        "conversions": 2
      }
    ]
  }
}
```

---

#### PUT /ads/{id}
Update ad.

**Request Body:** (same as POST /ads, all fields optional)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "updated_at": "2026-03-17T11:00:00Z"
  },
  "message": "Ad updated successfully"
}
```

---

#### DELETE /ads/{id}
Delete ad.

**Response (200):**
```json
{
  "success": true,
  "message": "Ad deleted successfully"
}
```

---

#### POST /ads/{id}/publish
Publish ad to platform.

**Request Body:**
```json
{
  "platforms": ["facebook", "instagram"]
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "ad_id": "uuid",
    "status": "active",
    "platform_ad_ids": {
      "facebook": "23845678901234567",
      "instagram": "23845678901234568"
    },
    "published_at": "2026-03-17T10:05:00Z"
  },
  "message": "Ad published successfully to 2 platforms"
}
```

---

#### POST /ads/{id}/pause
Pause active ad.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "ad_id": "uuid",
    "status": "paused",
    "paused_at": "2026-03-17T10:00:00Z"
  },
  "message": "Ad paused successfully"
}
```

---

#### POST /ads/{id}/resume
Resume paused ad.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "ad_id": "uuid",
    "status": "active",
    "resumed_at": "2026-03-17T10:00:00Z"
  },
  "message": "Ad resumed successfully"
}
```

---

#### GET /ads/{id}/metrics
Get ad metrics.

**Query Parameters:**
- `start_date` (ISO date, required)
- `end_date` (ISO date, required)
- `granularity` (day, week, month) - default: day

**Example:**
```http
GET /api/v1/ads/uuid/metrics?start_date=2026-03-01&end_date=2026-03-17&granularity=day
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "ad_id": "uuid",
    "platform": "facebook",
    "period": {
      "start": "2026-03-01",
      "end": "2026-03-17"
    },
    "summary": {
      "total_impressions": 45230,
      "total_clicks": 1580,
      "avg_ctr": 0.0349,
      "total_spend": 2340.50,
      "total_conversions": 45,
      "conversion_rate": 0.0285,
      "cost_per_click": 1.48,
      "cost_per_conversion": 52.01,
      "total_revenue": 121500.00,
      "roi": 50.91,
      "roas": 51.91
    },
    "metrics": [
      {
        "date": "2026-03-01",
        "impressions": 2654,
        "clicks": 93,
        "ctr": 0.0350,
        "spend": 137.50,
        "conversions": 3,
        "conversion_rate": 0.0323,
        "cost_per_click": 1.48,
        "cost_per_conversion": 45.83
      }
    ]
  }
}
```

---

### 4. Metrics & Analytics APIs

#### GET /metrics/dashboard
Get dashboard metrics summary.

**Query Parameters:**
- `period` (today, yesterday, last_7_days, last_30_days, last_90_days, this_month, last_month, custom)
- `start_date` (ISO date) - required if period=custom
- `end_date` (ISO date) - required if period=custom

**Example:**
```http
GET /api/v1/metrics/dashboard?period=last_30_days
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "period": {
      "start": "2026-02-15",
      "end": "2026-03-17"
    },
    "overview": {
      "total_vehicles": 24,
      "active_ads": 18,
      "total_impressions": 1523450,
      "total_clicks": 52890,
      "avg_ctr": 0.0347,
      "total_spend": 78543.20,
      "total_conversions": 1456,
      "conversion_rate": 0.0275,
      "total_revenue": 2184000.00,
      "avg_roi": 26.81,
      "cost_per_lead": 53.94
    },
    "by_platform": [
      {
        "platform": "facebook",
        "impressions": 892340,
        "clicks": 32890,
        "ctr": 0.0369,
        "spend": 48234.50,
        "conversions": 890,
        "roi": 32.45
      },
      {
        "platform": "google",
        "impressions": 631110,
        "clicks": 20000,
        "ctr": 0.0317,
        "spend": 30308.70,
        "conversions": 566,
        "roi": 19.82
      }
    ],
    "top_vehicles": [
      {
        "vehicle_id": "uuid",
        "title": "Honda Civic Touring 2024",
        "image": "https://...",
        "impressions": 152340,
        "clicks": 5289,
        "conversions": 145,
        "roi": 38.45,
        "revenue": 218000.00
      }
    ],
    "performance_chart": [
      {
        "date": "2026-02-15",
        "impressions": 45230,
        "clicks": 1580,
        "conversions": 45,
        "spend": 2340.50
      }
    ]
  }
}
```

---

#### GET /metrics/roi
Get ROI metrics.

**Query Parameters:**
- `start_date`, `end_date`
- `group_by` (vehicle, ad, platform)
- `sort_by` (roi, revenue, conversions)

**Example:**
```http
GET /api/v1/metrics/roi?start_date=2026-03-01&end_date=2026-03-17&group_by=vehicle&sort_by=roi
```

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "vehicle_id": "uuid",
      "title": "Honda Civic Touring 2024",
      "total_spend": 2340.50,
      "total_revenue": 121500.00,
      "total_conversions": 45,
      "roi": 50.91,
      "roas": 51.91,
      "cost_per_conversion": 52.01
    }
  ]
}
```

---

### 5. AI Agent APIs

#### POST /ai/analyze-vehicle
Analyze vehicle with AI.

**Request Body:**
```json
{
  "vehicle_id": "uuid"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "vehicle_id": "uuid",
    "analysis": {
      "score": 85,
      "price_analysis": {
        "current_price": 135000.00,
        "market_range": {
          "min": 130000,
          "avg": 140000,
          "max": 145000
        },
        "position": "below_market",
        "score": 85,
        "discount_percent": 3.57
      },
      "selling_points": [
        "Único dono",
        "Todas revisões na concessionária",
        "Baixa quilometragem (15.000 km)",
        "Garantia de fábrica vigente"
      ],
      "target_audience": [
        "Famílias de classe média/alta",
        "Profissionais liberais",
        "Motoristas exigentes com foco em conforto e segurança"
      ],
      "improvements": [
        "Adicionar vídeo walkaround do veículo",
        "Mais fotos do interior",
        "Destacar itens de série na descrição",
        "Incluir informações sobre garantia"
      ],
      "performance_prediction": {
        "ctr": {
          "min": 0.030,
          "avg": 0.035,
          "max": 0.041,
          "confidence": 0.85
        },
        "conversion_rate": {
          "min": 0.025,
          "avg": 0.028,
          "max": 0.032,
          "confidence": 0.82
        },
        "cost_per_lead": {
          "min": 4.00,
          "avg": 4.50,
          "max": 5.20,
          "currency": "BRL"
        },
        "estimated_monthly_leads": {
          "min": 35,
          "avg": 45,
          "max": 55
        }
      },
      "competitor_analysis": {
        "avg_price": 142000.00,
        "price_difference": -7000.00,
        "competitor_count": 12
      }
    }
  }
}
```

---

#### POST /ai/generate-ad
Generate ad content with AI.

**Request Body:**
```json
{
  "vehicle_id": "uuid",
  "platform": "facebook",
  "target_audience": ["familias", "profissionais_liberais"],
  "tone": "professional",
  "max_headlines": 3,
  "max_descriptions": 2
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "vehicle_id": "uuid",
    "platform": "facebook",
    "generated_content": {
      "headlines": [
        {
          "text": "Honda Civic Touring 2024 - Único Dono - Impecável",
          "character_count": 56,
          "score": 0.92
        },
        {
          "text": "Civic 2024 Completo - Único Dono - Garantia de Fábrica",
          "character_count": 58,
          "score": 0.88
        },
        {
          "text": "Honda Civic Touring - Revisões na Concessionária",
          "character_count": 52,
          "score": 0.85
        }
      ],
      "descriptions": [
        {
          "text": "Honda Civic Touring 2024/2024, único dono, 15.000km. Todas revisões na concessionária Honda. Completo: teto solar, bancos em couro, central multimídia, Android Auto/CarPlay. Garantia de fábrica até 2026. Financiamento em até 60x. Agende seu test-drive!",
          "character_count": 228,
          "score": 0.90
        },
        {
          "text": "Civic Touring impecável! Único dono, todas revisões na concessionária. 4 portas, automático, flex. Opcionais: teto solar solar, piloto automático, câmera de ré, sensores. Aceita troca. Parcelamos em até 60x sem juros.",
          "character_count": 215,
          "score": 0.87
        }
      ],
      "call_to_actions": [
        "Agendar Test-Drive",
        "Saber Mais",
        "Ver Detalhes"
      ],
      "targeting_suggestions": {
        "age_range": {
          "min": 28,
          "max": 55,
          "reason": "Poder aquisitivo compatível com o valor do veículo"
        },
        "locations": [
          {
            "city": "São Paulo",
            "radius": 30,
            "reason": "Área de cobertura da revenda"
          }
        ],
        "interests": [
          "Automotive",
          "Honda",
          "New cars",
          "Compact cars",
          "Car accessories"
        ],
        "behaviors": [
          "Car buyers (recent)",
          "Luxury shoppers"
        ]
      },
      "budget_recommendation": {
        "daily_min": 100.00,
        "daily_recommended": 150.00,
        "daily_max": 200.00,
        "estimated_reach": {
          "min": 30000,
          "avg": 45000,
          "max": 60000
        },
        "reason": "Para atingir 40-60K pessoas no público-alvo"
      }
    },
    "performance_prediction": {
      "ctr": {
        "min": 0.035,
        "avg": 0.038,
        "max": 0.042
      },
      "conversions": {
        "min": 38,
        "avg": 45,
        "max": 52
      },
      "cost_per_lead": {
        "min": 4.20,
        "avg": 4.50,
        "max": 4.90
      }
    }
  }
}
```

---

#### POST /ai/optimize
Get AI suggestions to optimize existing ad.

**Request Body:**
```json
{
  "ad_id": "uuid",
  "optimization_type": "all"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "ad_id": "uuid",
    "current_performance": {
      "ctr": 0.028,
      "conversion_rate": 0.022,
      "cost_per_lead": 5.80,
      "benchmark_ctr": 0.035,
      "benchmark_conversion": 0.028
    },
    "optimizations": [
      {
        "type": "creative",
        "priority": "high",
        "current": "Headline atual",
        "suggestion": "Nova headline mais impactante",
        "expected_improvement": "+15% CTR",
        "confidence": 0.85
      },
      {
        "type": "targeting",
        "priority": "medium",
        "current": {"age_min": 25, "age_max": 55},
        "suggestion": {"age_min": 28, "age_max": 50},
        "expected_improvement": "+10% conversion",
        "confidence": 0.78
      },
      {
        "type": "budget",
        "priority": "low",
        "current": 100.00,
        "suggestion": 150.00,
        "expected_improvement": "+50% reach",
        "confidence": 0.92
      }
    ],
    "overall_score": 72,
    "potential_roi_improvement": "+25%"
  }
}
```

---

#### GET /ai/predict
Get performance prediction for ad.

**Query Parameters:**
- `vehicle_id` (UUID, required)
- `platform` (string, required)
- `budget_daily` (decimal, required)
- `duration_days` (integer, required)

**Example:**
```http
GET /api/v1/ai/predict?vehicle_id=uuid&platform=facebook&budget_daily=150&duration_days=30
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "vehicle_id": "uuid",
    "platform": "facebook",
    "budget": {
      "daily": 150.00,
      "total": 4500.00
    },
    "duration_days": 30,
    "predictions": {
      "impressions": {
        "min": 1200000,
        "avg": 1500000,
        "max": 1800000
      },
      "clicks": {
        "min": 42000,
        "avg": 52500,
        "max": 63000
      },
      "ctr": {
        "min": 0.030,
        "avg": 0.035,
        "max": 0.040
      },
      "conversions": {
        "min": 1050,
        "avg": 1312,
        "max": 1575
      },
      "conversion_rate": {
        "min": 0.025,
        "avg": 0.028,
        "max": 0.032
      },
      "cost_per_click": {
        "min": 0.08,
        "avg": 0.09,
        "max": 0.10
      },
      "cost_per_conversion": {
        "min": 2.86,
        "avg": 3.43,
        "max": 4.29
      },
      "roi": {
        "min": 25.5,
        "avg": 30.2,
        "max": 35.8
      }
    },
    "confidence": 0.85,
    "model_version": "v1.2.0"
  }
}
```

---

### 6. Integration APIs

#### POST /integrations/facebook/connect
Connect Facebook Ads account.

**Request Body:**
```json
{
  "access_token": "EAABwz...",
  "account_id": "act_123456789",
  "business_id": "123456789"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "platform": "facebook",
    "account_id": "act_123456789",
    "account_name": "Auto Premium Ads",
    "status": "active",
    "connected_at": "2026-03-17T10:00:00Z"
  },
  "message": "Facebook Ads account connected successfully"
}
```

---

#### POST /integrations/google/connect
Connect Google Ads account.

**Request Body:**
```json
{
  "refresh_token": "1//0g...",
  "customer_id": "123-456-7890",
  "developer_token": "YOUR_DEVELOPER_TOKEN"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "platform": "google",
    "customer_id": "123-456-7890",
    "account_name": "Auto Premium",
    "status": "active",
    "connected_at": "2026-03-17T10:00:00Z"
  },
  "message": "Google Ads account connected successfully"
}
```

---

#### GET /integrations/{platform}/accounts
List connected accounts for platform.

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "platform": "facebook",
      "account_id": "act_123456789",
      "account_name": "Auto Premium Ads",
      "status": "active",
      "last_sync_at": "2026-03-17T09:00:00Z"
    }
  ]
}
```

---

#### DELETE /integrations/{platform}/disconnect
Disconnect platform account.

**Response (200):**
```json
{
  "success": true,
  "message": "Account disconnected successfully"
}
```

---

#### POST /integrations/{platform}/sync
Manually trigger sync with platform.

**Query Parameters:**
- `sync_type` (metrics, ads, all) - default: all

**Response (200):**
```json
{
  "success": true,
  "data": {
    "sync_id": "uuid",
    "status": "running",
    "started_at": "2026-03-17T10:00:00Z"
  },
  "message": "Sync started successfully"
}
```

---

### 7. User & Dealership Management APIs

#### GET /users/me
Get current user profile.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "João Silva",
    "email": "joao@autopremium.com.br",
    "role": "manager",
    "dealership": {
      "id": "uuid",
      "name": "Auto Premium Ltda",
      "status": "active"
    },
    "permissions": [
      "vehicles:create",
      "vehicles:edit",
      "ads:publish",
      "metrics:view"
    ]
  }
}
```

---

#### PUT /users/me
Update current user profile.

**Request Body:**
```json
{
  "name": "João Silva Jr.",
  "phone": "+55 11 98765-4321"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "João Silva Jr.",
    "updated_at": "2026-03-17T10:00:00Z"
  }
}
```

---

#### PUT /users/me/password
Change password.

**Request Body:**
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewPass456!"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

#### GET /dealerships/me
Get current dealership information.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Auto Premium Ltda",
    "trade_name": "Auto Premium",
    "document_id": "12.345.678/0001-90",
    "email": "contato@autopremium.com.br",
    "phone": "+55 11 3456-7890",
    "whatsapp": "+55 11 98765-4321",
    "address": {
      "street": "Av. Paulista",
      "number": "1000",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01310-100"
    },
    "status": "active",
    "settings": {
      "timezone": "America/Sao_Paulo",
      "currency": "BRL",
      "notifications_enabled": true
    },
    "created_at": "2026-01-01T10:00:00Z"
  }
}
```

---

#### PUT /dealerships/me
Update dealership information.

**Request Body:** (same structure as GET response)

**Response (200):**
```json
{
  "success": true,
  "message": "Dealership updated successfully"
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Invalid input data |
| `AUTHENTICATION_ERROR` | Invalid or missing token |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `CONFLICT` | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Internal server error |
| `SERVICE_UNAVAILABLE` | External service unavailable |
| `PLATFORM_ERROR` | Platform API error (Facebook, Google) |

---

## Rate Limiting

- **Default**: 100 requests per minute per user
- **Burst**: 200 requests per minute
- **Headers**:
  - `X-RateLimit-Limit`: Total limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset time (Unix timestamp)

---

## Webhooks (Future)

### POST /webhooks
Register webhook URL.

**Request Body:**
```json
{
  "url": "https://yourapp.com/webhooks",
  "events": ["ad.published", "ad.completed", "vehicle.sold"]
}
```

### Webhook Events

- `ad.published`: Ad published to platform
- `ad.paused`: Ad paused
- `ad.completed`: Ad completed
- `vehicle.sold`: Vehicle sold
- `metrics.updated`: Metrics updated

---

## WebSocket API (Real-time Updates)

### Connect

```javascript
const ws = new WebSocket('wss://api.caradsplatform.com/ws');

ws.onopen = () => {
  // Send auth token
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'jwt_token_here'
  }));
};
```

### Subscribe to Updates

```javascript
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['ad_metrics', 'vehicle_updates']
}));
```

### Message Format

```json
{
  "type": "ad_metrics_update",
  "data": {
    "ad_id": "uuid",
    "impressions": 1523,
    "clicks": 54,
    "ctr": 0.0354
  },
  "timestamp": "2026-03-17T10:00:00Z"
}
```

---

## SDK Examples

### Python (httpx)

```python
import httpx

client = httpx.AsyncClient(
    base_url="https://api.caradsplatform.com/api/v1",
    headers={"Authorization": f"Bearer {token}"}

# List vehicles
response = await client.get("/vehicles")
vehicles = response.json()["data"]

# Create ad
ad_data = {
    "vehicle_id": vehicle_id,
    "platform": "facebook",
    "title": "My Ad",
    "budget_daily": 150.00
}
response = await client.post("/ads", json=ad_data)
ad = response.json()["data"]
```

### JavaScript (axios)

```javascript
import axios from 'axios';

const client = axios.create({
  baseURL: 'https://api.caradsplatform.com/api/v1',
  headers: { 'Authorization': `Bearer ${token}` }
});

// List vehicles
const { data } = await client.get('/vehicles');
const vehicles = data.data;

// Create ad
const adData = {
  vehicle_id: vehicleId,
  platform: 'facebook',
  title: 'My Ad',
  budget_daily: 150.00
};
const response = await client.post('/ads', adData);
const ad = response.data.data;
```

---

## Próximos Passos

1. ✅ API Specification completa
2. ⏳ Implementar modelos Pydantic
3. ⏳ Criar endpoints FastAPI
4. ⏳ Implementar repositórios
5. ⏳ Adicionar testes
6. ⏳ Documentação interativa (Swagger/ReDoc)
7. ⏳ SDK Python e JavaScript
