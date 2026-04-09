# Arquitetura do Sistema - Car Ads Platform

## Overview

Sistema completo de anúncios patrocinados para revenda de carros, utilizando IA para otimização automática de anúncios e maximização de ROI.

---

## 1. Arquitetura Geral

### Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│                      (Next.js + React)                          │
│                    • Dashboard & Analytics                      │
│                    • Vehicle Management                         │
│                    • Ad Creation Wizard                         │
│                    • Real-time Metrics                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTPS/WSS
┌─────────────────────────────┴───────────────────────────────────┐
│                       API Gateway                                │
│                      (NGINX / Kong)                              │
│                    • Rate Limiting                               │
│                    • Load Balancing                              │
│                    • SSL Termination                             │
│                    • Request Routing                             │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌────────▼─────────┐  ┌───────▼─────────┐
│  Core API      │  │   AI Agent       │  │  Ads Integ.     │
│  (FastAPI)     │  │   Service        │  │  Service        │
│                │  │                  │  │                 │
│ - Veículos     │  │ - Análise AI     │  │ - Facebook Ads  │
│ - Anúncios     │  │ - Geração        │  │ - Google Ads    │
│ - Métricas     │  │ - Scoring        │  │ - Instagram     │
│ - Usuários     │  │ - Previsões      │  │ - TikTok (fut)  │
│                │  │ - Otimização     │  │                 │
└───────┬────────┘  └────────┬─────────┘  └────────┬─────────┘
        │                     │                     │
        │ HTTP/REST           │ HTTP/REST           │ HTTP/REST
        │ WebSocket           │                     │
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                       Data Layer                                 │
│  ┌─────────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│  │ PostgreSQL  │  │  Redis   │  │  S3/MinIO│  │ ClickHouse  │  │
│  │ (Primary)   │  │ (Cache)  │  │ (Images) │  │ (Analytics) │  │
│  │             │  │          │  │          │  │             │  │
│  │ - Dealers   │  │ - Cache  │  │ - Media  │  │ - Events    │  │
│  │ - Vehicles  │  │ - Queue  │  │ - Backup │  │ - Metrics   │  │
│  │ - Ads       │  │ - Session│  │          │  │ - Reports   │  │
│  │ - Users     │  │          │  │          │  │             │  │
│  └─────────────┘  └──────────┘  └──────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Camadas da Arquitetura

#### 1. Frontend Layer
- **Next.js 14** (App Router)
  - Server Components para performance
  - Client Components para interatividade
  - SSR/SSG para SEO
  - API Routes para BFF pattern

#### 2. API Gateway
- **NGINX** / **Kong**
  - Reverse proxy
  - Load balancing
  - Rate limiting
  - SSL/TLS termination
  - CORS management
  - Request routing

#### 3. Microservices Layer

##### Core API Service
**Responsabilidade**: Gerenciamento core do negócio
- Veículos e inventário
- Anúncios e campanhas
- Usuários e permissões
- Métricas e relatórios

**Tech Stack**:
- FastAPI (Python 3.11+)
- SQLAlchemy 2.0 (async)
- Pydantic v2
- Alembic (migrations)

##### AI Agent Service
**Responsabilidade**: Inteligência artificial e ML
- Análise de veículos
- Geração de conteúdo
- Scoring e previsões
- Otimização automática

**Tech Stack**:
- FastAPI (Python 3.11+)
- LangChain / LlamaIndex
- Claude API / OpenAI GPT-4
- scikit-learn / XGBoost
- pgvector (vector search)

##### Ads Integration Service
**Responsabilidade**: Integração com plataformas de ads
- Facebook Ads
- Google Ads
- Instagram
- TikTok (future)

**Tech Stack**:
- FastAPI (Python 3.11+)
- Facebook Business SDK
- Google Ads API
- Celery (async tasks)

#### 4. Data Layer

##### PostgreSQL 16
**Banco de dados primário**
- Dados transacionais
- Relacionamentos
- ACID compliance
- pgvector para busca vetorial

##### Redis 7
**Cache e mensagem broker**
- Cache de queries frequentes
- Session storage
- Celery broker
- Feature store para ML

##### S3 / MinIO
**Armazenamento de objetos**
- Imagens de veículos
- Criativos de anúncios
- Relatórios exportados
- Backup de dados

##### ClickHouse (Opcional)
**Analytics database**
- Métricas de anúncios
- Event tracking
- Dashboards em tempo real
- Data warehouse

---

## 2. Stack Tecnológica

### Backend Stack

| Componente | Tecnologia | Versão | Justificativa |
|------------|-----------|--------|---------------|
| **Framework** | FastAPI | 0.104+ | Async nativo, performance, type hints |
| **Runtime** | Python | 3.11+ | Features modernas, performance |
| **ORM** | SQLAlchemy | 2.0+ | Async support, maduro, estável |
| **Validação** | Pydantic | 2.0+ | Validação de dados, type hints |
| **Auth** | JWT + OAuth2 | - | Padrão da indústria, seguro |
| **Task Queue** | Celery | 5.3+ | Processamento async, robusto |
| **WebSocket** | FastAPI WebSockets | - | Comunicação real-time |
| **Migrations** | Alembic | 1.12+ | Controle de versão do DB |
| **HTTP Client** | httpx | 0.25+ | Async HTTP requests |
| **Testing** | pytest + pytest-asyncio | - | Testing framework moderno |

### Frontend Stack

| Componente | Tecnologia | Versão | Justificativa |
|------------|-----------|--------|---------------|
| **Framework** | Next.js | 14 (App Router) | SSR/SSG, performance, SEO |
| **UI Library** | shadcn/ui | latest | Componentes modernos, customizáveis |
| **Styling** | TailwindCSS | 3.3+ | Utility-first, rápido desenvolvimento |
| **State Global** | Zustand | 4.4+ | Leve, simples, TypeScript-first |
| **Server State** | React Query | 5.0+ | Cache, sync com servidor |
| **Forms** | React Hook Form | 7.45+ | Performance, validation |
| **Validation** | Zod | 3.22+ | Type-safe validation |
| **Charts** | Recharts | 2.8+ | Composable, declarativo |
| **HTTP Client** | axios / fetch | - | Requests HTTP |

### Database & Cache Stack

| Componente | Tecnologia | Versão | Uso |
|------------|-----------|--------|-----|
| **Primary DB** | PostgreSQL | 16 | Dados transacionais |
| **Cache** | Redis | 7 | Cache, sessions, queue |
| **Vector DB** | pgvector | 0.5+ | Busca semântica |
| **Analytics** | ClickHouse | 23+ | Métricas e eventos (opcional) |
| **Object Storage** | MinIO / S3 | - | Imagens e arquivos |

### AI/ML Stack

| Componente | Tecnologia | Uso |
|------------|-----------|-----|
| **LLM** | Claude API (Anthropic) | Geração de conteúdo, análise |
| **Alternative** | OpenAI GPT-4 | Backup LLM |
| **Vector Store** | pgvector | Embeddings, busca semântica |
| **ML Framework** | scikit-learn | Modelos de ML tradicional |
| **Gradient Boosting** | XGBoost | Previsões, scoring |
| **Feature Store** | Redis | Cache de features |

### Infrastructure Stack

| Componente | Tecnologia | Uso |
|------------|-----------|-----|
| **Container** | Docker | Containerização |
| **Orchestration** | Docker Compose | Desenvolvimento local |
| **Reverse Proxy** | NGINX | Load balancing, routing |
| **Monitoring** | Prometheus | Metrics collection |
| **Visualization** | Grafana | Dashboards de monitoramento |
| **Logging** | ELK Stack | Logs centralizados |
| **CI/CD** | GitHub Actions | Pipeline de deploy |
| **Quality** | SonarQube | Code quality (opcional) |

---

## 3. Design Patterns

### Patterns Utilizados

#### 1. Repository Pattern
```python
# Abstract base repository
class BaseRepository(Generic[T]):
    async def get(self, id: UUID) -> T | None:
        ...

    async def list(self, **filters) -> list[T]:
        ...

    async def create(self, obj: T) -> T:
        ...

    async def update(self, id: UUID, **data) -> T | None:
        ...

    async def delete(self, id: UUID) -> bool:
        ...
```

#### 2. Service Layer Pattern
```python
# Business logic separation
class VehicleService:
    def __init__(self, repository: VehicleRepository):
        self.repository = repository

    async def create_vehicle(self, data: VehicleCreate) -> Vehicle:
        # Business logic
        vehicle = await self.repository.create(data)
        # Trigger AI analysis
        await self.ai_service.analyze_vehicle(vehicle)
        return vehicle
```

#### 3. Dependency Injection
```python
# FastAPI Depends
@router.post("/vehicles")
async def create_vehicle(
    data: VehicleCreate,
    service: VehicleService = Depends(get_vehicle_service)
):
    return await service.create_vehicle(data)
```

#### 4. Factory Pattern (AI Agents)
```python
class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str) -> BaseAgent:
        if agent_type == "analyzer":
            return AnalyzerAgent()
        elif agent_type == "generator":
            return GeneratorAgent()
        # ...
```

#### 5. Observer Pattern (Real-time Updates)
```python
# WebSocket for real-time metrics
class MetricsBroadcaster:
    async def broadcast_update(self, ad_id: UUID, metrics: AdMetrics):
        # Send to all connected clients
        ...
```

#### 6. Strategy Pattern (Ad Platforms)
```python
class AdPlatformStrategy(ABC):
    @abstractmethod
    async def publish_ad(self, ad: Ad) -> str:
        ...

class FacebookAdPlatform(AdPlatformStrategy):
    async def publish_ad(self, ad: Ad) -> str:
        # Facebook-specific implementation
        ...

class GoogleAdPlatform(AdPlatformStrategy):
    async def publish_ad(self, ad: Ad) -> str:
        # Google-specific implementation
        ...
```

---

## 4. Segurança

### Autenticação e Autorização

#### JWT-based Authentication
```python
# JWT Token structure
{
  "sub": "user_id",
  " dealership_id": "dealership_id",
  "role": "manager",
  "exp": 1234567890,
  "iat": 1234567890
}
```

#### Role-based Access Control (RBAC)
- **Admin**: Acesso total
- **Manager**: Gerencia veículos e anúncios
- **User**: Visualização apenas

#### Security Best Practices
1. **Password Hashing**: bcrypt com salt
2. **SQL Injection Prevention**: ORM (SQLAlchemy)
3. **XSS Protection**: Input sanitization, CSP headers
4. **CSRF Protection**: Tokens for state-changing operations
5. **Rate Limiting**: Por usuário e por IP
6. **HTTPS Only**: TLS 1.3
7. **Data Encryption**: Sensitive data encrypted at rest
8. **API Keys**: Secure storage, rotation

---

## 5. Performance & Scalability

### Optimization Strategies

#### Backend
1. **Async/Await**: Non-blocking I/O
2. **Connection Pooling**: Database connection reuse
3. **Caching**: Redis para queries frequentes
4. **Database Indexing**: Índices otimizados
5. **Query Optimization**: N+1 prevention
6. **Pagination**: Limit response size

#### Frontend
1. **Code Splitting**: Lazy loading de rotas
2. **Image Optimization**: WebP, lazy load
3. **Server Components**: Reduz bundle size
4. **Memoization**: React.memo, useMemo
5. **Virtual Scrolling**: Para listas longas

#### Database
1. **Read Replicas**: Distribuir carga de leitura
2. **Partitioning**: Dividir tabelas grandes
3. **Connection Pooling**: pg_bouncer
4. **Query Caching**: PostgreSQL query cache

---

## 6. Monitoramento & Logging

### Metrics Collection

#### Application Metrics
- Request rate
- Response time
- Error rate
- Database query time
- Cache hit rate
- Active users

#### Business Metrics
- Active ads
- Total spend
- ROI per ad
- Conversion rate
- CTR distribution

### Monitoring Stack
```
Application → Prometheus → Grafana
                    ↓
              AlertManager
```

### Logging Strategy
```
Application → File → Logstash → Elasticsearch → Kibana
```

#### Log Levels
- **ERROR**: Erros que precisam de atenção
- **WARNING**: Situações anormais, não críticas
- **INFO**: Eventos importantes de negócio
- **DEBUG**: Informação detalhada para debugging

---

## 7. Deploy & DevOps

### Deployment Strategy

#### Development
```bash
docker-compose up
```

#### Staging/Production
```bash
# CI/CD Pipeline
1. Run tests
2. Build Docker images
3. Push to registry
4. Deploy to staging
5. Run integration tests
6. Deploy to production (blue-green)
```

### Infrastructure as Code (Future)
- **Terraform**: Para provisionar infraestrutura cloud
- **Ansible**: Para configuração de servidores
- **Kubernetes**: Para orquestração de containers (scale)

---

## 8. Arquitetura de Microserviços

### Comunicação entre Serviços

#### Síncrona (HTTP/REST)
```python
# Core API → AI Service
response = await httpx.post(
    "http://ai-service/api/v1/ai/analyze-vehicle",
    json={"vehicle_id": str(vehicle_id)}
)
analysis = response.json()
```

#### Assíncrona (Message Queue)
```python
# Celery tasks
@celery_app.task
def analyze_vehicle_async(vehicle_id: UUID):
    # Background processing
    analysis = ai_service.analyze_vehicle(vehicle_id)
    # Notify via WebSocket
    websocket_manager.broadcast(analysis)
```

### Service Discovery (Future)
- **Consul**: Service registration and discovery
- **Load Balancing**: Automatic between instances

---

## 9. Data Flow Examples

### Creating a Vehicle with AI Analysis

```
User (Frontend)
    │ POST /api/v1/vehicles
    ▼
API Gateway
    │ Route to Core API
    ▼
Core API
    │ 1. Validate data (Pydantic)
    │ 2. Save to PostgreSQL
    │ 3. Trigger Celery task
    ▼
Celery Worker
    │ 4. Call AI Service
    ▼
AI Service
    │ 5. Analyze with LLM
    │ 6. Score with ML
    │ 7. Save analysis
    │ 8. Notify via WebSocket
    ▼
Frontend
    │ 9. Real-time update
```

### Publishing an Ad

```
User (Frontend)
    │ POST /api/v1/ads/{id}/publish
    ▼
API Gateway
    │ Route to Ads Integration Service
    ▼
Ads Integration Service
    │ 1. Get ad details
    │ 2. Generate platform-specific format
    │ 3. Call Facebook/Google API
    │ 4. Get platform_ad_id
    │ 5. Update ad status
    │ 6. Schedule metrics sync
    ▼
Celery Worker (Periodic)
    │ 7. Fetch metrics from platform
    │ 8. Store in PostgreSQL/ClickHouse
    │ 9. Calculate ROI
    ▼
Frontend
    │ 10. Display updated metrics
```

---

## 10. Tecnologias Específicas por Área

### Core API Dependencies
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
pydantic==2.5.0
pydantic-settings==2.1.0
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
celery==5.3.4
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
```

### AI Service Dependencies
```txt
# Plus Core API dependencies
anthropic==0.7.8
openai==1.3.7
langchain==0.0.335
scikit-learn==1.3.2
xgboost==2.0.2
numpy==1.26.2
pandas==2.1.4
pgvector==0.2.4
```

### Frontend Dependencies
```json
{
  "dependencies": {
    "next": "14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.12.2",
    "zustand": "^4.4.7",
    "react-hook-form": "^7.48.2",
    "zod": "^3.22.4",
    "@hookform/resolvers": "^3.3.2",
    "recharts": "^2.8.0",
    "tailwindcss": "^3.3.6",
    "axios": "^1.6.2",
    "lucide-react": "^0.294.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.1.0"
  }
}
```

---

## 11. Próximos Passos

1. ✅ Arquitetura definida
2. ✅ Stack tecnológica escolhida
3. ⏳ Implementar schema do banco de dados
4. ⏳ Criar APIs Core
5. ⏳ Desenvolver AI Service
6. ⏳ Implementar integrações com plataformas
7. ⏳ Desenvolver Frontend
8. ⏳ Setup de monitoramento e logging
9. ⏳ Testes E2E
10. ⏳ Deploy e otimização
