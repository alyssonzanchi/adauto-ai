# Car Ads Platform - Sistema de Anúncios Patrocinados para Revenda de Carros

## 🚗 Sobre o Projeto

Plataforma completa de anúncios patrocinados com inteligência artificial para revendas de carros. O sistema utiliza IA para analisar veículos, gerar conteúdo de anúncios otimizados e prever performance, maximizando o ROI das campanhas.

### 🎯 Funcionalidades Principais

- **Gestão de Veículos**: Cadastro completo de inventário com fotos e especificações
- **Análise AI**: Análise automática de veículos com scoring e insights de mercado
- **Geração de Anúncios**: Criação automática de conteúdo para Facebook, Instagram e Google Ads
- **Previsão de Performance**: Estimativas de CTR, conversões e ROI usando ML
- **Otimização Automática**: Melhorias automáticas baseadas em performance
- **Métricas em Tempo Real**: Dashboard completo com analytics e relatórios
- **Integrações Nativas**: Facebook Ads, Instagram Ads, Google Ads

---

## 🏗️ Arquitetura

```
Frontend (Next.js 14)          Backend (FastAPI)           AI Service
├─ shadcn/ui                 ├─ SQLAlchemy 2.0           ├─ Claude API
├─ React Query               ├─ Pydantic v2              ├─ OpenAI GPT-4
├─ Zustand                   ├─ Alembic                  ├─ LangChain
└─ TailwindCSS               └─ JWT Auth                 └─ XGBoost

Data Layer
├─ PostgreSQL 16
├─ Redis 7
├─ pgvector (AI embeddings)
└─ MinIO (images)
```

---

## 📋 Índice

- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Execução](#execução)
- [API Documentation](#api-documentation)
- [Desenvolvimento](#desenvolvimento)
- [Deploy](#deploy)
- [Contribuindo](#contribuindo)

---

## 🔧 Tecnologias

### Backend
- **Python 3.11+**
- **FastAPI 0.104+** - Framework web async
- **SQLAlchemy 2.0** - ORM async
- **Pydantic v2** - Validação de dados
- **Alembic** - Migrations do banco
- **PostgreSQL 16** - Banco de dados principal
- **Redis 7** - Cache e message broker
- **Celery** - Task queue
- **pgvector** - Busca vetorial para IA

### Frontend
- **Next.js 14** (App Router) - Framework React
- **TypeScript** - Tipagem estática
- **shadcn/ui** - Componentes UI
- **TailwindCSS** - Estilização
- **Zustand** - State management
- **React Query** - Server state
- **Recharts** - Gráficos e analytics

### AI/ML
- **Claude API** (Anthropic) - LLM principal
- **OpenAI GPT-4** - LLM alternativo
- **LangChain** - Orquestração de agents
- **XGBoost** - Modelos de ML
- **scikit-learn** - ML tradicional

### Infrastructure
- **Docker** - Containerização
- **Docker Compose** - Orquestração local
- **NGINX** - Reverse proxy
- **GitHub Actions** - CI/CD

---

## 📁 Estrutura do Projeto

```
car-ads-system/
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   └── v1/
│   │   │       ├── endpoints/ # Route handlers
│   │   │       ├── deps.py    # Dependencies
│   │   │       └── router.py  # API router
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py      # Settings
│   │   │   ├── security.py    # Auth
│   │   │   └── deps.py        # Shared deps
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── utils/             # Utilities
│   │   └── main.py            # App entry point
│   ├── tests/                 # Testes
│   ├── alembic/               # Migrations
│   ├── requirements.txt        # Python deps
│   └── Dockerfile
│
├── frontend/                   # Frontend Next.js
│   ├── src/
│   │   ├── app/               # App Router
│   │   │   ├── (auth)/        # Auth routes
│   │   │   ├── dashboard/     # Dashboard
│   │   │   ├── vehicles/      # Vehicles
│   │   │   ├── ads/           # Ads
│   │   │   └── metrics/       # Metrics
│   │   ├── components/        # React components
│   │   │   ├── ui/            # shadcn/ui components
│   │   │   ├── dashboard/     # Dashboard components
│   │   │   ├── vehicles/      # Vehicle components
│   │   │   ├── ads/           # Ad components
│   │   │   └── metrics/       # Metrics components
│   │   ├── lib/               # Utilities
│   │   ├── types/             # TypeScript types
│   │   └── styles/            # Global styles
│   ├── public/                # Static assets
│   ├── package.json
│   └── Dockerfile
│
├── docs/                       # Documentation
│   ├── architecture.md         # System architecture
│   ├── database-schema.md      # DB schema
│   ├── api-specification.md    # API docs
│   ├── ai-agent-structure.md   # AI agents
│   └── wireframes/            # UI wireframes
│
├── scripts/                    # Utility scripts
├── docker/                     # Docker configs
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── init-scripts/
│
└── README.md
```

---

## 📦 Pré-requisitos

### Obrigatórios
- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **PostgreSQL 16+** (ou usar Docker)
- **Redis 7+** (ou usar Docker)

### Recomendados
- **Git**
- **Make** (para scripts de desenvolvimento)
- **VS Code** (com extensões Python, TypeScript)

### Contas Externas
- **Anthropic Claude API** (para IA)
- **OpenAI API** (alternativa)
- **Facebook Developer Account** (Facebook Ads)
- **Google Ads Account** (Google Ads)

---

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/yourusername/car-ads-system.git
cd car-ads-system
```

### 2. Variáveis de Ambiente

#### Backend (.env)
```bash
cp backend/.env.example backend/.env
```

Edite `backend/.env`:
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/car_ads_db
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/car_ads_test

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI APIs
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key

# Ad Platforms
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-secret
FACEBOOK_REDIRECT_URI=http://localhost:8000/api/v1/integrations/facebook/callback

GOOGLE_ADS_DEVELOPER_TOKEN=your-google-token
GOOGLE_ADS_CLIENT_ID=your-google-client-id
GOOGLE_ADS_CLIENT_SECRET=your-google-client-secret
GOOGLE_ADS_REDIRECT_URI=http://localhost:8000/api/v1/integrations/google/callback

# S3/MinIO
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_S3_ENDPOINT=http://localhost:9000
AWS_S3_BUCKET=car-ads-images

# Environment
ENVIRONMENT=development
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

#### Frontend (.env.local)
```bash
cp frontend/.env.example frontend/.env.local
```

Edite `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_ENABLE_MOCKING=false
```

### 3. Docker Compose (Recomendado)

```bash
# Inicia todos os serviços
docker-compose up -d

# Verifica status
docker-compose ps

# Ver logs
docker-compose logs -f
```

Serviços incluídos:
- PostgreSQL (porta 5432)
- Redis (porta 6379)
- MinIO (porta 9000)
- Backend (porta 8000)
- Frontend (porta 3000)

### 4. Instalação Manual

#### Backend
```bash
cd backend

# Criar virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Rodar migrations
alembic upgrade head

# Criar usuário admin
python scripts/create_admin.py
```

#### Frontend
```bash
cd frontend

# Instalar dependências
npm install
# ou
yarn install

# Build para produção
npm run build
```

---

## ⚙️ Configuração

### Banco de Dados

```bash
# Criar database
createdb car_ads_db

# Rodar migrations
cd backend
alembic upgrade head

# Rollback
alembic downgrade -1

# Criar nova migration
alembic revision --autogenerate -m "description"
```

### Redis

```bash
# Start Redis
redis-server

# Testar conexão
redis-cli ping
```

### MinIO (S3)

```bash
# Acessar console: http://localhost:9000
# User: minioadmin
# Password: minioadmin

# Criar bucket: car-ads-images
# Policy: public read
```

---

## 🏃 Execução

### Modo Desenvolvimento

#### Backend
```bash
cd backend

# Com UVicorn (recomendado)
uvicorn app.main:app --reload --port 8000

# Com debug
uvicorn app.main:app --reload --log-level debug
```

API disponível em:
- HTTP: http://localhost:8000
- Docs (Swagger): http://localhost:8000/docs
- Docs (ReDoc): http://localhost:8000/redoc

#### Frontend
```bash
cd frontend

# Development server
npm run dev

# Disponível em: http://localhost:3000
```

### Modo Produção

```bash
# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend
cd frontend
npm run build
npm run start
```

### Testes

#### Backend
```bash
cd backend

# Todos os testes
pytest

# Com coverage
pytest --cov=app --cov-report=html

# Testes específicos
pytest tests/test_api.py -v

# Testes async
pytest -k "test_async" -v
```

#### Frontend
```bash
cd frontend

# Unit tests
npm test

# E2E tests
npm run test:e2e

# Component tests
npm run test:component
```

---

## 📚 API Documentation

### Swagger UI

Acesse: http://localhost:8000/docs

### Principais Endpoints

#### Autenticação
- `POST /api/v1/auth/register` - Registro
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token

#### Veículos
- `GET /api/v1/vehicles` - Listar veículos
- `POST /api/v1/vehicles` - Criar veículo
- `GET /api/v1/vehicles/{id}` - Detalhes
- `PUT /api/v1/vehicles/{id}` - Atualizar
- `DELETE /api/v1/vehicles/{id}` - Deletar
- `POST /api/v1/vehicles/{id}/analyze` - Análise AI

#### Anúncios
- `GET /api/v1/ads` - Listar anúncios
- `POST /api/v1/ads` - Criar anúncio
- `POST /api/v1/ads/{id}/publish` - Publicar
- `POST /api/v1/ads/{id}/pause` - Pausar
- `GET /api/v1/ads/{id}/metrics` - Métricas

#### AI
- `POST /api/v1/ai/analyze-vehicle` - Analisar veículo
- `POST /api/v1/ai/generate-ad` - Gerar anúncio
- `POST /api/v1/ai/optimize` - Otimizar
- `GET /api/v1/ai/predict` - Previsão performance

Documentação completa: [docs/api-specification.md](docs/api-specification.md)

---

## 👨‍💻 Desenvolvimento

### Comandos Úteis

#### Backend
```bash
# Formatar código
black app/
isort app/

# Linter
flake8 app/
pylint app/

# Type check
mypy app/

# Security check
bandit -r app/
```

#### Frontend
```bash
# Linter
npm run lint

# Format
npm run format

# Type check
npm run type-check
```

### Git Workflow

```bash
# Feature branch
git checkout -b feature/nova-funcionalidade

# Commit
git add .
git commit -m "feat: add nova funcionalidade"

# Push
git push origin feature/nova-funcionalidade

# PR para main
```

### Convenções de Commit

- `feat`: Nova funcionalidade
- `fix`: Bug fix
- `docs`: Documentação
- `style`: Formatação, style
- `refactor`: Refatoração
- `test`: Tests
- `chore`: Build, configs

---

## 🚢 Deploy

### Produção com Docker

```bash
# Build
docker-compose -f docker-compose.prod.yml build

# Up
docker-compose -f docker-compose.prod.yml up -d

# Logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Variáveis de Produção

- Set `ENVIRONMENT=production`
- Set `DEBUG=false`
- Use secrets management (AWS Secrets, etc.)
- Configure HTTPS/SSL
- Setup backups

### Monitoring

- **Application Logs**: ELK Stack
- **Metrics**: Prometheus + Grafana
- **Error Tracking**: Sentry
- **Uptime**: UptimeRobot

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie branch para feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: add AmazingFeature'`)
4. Push para branch (`git push origin feature/AmazingFeature`)
5. Abra Pull Request

### Code Review Checklist
- [ ] Código segue style guide
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Sem merges diretos para main
- [ ] PR description clara
- [ ] Todos os checks passam

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/yourusername/car-ads-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/car-ads-system/discussions)
- **Email**: support@caradsplatform.com

---

## 🗺️ Roadmap

### Versão 1.0 (Q2 2026)
- ✅ Sistema core de gestão de veículos
- ✅ Anúncios Facebook e Instagram
- ✅ AI básico para análise e geração
- ✅ Dashboard de métricas

### Versão 1.1 (Q3 2026)
- ⏳ Integração Google Ads
- ⏳ Otimização automática de anúncios
- ⏳ Relatórios avançados
- ⏳ A/B testing

### Versão 2.0 (Q4 2026)
- ⏳ TikTok Ads
- ⏳ LinkedIn Ads
- ⏳ Previsões avançadas de ML
- ⏳ Auto-optimization completa

---

## 🙏 Agradecimentos

- **FastAPI** - Framework web moderno
- **Next.js** - Framework React
- **shadcn/ui** - Componentes UI
- **Anthropic** - Claude API
- **Vercel** - Hosting de referência

---

**Desenvolvido com ❤️ pela equipe Car Ads Platform**
