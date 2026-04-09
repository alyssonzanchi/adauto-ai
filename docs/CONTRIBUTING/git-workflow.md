# 🔄 Git Workflow - Car Ads Platform

## 📋 Estrutura de Branches

```
main                    ← Branch de produção (sempre estável)
├── develop             ← Branch de desenvolvimento (integração)
    ├── week-3-auth     ← Branch da Semana 3 (autenticação)
    ├── week-4-vehicles ← Branch da Semana 4 (veículos)
    └── week-5-ai       ← Branch da Semana 5 (AI service)
```

## 🎯 Convenções de Branches

### Branches Principais

**`main`**
- Branch de produção
- Código testado e estável
- Tags de release (v1.0.0, v1.1.0, etc.)
- Protegido: requer pull request para merge

**`develop`**
- Branch de desenvolvimento
- Integração de todas as features
- Próximo release é criado daqui
- Protegido: requer pull request para merge

### Branches de Feature

**Padrão de nomeação:**
- `week-N-feature` - Ex: `week-4-vehicles`
- `feature/description` - Ex: `feature/upload-images`
- `bugfix/description` - Ex: `bugfix/login-error`
- `hotfix/description` - Ex: `hotfix/security-patch`

## 🔄 Workflow

### 1. Iniciar uma Nova Feature

```bash
# Atualizar develop
git checkout develop
git pull origin develop

# Criar branch da feature
git checkout -b week-4-vehicles

# Trabalhar na feature
# ... fazer commits ...

# Push para origin
git push -u origin week-4-vehicles
```

### 2. Commits Convencionais

**Formato:**
```
<tipo>(<escopo>): <descrição>

[opcional: corpo]

[opcional: footer]
```

**Tipos:**
- `feat` - Nova feature
- `fix` - Bug fix
- `docs` - Mudança na documentação
- `style` - Formatação, missing semicolons
- `refactor` - Refatoração
- `test` - Adicionando testes
- `chore` - Atualização de tarefas, configs

**Exemplos:**
```bash
git commit -m "feat(auth): implement JWT authentication"
git commit -m "fix(users): resolve email validation bug"
git commit -m "docs(readme): update setup instructions"
git commit -m "feat(vehicles): add image upload endpoint"
```

### 3. Pull Request

**Criar PR para `develop`:**

```markdown
## Descrição
Implementação do CRUD de Vehicles com upload de imagens.

## Tipo de Mudança
- [ ] Bug fix
- [x] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Testes
- [x] Testes unitários
- [x] Testes de integração
- [ ] Testes manuais

## Checklist
- [x] Código segue os padrões do projeto
- [x] Commits seguem convenção de mensagens
- [x] Documentação atualizada
- [x] Tests passando
- [x] Sem conflitos com develop
```

### 4. Code Review

**Processo:**
1. Abrir PR no GitHub/GitLab
2. Solicitar review de pelo menos 1 pessoa
3. Responder aos comentários
4. Fazer ajustes se necessário
5. Aprovar e merge para `develop`

### 5. Merge para Develop

```bash
# Opção 1: Merge commit (preserva histórico)
git checkout develop
git merge week-4-vehicles

# Opção 2: Squash and merge (histórico limpo)
# Usar interface do GitHub/GitLab

# Opção 3: Rebase and merge (histórico linear)
# Usar interface do GitHub/GitLab

# Deletar branch após merge
git branch -d week-4-vehicles
git push origin --delete week-4-vehicles
```

### 6. Release para Main

```bash
# Criar branch de release
git checkout develop
git checkout -b release/v0.3.0

# Atualizar versão nos arquivos
# ... fazer ajustes finais ...

# Merge para main
git checkout main
git merge release/v0.3.0

# Criar tag
git tag -a v0.3.0 -m "Release v0.3.0: Semana 3 completa"
git push origin main --tags

# Merge de volta para develop
git checkout develop
git merge release/v0.3.0
git push origin develop

# Deletar branch de release
git branch -d release/v0.3.0
```

## 🏷️ Convenção de Versionamento (SemVer)

**Formato:** `MAJOR.MINOR.PATCH`

- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Nova feature backwards compatible
- **PATCH**: Bug fix backwards compatible

**Exemplos:**
- `v0.1.0` - MVP (Semana 1-4)
- `v0.2.0` - AI Service (Semana 5-8)
- `v0.3.0` - Ads Integration (Semana 9-12)
- `v1.0.0` - Primeira versão estável (Semana 22)

## 🚀 Comandos Úteis

### Ver histórico
```bash
git log --oneline --graph --all
git log --author="Seu Nome"
git log --grep="feat"
```

### Ver branches
```bash
git branch -a           # Todas as branches
git branch -r           # Branches remotas
git branch -vv          # Branches com tracking
```

### Limpeza
```bash
git gc                  # Garbage collection
git clean -fd           # Remove arquivos não trackeados
git remote prune origin # Remove branches remotas deletadas
```

### Stash (salvar trabalho temporário)
```bash
git stash               # Salvar mudanças
git stash list          # Ver stashs
git stash pop           # Recuperar stash
git stash drop          # Deletar stash
```

## 🚨 Regras Importantes

### ✅ Sempre
- Fazer pull antes de push
- Escrever mensagens de commit claras
- Criar branches para cada feature
- Fazer code review via PR
- Atualizar documentação

### ❌ Nunca
- Commitar direto em `main`
- Commitar arquivos sensíveis (.env, secrets)
- Commitar código quebrado
- Fazer force push em branches compartilhadas
- Ignorar code review

## 📱 Integração Contínua (CI)

**GitHub Actions / GitLab CI:**

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pytest
```

## 🔗 Links Úteis

- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

**Status**: 🟢 Ativo
**Última atualização**: 08/04/2026
