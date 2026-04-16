# AI Service Runbook Operacional

Guide operacional para gerenciamento do serviço de IA em produção.

## 📋 Sumário Executivo

Este runbook documenta os procedimentos operacionais para gerenciar, monitorar e solucionar problemas do serviço de IA.

**Última Atualização**: 15/04/2026
**Versão**: v2.0.0
**Status**: Produção

---

## 🚀 Start/Stop dos Serviços

### Iniciar Serviços

```bash
# Docker Compose (recomendado)
docker-compose -f docker/docker-compose.yml up -d postgres redis backend

# Verificar status
docker-compose -f docker/docker-compose.yml ps
```

### Parar Serviços

```bash
# Parar todos
docker-compose -f docker/docker-compose.yml down

# Parar backend apenas
docker-compose -f docker/docker-compose.yml stop backend
```

### Reiniciar Backend

```bash
# Reiniciar backend
docker-compose -f docker/docker-compose.yml restart backend

# Logs em tempo real
docker-compose -f docker/docker-compose.yml logs -f backend
```

---

## 🔍 Health Checks

### Health Check Completo

```bash
# Endpoint health
curl http://localhost:8000/health/ai

# Expected response
{
  "status": "healthy",
  "services": {
    "llm_client": "ok",
    "embedding_service": "ok",
    "feature_store": "ok"
  }
}
```

### Health Checks Individuais

```bash
# 1. PostgreSQL + pgvector
docker-compose exec postgres psql -U postgres -d car_ads_db -c "SELECT 1 FROM pg_extension WHERE extname = 'vector';"

# 2. Redis
docker-compose exec redis redis-cli ping

# 3. AI Services (via script)
python scripts/validate_ai_setup.py
```

---

## 📊 Monitoramento

### Métricas Chave

**Métricas a Monitorar:**

1. **Disponibilidade**
   - Uptime do serviço
   - Taxa de erro da API
   - Latência das requisições

2. **Performance**
   - Tempo de análise (P95 < 3s)
   - Tempo de busca semântica (P95 < 100ms)
   - Cache hit rate (> 80%)

3. **Custos**
   - Tokens consumidos por dia
   - Custo por análise
   - Fallback rate (Claude → OpenAI)

### Como Monitorar

```bash
# Ver métricas atuais
curl http://localhost:8000/metrics/ai

# Ou no código Python
from app.services.ai.orchestrator import get_orchestrator
orchestrator = get_orchestrator()
metrics = orchestrator.get_metrics()
print(metrics)
```

### Alerts Configurar

**Alertas Críticos:**
- Error rate > 5%
- Fallback rate > 20%
- Analysis time P95 > 5s
- Cache hit rate < 60%

**Alerts de Aviso:**
- OpenAI fallback ativado
- Token usage > 80% do limite
- Custo diário > US$10

---

## 🛠️ Operações Comuns

### Gerar Embeddings para Novos Veículos

**Automaticamente (via background task):**
```python
from app.tasks.ai_tasks import generate_vehicle_embeddings

# Gerar para veículo específico
generate_vehicle_embeddings.delay(str(vehicle_id))
```

**Manualmente:**
```bash
python scripts/populate_embeddings_simple.py --vehicle-id <uuid>
```

**Em batch:**
```bash
# Para todos os veículos sem embeddings
python scripts/populate_embeddings_simple.py

# Limite específico
python scripts/populate_embeddings_simple.py --limit 50
```

### Limpar Cache

**Cache específico:**
```python
from app.services.cache.feature_store import FeatureStore

feature_store = FeatureStore(redis_client)
await feature_store.invalidate_vehicle(vehicle_id)
```

**Todo o cache:**
```bash
# Redis
docker-compose exec redis redis-cli FLUSHDB

# Verificar tamanho
docker-compose exec redis redis-cli INFO memory
```

### Atualizar Embeddings

**Quando atualizar veículo:**
```python
# Embadings são regenerados automaticamente se usar cache
# Para forçar regeneração:
await feature_store.invalidate_vehicle(vehicle_id)
# Depois gerar embeddings novamente
```

---

## 🚨 Troubleshooting

### Problema: Análise demorando muito

**Sintoma**: Análise levando > 10 segundos

**Diagnóstico:**
```bash
# Ver latência da API
curl -w "@json" -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

**Soluções:**
1. Verificar conexão de rede
2. Reduzir tamanho do prompt
3. Ajustar `AI_TIMEOUT` se necessário
4. Verificar se circuit breaker está aberto

### Problema: Alta taxa de fallback

**Sintoma**: Mais de 10% de requisições usando OpenAI

**Diagnóstico:**
```python
orchestrator = get_orchestrator()
metrics = orchestrator.get_metrics()
fallback_rate = metrics["llm_client"]["fallback_rate"]
print(f"Fallback rate: {fallback_rate:.2%}")
```

**Soluções:**
1. Verificar status da API Anthropic
2. Verificar cotas de uso
3. Verificar se há problemas de autenticação
4. Aumentar `AI_MAX_RETRIES` se for erro transitório

### Problema: Cache hit rate baixo

**Sintoma**: Cache hit rate < 60%

**Diagnóstico:**
```python
from app.services.cache.feature_store import FeatureStore

feature_store = FeatureStore(redis_client)
metrics = feature_store.get_metrics()
print(metrics["hit_rate"])
```

**Soluções:**
1. Verificar se TTL está muito curto
2. Verificar se cache está sendo invalidado demais
3. Aumentar `FEATURE_CACHE_TTL`
4. Implementar cache warming

### Problema: Busca semântica não retorna resultados

**Sintoma**: `search_by_text` retorna lista vazia

**Diagnóstico:**
```bash
# Verificar se veículos têm embeddings
docker-compose exec postgres psql -U postgres -d car_ads_db -c \
  "SELECT COUNT(*) FROM vehicles WHERE description_embedding IS NOT NULL;"

# Verificar dimensões do embedding
docker-compose exec postgres psql -U postgres -d car_ads_db -c \
  "SELECT array_length(description_embedding, 1) FROM vehicles WHERE description_embedding IS NOT NULL LIMIT 1;"
```

**Soluções:**
1. Gerar embeddings para os veículos
2. Ajustar `VECTOR_SIMILARITY_THRESHOLD`
3. Verificar se query_text está muito específico
4. Aumentar `limit` na busca

### Problema: Custos muito altos

**Sintoma**: Faturamento semanal > US$50

**Diagnóstico:**
```python
orchestrator = get_orchestrator()
metrics = orchestrator.get_metrics()
total_cost = metrics["llm_client"]["total_cost"]
total_tokens = metrics["llm_client"]["total_tokens"]

print(f"Custo total: US${total_cost:.2f}")
print(f"Tokens: {total_tokens:,}")
```

**Soluções:**
1. Aumentar cache TTL
2. Implementar cache warming
3. Usar modelo menor (haiku) para testes
4. Reduzir tamanho dos prompts
5. Limitar requisições por usuário

---

## 🔄 Manutenção Rotineira

### Diária

- [ ] Verificar health checks
- [ ] Monitorar métricas de custo
- [ ] Verificar taxas de erro
- [ ] Review logs de erro

### Semanal

- [ ] Analisar tendências de uso
- [ ] Otimizar prompts se necessário
- [ ] Review e ajustar cache TTLs
- [ ] Verificar créditos das APIs

### Mensal

- [ ] Análise de custos detalhada
- [ ] Otimizar performance se necessário
- [ ] Atualizar documentação
- [ ] Revisar e ajustar feature flags

---

## 📈 Incident Management

### Níveis de Severidade

**P1 - Crítico:**
- Sistema completamente fora
- Perda de dados
- Perda financeira significativa

**P2 - Alto:**
- Degradação severa de performance
- Alta taxa de erros
- Funcionalidade limitada

**P3 - Médio:**
- Degradação moderada
- Taxa de erros aumentada
- Alguns recursos não funcionando

**P4 - Baixo:**
- Problemas menores
- Questões de performance
- Melhorias desejáveis

### Procedimento P1

1. **Identificar** (5 min)
   ```bash
   # Verificar status dos serviços
   docker-compose ps

   # Verificar health
   curl http://localhost:8000/health/ai

   # Verificar logs
   docker-compose logs --tail=100 backend
   ```

2. **Mitigar** (10 min)
   ```bash
   # Se AI service com problema, desabilitar
   # No .env ou variável de ambiente:
   ENABLE_AI_SERVICE=false

   # Reiniciar backend
   docker-compose restart backend
   ```

3. **Resolver** (tempo variável)
   - Seguir runbook específico do incidente
   - Envolver equipe se necessário
   - Documentar resolução

4. **Post-Mortem** (1 dia após)
   - Documentar causa raiz
   - Atualizar runbooks
   - Implementar melhorias preventivas

---

## 🔐 Segurança

### API Keys

**Never commit API keys to repository!**

**Gerenciar Keys:**
- Usar variáveis de ambiente
- Rotacionar keys mensalmente
- Usar keys separadas para prod/dev/test
- Monitorar uso de keys

**Verificar exposição:**
```bash
# Verificar se keys estão em código
grep -r "sk-ant" backend/app --include="*.py"
grep -r "sk-" backend/app --include="*.py"
```

### Rate Limiting

**Limites Configurados:**
```python
# Em config.py
RATE_LIMIT_PER_MINUTE: int = 100  # Ajustar conforme necessário
RATE_LIMIT_BURST: int = 200
```

**Ajustar limites:**
1. Editar `config.py`
2. Reiniciar backend
3. Monitorar impactos

---

## 📊 Backup e Restore

### Backup de Dados

**Automático (via Docker volumes):**
```bash
# Dados PostgreSQL
docker volume ls | grep postgres

# Dados Redis
docker volume ls | grep redis
```

**Export manual:**
```bash
# Exportar veículos com embeddings
docker-compose exec postgres pg_dump -U postgres -d car_ads_db \
  -t vehicles --no-owner > vehicles_backup.sql
```

### Restore

**Restaurar de backup:**
```bash
# Restaurar PostgreSQL
docker-compose exec -T postgres psql -U postgres -d car_ads_db < vehicles_backup.sql
```

---

## 🚀 Deploy

### Deploy em Produção

**Checklist:**
- [ ] API keys de produção configuradas
- [ ] Feature flags ajustadas
- [ ] Rate limiting configurado
- [ ] Redis persistente configurado
- [ ] Backup automatizado ativo
- [ ] Monitoramento configurado
- [ ] Logs centralizados
- [ ] Health checks configurados

**Comandos:**
```bash
# 1. Build imagem Docker
docker-compose -f docker/docker-compose.yml build backend

# 2. Parar serviços atuais
docker-compose -f docker/docker-compose.yml down

# 3. Iniciar novos serviços
docker-compose -f docker/docker-compose.yml up -d

# 4. Verificar health
curl http://localhost:8000/health/ai
```

### Deploy com Zero Downtime

**Estratégia:**
1. Atualizar serviço novo em paralelo
2. Migrar database gradualmente
3. Trocar roteamento
4. Desativar serviço antigo

---

## 📝 SOPs Procedimentos Operacionais Padrão

### SOP-001: Iniciar Novo Servidor

**Objetivo**: Iniciar novo servidor com AI Service

**Passos:**
1. Clonar repositório
2. Configurar `.env` com API keys
3. Iniciar Docker services
4. Rodar migrações (`alembic upgrade head`)
5. Validar setup (`python scripts/validate_ai_setup.py`)
6. Iniciar backend
7. Verificar health check

### SOP-002: Atualizar AI Service

**Objetivo**: Atualizar para nova versão

**Passos:**
1. Fazer backup dos dados
2. Parar backend
3. Pull novo código
4. Instalar dependências (`pip install -r requirements.txt`)
5. Rodar migrações (`alembic upgrade head`)
6. Iniciar backend
7. Validar funcionalidades
8. Monitorar por 1 hora

### SOP-003: Responder a Alerta de Custo

**Objetivo**: Ajustar serviço se custos muito altos

**Passos:**
1. Identificar causa (ver métricas)
2. Se token usage alto: otimizar prompts
3. Se error rate alto: investigar falhas
4. Se volume alto: implementar rate limiting
5. Documentar mudanças

---

## 🎓 Formação e Conhecimento

### Para Time de Desenvolvimento

**Conceitos Chave:**
1. **Agent Architecture**: Orchestrator + Agents especializados
2. **Fallback Strategy**: Claude primário, OpenAI secundário
3. **Circuit Breaker**: Prevenir falhas em cascata
4. **Vector Embeddings**: Representação numérica de texto
5. **Semantic Search**: Busca por similaridade de contexto
6. **Feature Store**: Cache inteligente de features

**Recursos de Aprendizado:**
- Arquitetura: `docs/dia2-arquitetura/ai-agent-structure.md`
- Roadmap: `docs/referencias/roadmap.md`
- Este runbook

### Para Time de Operações

**Procedimentos Críticos:**
1. Health checks
2. Incident response
3. Backup/restore
4. Monitoramento
5. Custos

**Métricas Importantes:**
- Disponibilidade: > 99.9%
- Performance: P95 < 3s (análise)
- Custo: < US$50/mês (esperado)
- Error rate: < 1%

---

## 📞 Contatos e Escalation

### Time Técnico

**Engenheiro de AI/ML**: [Contato]
**Tech Lead**: [Contato]
**DevOps Engineer**: [Contato]

### Escalation Matrix

| Tempo | Escalação | Contato |
|-------|----------|---------|
| Imediato | Time Técnico | Slack #ai-service |
| 1 hora | Tech Lead | Slack #tech-lead |
| 4 horas | Gerência | Email |
| 24 horas | CTO | Email |

---

## 📚 Referências Internas

- Setup: `AI_SERVICE_SETUP.md`
- Validação: `VALIDATION_CHECKLIST.md`
- Testes: `TESTING.md`
- Roadmap: `docs/referencias/roadmap.md`
- Arquitetura: `docs/dia2-arquitetura/`

---

**Versão**: 2.0.0
**Última Atualização**: 15/04/2026
**Próxima Revisão**: Conforme necessidade
