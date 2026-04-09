# Tecnologias Necessárias - Stack Tecnológico

**Data**: 16/03/2026
**Versão**: 1.0

---

## 1. Visão Geral

Este documento define todas as tecnologias necessárias para construir o sistema, desde backend até infraestrutura, incluindo justificativas para cada escolha.

---

## 2. Stack Tecnológico Principal

### 2.1 Backend

#### Opção A: Python (FastAPI) ⭐ **RECOMENDADO**

**Framework**: FastAPI

**Justificativa**:
- ✓ Moderno, rápido e type-safe
- ✓ Documentação automática (OpenAPI/Swagger)
- ✓ Suporte nativo a async/await
- ✓ Excelente para APIs REST
- ✓ Ecossistema rico de bibliotecas
- ✓ Ideal para projetos com IA/ML

**Principais Bibliotecas**:
```python
# Core
fastapi          # Framework web
uvicorn          # Servidor ASGI
pydantic         # Validação de dados

# Database
sqlalchemy       # ORM
alembic          # Migrações
asyncpg          # PostgreSQL async
redis            # Cache

# Autenticação
python-jose      # JWT tokens
passlib          # Hash de senhas
python-multipart # Upload de arquivos

# IA/ML
openai           # API OpenAI
anthropic        # API Claude
langchain        # Orchestration de LLMs
scikit-learn     # Machine learning
pandas           # Análise de dados
numpy            # Computação numérica

# Ads APIs
facebook-business # Facebook Marketing API
google-ads       # Google Ads API

# Utilidades
requests         # HTTP client
httpx            # HTTP async
aiofiles         # Arquivos async
python-dotenv    # Variáveis de ambiente
celery           # Filas de tarefas
pytest           # Testes
```

**Estrutura de Pastas**:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── config.py            # Configurações
│   ├── dependencies.py      # Dependências
│   │
│   ├── api/                 # Rotas da API
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── veiculos.py
│   │   │   ├── campanhas.py
│   │   │   ├── analise.py
│   │   │   └── dashboard.py
│   │
│   ├── core/                # Core do sistema
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── config.py
│   │   └── deps.py
│   │
│   ├── models/              # Models do banco
│   │   ├── __init__.py
│   │   ├── veiculo.py
│   │   ├── usuario.py
│   │   ├── campanha.py
│   │   └── revenda.py
│   │
│   ├── schemas/             # Schemas Pydantic
│   │   ├── __init__.py
│   │   ├── veiculo.py
│   │   ├── usuario.py
│   │   └── campanha.py
│   │
│   ├── services/            # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── veiculo_service.py
│   │   ├── analise_service.py
│   │   ├── campanha_service.py
│   │   └── ads_service.py
│   │
│   ├── integrations/        # Integrações externas
│   │   ├── __init__.py
│   │   ├── facebook_ads.py
│   │   ├── google_ads.py
│   │   ├── openai_client.py
│   │   └── fipe_api.py
│   │
│   ├── ml/                  # Machine Learning
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── training.py
│   │   └── inference.py
│   │
│   ├── workers/             # Background workers
│   │   ├── __init__.py
│   │   ├── optimization_worker.py
│   │   └── metrics_worker.py
│   │
│   └── utils/               # Utilitários
│       ├── __init__.py
│       ├── helpers.py
│       └── validators.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── alembic/                 # Migrações
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

#### Opção B: Node.js (NestJS)

**Framework**: NestJS

**Justificativa**:
- ✓ Arquitetura modular e escalável
- ✓ TypeScript nativo
- ✓ Injeção de dependências
- ✓ Excelente para APIs REST e GraphQL
- ✓ Grande ecossistema JavaScript

**Por que NÃO escolher**:
- ✗ Ecossistema de IA/ML menos maduro que Python
- ✗ Mais verboso que FastAPI
- ✗ Integração com bibliotecas de ML mais complexa

**Quando usar**:
- Se a equipe já tem mais experiência com JavaScript
- Se integração com frontend em Next.js for prioritária

---

### 2.2 Frontend

#### Next.js 14+ ⭐ **RECOMENDADO**

**Framework**: Next.js (React)

**Justificativa**:
- ✓ SSR/SSG para melhor SEO e performance
- ✓ File-based routing (simplicidade)
- ✓ App Router moderno
- ✓ Server Components (performance)
- ✓ Ótima DX (Developer Experience)
- ✓ Ecossistema imenso

**Principais Bibliotecas**:
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",

    "typescript": "^5.0.0",

    "tailwindcss": "^3.3.0",
    "@headlessui/react": "^1.7.0",
    "@heroicons/react": "^2.0.0",

    "axios": "^1.5.0",
    "react-query": "^3.39.0",
    "zustand": "^4.4.0",

    "recharts": "^2.8.0",
    "date-fns": "^2.30.0",

    "react-hook-form": "^7.47.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.3.0",

    "next-auth": "^4.24.0",
    "next-intl": "^3.4.0",

    "react-hot-toast": "^2.4.1",
    "lucide-react": "^0.292.0"
  }
}
```

**Estrutura de Pastas**:
```
frontend/
├── app/                    # App Router
│   ├── (auth)/
│   │   ├── login/
│   │   └── register/
│   │
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── veiculos/
│   │   ├── campanhas/
│   │   └── analise/
│   │
│   ├── api/                # API routes (se necessário)
│   ├── layout.tsx
│   └── page.tsx
│
├── components/
│   ├── ui/                 # Componentes base
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   └── Table.tsx
│   │
│   ├── dashboard/
│   │   ├── MetricCard.tsx
│   │   ├── Chart.tsx
│   │   └── DataTable.tsx
│   │
│   ├── veiculos/
│   │   ├── VeiculoForm.tsx
│   │   ├── VeiculoList.tsx
│   │   └── VeiculoCard.tsx
│   │
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
│
├── lib/
│   ├── api.ts              # Cliente HTTP
│   ├── auth.ts             # Autenticação
│   ├── query.ts            # React Query setup
│   └── utils.ts            # Helpers
│
├── hooks/
│   ├── useVeiculos.ts
│   ├── useCampanhas.ts
│   └── useAuth.ts
│
├── stores/
│   └── useStore.ts         # Zustand
│
├── types/
│   └── index.ts            # TypeScript types
│
├── public/
│   └── images/
│
├── styles/
│   └── globals.css
│
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

---

### 2.3 Database

#### PostgreSQL ⭐ **RECOMENDADO**

**Versão**: PostgreSQL 15+

**Justificativa**:
- ✓ Relacional (ideal para structured data)
- ✓ ACID compliance
- ✓ Excelente performance
- ✓ JSONB (flexibilidade quando necessário)
- ✓ Full-text search nativo
- ✓ Open source e robusto
- ✓ Grande comunidade

**Extensões**:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUIDs
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Busca fuzzy
CREATE EXTENSION IF NOT EXISTS "btree_gist";     -- Índices especiais
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- Análise de queries
```

**Alternativa: MongoDB**
- ✓ Schemaless (flexibilidade)
- ✓ Excelente para dados não estruturados
- ✗ Menos adequado para queries complexas
- ✗ Sem joins nativos

**Decisão**: PostgreSQL (relacional é melhor para este caso de uso)

---

### 2.4 Cache

#### Redis ⭐ **RECOMENDADO**

**Versão**: Redis 7+

**Justificativa**:
- ✓ Cache em memória (ultra rápido)
- ✓ Pub/Sub (websockets, workers)
- ✓ Rate limiting
- ✓ Session storage
- ✓ Filas simples (para MVP)

**Uso**:
1. Cache de respostas da IA (economizar custos)
2. Cache de métricas de anúncios (5-15 min)
3. Session storage (JWT refresh tokens)
4. Rate limiting (API)
5. Pub/Sub (websockets em tempo real)

---

### 2.5 File Storage

#### AWS S3 ⭐ **RECOMENDADO**

**Justificativa**:
- ✓ Escalável (ilimitado)
- ✓ Barato (pay-per-use)
- ✓ CDN integrado (CloudFront)
- ✓ Durabilidade 99.999999999%

**Alternativas**:
- Cloudflare R2 (mais barato, sem egress fees)
- Google Cloud Storage
- Azure Blob Storage

**Estrutura de Buckets**:
```
s3://adauto-prod/
├── veiculos/
│   ├── {veiculo_id}/
│   │   ├── original/
│   │   ├── resized/
│   │   └── thumbnails/
│
├── revendas/
│   └── {revenda_id}/
│       └── logo.png
│
└── temp/
    └── {upload_id}/
```

---

### 2.6 Background Jobs

#### Celery + Redis (Python) ⭐ **RECOMENDADO**

**Justificativa**:
- ✓ Robusto e testado
- ✓ Integração perfeita com Redis
- ✓ Suporte a retries, scheduling
- ✓ Monitoramento (Flower)

**Casos de Uso**:
1. Otimização automática de campanhas (agendado)
2. Coleta de métricas (agendado)
3. Geração de relatórios (agendado)
4. Processamento de imagens (fila)
5. Webhooks de ads (fila)

**Alternativas**:
- RQ (simples, menos features)
- BullMQ (Node.js)
- AWS SQS (managed, mas mais complexo)

---

### 2.7 APIs de IA/ML

#### OpenAI GPT-4 ⭐ **RECOMENDADO**

**Modelos**:
- `gpt-4-turbo`: Para geração de copy e análise complexa
- `gpt-3.5-turbo`: Para tarefas mais simples (mais barato)

**Justificativa**:
- ✓ State-of-the-art em NLG
- ✓ Excelente para copywriting
- ✓ API estável e confiável
- ✓ Preço competitivo

**Custo Estimado**:
- Análise de veículo: R$ 0,05
- Geração de copy: R$ 0,10
- Total por veículo: ~R$ 0,15

---

#### Claude API (Anthropic) - Opção Secundária

**Modelos**:
- `claude-3-opus`: Para tarefas complexas
- `claude-3-sonnet`: Para uso geral

**Justificativa**:
- ✓ Context window maior
- ✓ Excelente para análise
- ✓ Preço competitivo

**Uso**:
- Backup para OpenAI
- Para análise de longos documentos

---

#### Scikit-learn (ML)

**Casos de Uso**:
1. Previsão de CTR
2. Previsão de conversão
3. Recomendação de preço
4. Clustering de veículos

**Justificativa**:
- ✓ Biblioteca padrão de ML em Python
- ✓ Excelente para tabular data
- ✓ Modelos leves e rápidos

---

### 2.8 APIs de Ads

#### Facebook Marketing API

**SDK**: `facebook-business` (Python)

**Autenticação**: OAuth 2.0

**Features**:
- Criar campanhas, conjuntos, anúncios
- Upload de criativos
- Coletar métricas (insights)
- Webhooks

---

#### Google Ads API

**SDK**: `google-ads` (Python)

**Autenticação**: OAuth 2.0 ou Service Account

**Features**:
- Criar campanhas, grupos, anúncios
- Gerenciar keywords
- Coletar relatórios
- Google Ads Scripts (para automações)

---

### 2.9 APIs de Dados

#### BrasilAPI (FIPE)

**Endpoint**: `https://brasilapi.com.br/api/fipe/v1/`

**Uso**:
- Consultar preço médio FIPE
- Consultar código FIPE por marca/modelo

**Custo**: Gratuito

---

#### Detran APIs (Sindicatos)

**Uso**:
- Consultar débitos (multas, IPVA)
- Histórico de proprietários
- Veículo roubado/furtado

**Fornecedores**:
- SINESP
- CheckMais
- DETRAN SP

**Custo**: R$ 0,50 - R$ 2,00 por consulta

---

## 3. Infraestrutura

### 3.1 Hosting

#### AWS ⭐ **RECOMENDADO**

**Serviços**:
- **ECS** ou **EKS**: Containers (Docker)
- **RDS**: PostgreSQL gerenciado
- **ElastiCache**: Redis gerenciado
- **S3**: Storage
- **CloudFront**: CDN
- **Route53**: DNS
- **ALB**: Load balancer

**Justificativa**:
- ✓ Mais maduro e completo
- ✓ Grande variedade de serviços
- ✓ Excelente documentação
- ✓ Comunidade enorme

**Custo Estimado**:
- ECS: R$ 50-200/mês
- RDS: R$ 100-300/mês
- ElastiCache: R$ 50-150/mês
- S3: R$ 20-50/mês
- CloudFront: R$ 30-100/mês
- **Total**: R$ 250-800/mês (MVP)

---

#### Alternativa: Railway (Simples)

**Justificativa**:
- ✓ Muito mais simples
- ✓ Auto-deploy from GitHub
- ✓ Preview deployments
- ✓ Preço transparente

**Custo**:
- Plano Pro: US$ 20/mês por serviço
- Total: ~US$ 80-120/mês (4 serviços)

**Quando usar**:
- MVP / piloto
- Time pequeno
- Sem expertise em DevOps

---

#### Alternativa: Google Cloud Platform

**Justificativa**:
- ✓ Integração nativa com Google Ads
- ✓ Cloud Run (serverless)
- ✓ Excelente para ML/AI

**Custo**: Similar à AWS

---

### 3.2 CI/CD

#### GitHub Actions ⭐ **RECOMENDADO**

**Workflow**:
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: ${{ secrets.DOCKER_REGISTRY }}/backend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster production --service backend
```

---

### 3.3 Monitoring & Logging

#### Datadog (Opcional)

**Features**:
- APM (Application Performance Monitoring)
- Logs
- Métricas
- Uptime monitoring
- Error tracking

**Custo**: US$ 15-50/host/mês

---

#### Alternativa: Sentry (Error Tracking)

**Custo**: Gratuito (dev), US$ 26/mês (pro)

---

#### Alternativa: CloudWatch (AWS Nativo)

**Custo**: Incluído em muitos serviços AWS

---

### 3.4 Error Tracking

#### Sentry ⭐ **RECOMENDADO**

**Justificativa**:
- ✓ Excelente para errors em tempo real
- ✓ Integracão com GitHub
- ✓ Performance monitoring
- ✓ Free tier generoso

**Custo**:
- Developer: Gratuito
- Team: US$ 26/mês (5.000 errors/mês)

---

## 4. Development Tools

### 4.1 Version Control

**Git + GitHub**

**Workflow**:
- `main`: produção
- `develop`: desenvolvimento
- `feature/*`: novas features
- `bugfix/*`: correções

---

### 4.2 API Documentation

#### OpenAPI/Swagger

**Geração Automática**:
- FastAPI gera automaticamente
- Disponível em `/docs`

**Features**:
- Try out requests
- Schema visualization
- Client generation

---

### 4.3 Testing

#### Pytest (Backend)

**Coverage Goal**: > 80%

```python
# Exemplo de teste
def test_create_veiculo(client, auth_token):
    response = client.post(
        "/api/v1/veiculos",
        json={...},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    assert response.json()["modelo"] == "Civic"
```

---

#### Jest + React Testing Library (Frontend)

**Coverage Goal**: > 70%

```typescript
// Exemplo de teste
test('deve renderizar lista de veículos', () => {
  render(<VeiculoList veiculos={mockVeiculos} />)
  expect(screen.getByText('Honda Civic')).toBeInTheDocument()
})
```

---

### 4.4 Code Quality

#### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0
    hooks:
      - id: prettier
        files: \.(ts|tsx|js|jsx|css|json)$
```

---

### 4.5 Type Checking

#### mypy (Python)

```bash
mypy app/
```

#### TypeScript (Frontend)

```bash
tsc --noEmit
```

---

## 5. Segurança

### 5.1 Autenticação

#### JWT (JSON Web Tokens)

**Implementação**:
- Access token: 15 min
- Refresh token: 7 dias
- Armazenado em httpOnly cookies

---

### 5.2 Autorização

#### RBAC (Role-Based Access Control)

**Roles**:
- `admin`: Acesso total
- `manager`: Gestão de veículos e campanhas
- `viewer`: Apenas leitura

---

### 5.3 Criptografia

- Senhas: bcrypt (salt rounds: 12)
- Tokens: AES-256
- Dados sensíveis: criptografia no banco

---

### 5.4 Rate Limiting

#### slowapi (Python)

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/analise")
@limiter.limit("10/minute")
async def analise_veiculo(...):
    ...
```

---

### 5.5 CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://adauto.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 6. Comunicacões

### 6.1 Email

#### Resend (ou SendGrid)

**Uso**:
- Confirmação de cadastro
- Reset de senha
- Relatórios semanais
- Alertas de performance

**Custo**: ~US$ 20/mês (até 50.000 emails)

---

### 6.2 Notificações

#### Push (Browser) - Futuro

**SDK**: OneSignal

**Uso**: Alertas de leads, otimizações

---

## 7. Analytics

### 7.1 Product Analytics

#### PostHog ou Mixpanel

**Eventos**:
- `veiculo_cadastrado`
- `anuncio_criado`
- `sugestao_ia_aceita`
- `lead_gerado`

**Custo**: Gratuito até 1M eventos/mês

---

### 7.2 Funnel Analytics

Acompanhar jornada do usuário:
1. Sign up
2. Connect ads accounts
3. Create first vehicle
4. Generate suggestions
5. Create first ad
6. Get first lead
7. Make first sale

---

## 8. Custos Mensais Estimados (MVP)

| Serviço | Custo (BRL) |
|---------|-------------|
| AWS (ECS, RDS, ElastiCache, S3) | R$ 300-800 |
| OpenAI API | R$ 200-500 |
| Claude API (backup) | R$ 50-200 |
| Facebook Ads API | Gratuito |
| Google Ads API | R$ 50-150 |
| FIPE API | Gratuito |
| Detran APIs | R$ 50-200 |
| Sentry | R$ 130 |
| Datadog (opcional) | R$ 100-300 |
| Email (Resend) | R$ 100 |
| GitHub (se privado) | R$ 50 |
| **TOTAL** | **R$ 1.030-2.630/mês** |

---

## 9. Decisões Finais

### Stack Escolhido (MVP):

**Backend**: Python + FastAPI
**Frontend**: Next.js 14
**Database**: PostgreSQL
**Cache**: Redis
**Storage**: AWS S3
**Queue**: Celery + Redis
**Hosting**: AWS ECS
**CI/CD**: GitHub Actions
**Monitoring**: CloudWatch + Sentry
**Analytics**: PostHog

---

### Por que essas escolhas?

1. **Python + FastAPI**: Melhor para IA/ML, async nativo
2. **Next.js**: Melhor DX e performance para frontend
3. **PostgreSQL**: Melhor para structured data
4. **Redis**: Cache + filas em um só serviço
5. **AWS**: Mais maduro e completo
6. **OpenAI**: State-of-the-art em NLG
7. **Celery**: Padrao da industria para Python

---

**Documentos do Dia 1 Concluídos! ✅**

Entregáveis:
- ✅ Escopo completo do projeto definido
- ✅ Plataformas de anúncios identificadas
- ✅ Personas do público-alvo mapeadas
- ✅ Tipos de dados dos veículos listados
- ✅ Métricas de sucesso definidas
- ✅ Concorrentes e soluções existentes pesquisadas
- ✅ Documento de visão do produto criado
- ✅ Tecnologias necessárias identificadas

---

**Próximo Dia (Dia 2)**: Arquitetura e Design do Sistema
