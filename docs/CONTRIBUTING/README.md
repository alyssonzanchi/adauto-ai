# 📚 Guia de Contribuição - Car Ads Platform

## 🚀 Setup Inicial

### 1. Clone o Repositório

```bash
git clone <url-do-repositorio>
cd adauto-ai
```

### 2. Configure seu Ambiente

**Backend (Python):**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
cp .env.example .env
# Editar .env com suas configurações
```

**Frontend (Next.js):**
```bash
cd frontend
npm install
cp .env.example .env.local
# Editar .env.local com suas configurações
```

### 3. Inicie os Serviços

```bash
# Na raiz do projeto
docker-compose up -d

# Isso inicia:
# - PostgreSQL (porta 5432)
# - Redis (porta 6379)
# - MinIO (porta 9000)
```

### 4. Execute as Migrações

```bash
cd backend
alembic upgrade head
```

### 5. Inicie o Servidor de Desenvolvimento

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

---

## 🔄 Git Workflow

Veja [git-workflow.md](./git-workflow.md) para detalhes completos.

### Resumo Rápido:

```bash
# 1. Crie uma branch para sua feature
git checkout -b week-N-feature

# 2. Faça suas mudanças
git add .
git commit -m "feat(scope): descrição da mudança"

# 3. Push e crie Pull Request
git push -u origin week-N-feature

# 4. Aguardar code review e merge
```

---

## 📝 Convenções

### Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<escopo>): <descrição>

 tipos:
- feat:     nova feature
- fix:      bug fix
- docs:     mudança na documentação
- style:    formatação
- refactor: refatoração
- test:     adicionar testes
- chore:    tarefas
```

### Branches

- `main` - produção
- `develop` - desenvolvimento
- `week-N-feature` - features específicas

### Code Style

**Python (Backend):**
- Seguir PEP 8
- Usar type hints
- Docstrings em inglês
- Máximo 100 caracteres por linha

**TypeScript (Frontend):**
- Seguir ESLint/Prettier
- Usar functional components
- Props com TypeScript interfaces

---

## 🧪 Testes

### Backend

```bash
cd backend
pytest                        # Rodar todos os testes
pytest tests/test_auth.py     # Testes específicos
pytest -v                    # Verboso
pytest --cov=app             # Com coverage
```

### Frontend

```bash
cd frontend
npm test                     # Rodar todos os testes
npm run test:watch          # Modo watch
npm run test:coverage       # Com coverage
```

---

## 📖 Documentação

### Atualizar Documentação

Se sua mudança afeta a API ou funcionalidades:

1. Atualize `docs/dia2-arquitetura/api-specification.md`
2. Atualize `docs/referencias/roadmap.md` se necessário
3. Adicione exemplos em `backend/docs/` se relevante

### Criar Novas Features

1. Implemente a feature
2. Escreva testes
3. Atualize documentação
4. Crie PR com descrição detalhada

---

## 🐛 Reportar Bugs

Use o template de issue:

```markdown
## Descrição
Breve descrião do bug

## Passos para Reproduzir
1. Passo 1
2. Passo 2
3. Passo 3

## Comportamento Esperado
O que deveria acontecer

## Comportamento Atual
O que está acontecendo

## Ambiente
- OS:
- Versão:
- Navegador:
```

---

## 💡 Sugestões de Features

Use o template de feature request:

```markdown
## Descrição
Descrição da feature sugerida

## Problema
Qual problema essa feature resolve?

## Solução Proposta
Como você imagina que funcione

## Alternativas
Outras abordagens consideradas

## Prioridade
Baixa/Média/Alta
```

---

## ✅ Checklist antes de abrir PR

- [ ] Código segue os padrões do projeto
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Commits seguem convenção
- [ ] Sem conflitos com branch alvo
- [ ] Build passando
- [ ] Tests passando
- [ ] Código review feito

---

## 📞 Contato

Dúvidas? Entre em contato:
- **Email**: alyssonzanchi@icloud.com
- **Issues**: [GitHub Issues](url-do-repositorio/issues)

---

**Obrigado por contribuir!** 🙏
