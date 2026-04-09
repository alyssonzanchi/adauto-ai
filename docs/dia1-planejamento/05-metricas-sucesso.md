# Métricas de Sucesso - Sistema de Anúncios Patrocinados

**Data**: 16/03/2026
**Versão**: 1.0

---

## 1. Visão Geral

Este documento define todas as métricas de sucesso para medir a efetividade do sistema de anúncios patrocinados, incluindo métricas técnicas, de negócio e de performance de anúncios.

---

## 2. Métricas de Performance de Anúncios

### 2.1 Métricas de Awareness (Consciência)

#### Impressões
**Definição**: Número de vezes que o anúncio foi exibido

**Fórmula**: Total de visualizações do anúncio

**Meta**:
- Mínimo aceitável: 10.000 impressões/mês
- Meta saudável: 50.000+ impressões/mês
- Excepcional: 100.000+ impressões/mês

**Como Medir**:
- Via API de cada plataforma (Facebook Ads, Google Ads)
- Dashboard do sistema agregando todas as plataformas

**Alertas**:
- Alerta se < 5.000 impressões em 7 dias (baixa distribuição)

---

#### Alcance
**Definição**: Número único de pessoas que viram o anúncio

**Fórmula**: Pessoas únicas alcançadas

**Meta**:
- Mínimo aceitável: 60% do total de impressões
- Meta saudável: 70-80%
- Excepcional: 85%+

**Como Medir**:
- APIs das plataformas fornecem reach único

**Análise**:
- Alcance baixo + Impressões altas = Saturação (mesmo público vendo várias vezes)

---

### 2.2 Métricas de Engajamento

#### CTR - Click-Through Rate
**Definição**: Porcentagem de pessoas que clicaram no anúncio após visualizá-lo

**Fórmula**: `(Cliques / Impressões) × 100`

**Meta**:
- Mínimo aceitável: 1.0%
- Meta saudável: 2.0-3.0%
- Excepcional: 4.0%+

**Por Plataforma**:
| Plataforma | CTR Mínimo | CTR Saudável | CTR Excepcional |
|------------|------------|--------------|-----------------|
| Facebook | 0.8% | 1.5-2.5% | 3.5%+ |
| Instagram | 0.9% | 1.8-3.0% | 4.0%+ |
| Google Search | 3.0% | 5.0-8.0% | 10.0%+ |
| Google Display | 0.3% | 0.5-0.8% | 1.2%+ |

**Como Melhorar**:
- Criativos mais atraentes
- Headlines mais impactantes
- Segmentação mais precisa
- Testar A/B variações

---

#### Taxa de Engajamento
**Definição**: Porcentagem de qualquer tipo de engajamento (curtidas, comentários, compartilhamentos, cliques)

**Fórmula**: `(Total Engajamentos / Alcance) × 100`

**Meta**:
- Mínimo aceitável: 2.0%
- Meta saudável: 4.0-6.0%
- Excepcional: 8.0%+

**Componentes**:
- Reações (curtis, amei, etc.)
- Comentários
- Compartilhamentos
- Cliques em link
- Cliques para mais informações

---

#### Taxa de Conversão do Anúncio
**Definição**: Porcentagem de cliques que resultaram em uma conversão (lead, contato, WhatsApp)

**Fórmula**: `(Conversões / Cliques) × 100`

**Meta**:
- Mínimo aceitável: 2.0%
- Meta saudável: 4.0-6.0%
- Excepcional: 8.0%+

**O que Conta como Conversão**:
- Clique no botão do WhatsApp
- Preenchimento de formulário
- Clique em "Ligar Agora"
- Envio de mensagem via Messenger
- Clique no link para ver detalhes do veículo

---

### 2.3 Métricas de Custo

#### CPC - Custo Por Clique
**Definição**: Valor médio pago por cada clique no anúncio

**Fórmula**: `Valor Gasto / Total de Cliques`

**Meta**:
- Mínimo aceitável: R$ 3.00
- Meta saudável: R$ 1.50 - R$ 2.50
- Excepcional: < R$ 1.50

**Por Plataforma**:
| Plataforma | CPC Médio | CPC Meta |
|------------|-----------|----------|
| Facebook | R$ 1.50 - R$ 3.00 | R$ 2.00 |
| Instagram | R$ 2.00 - R$ 4.00 | R$ 2.50 |
| Google Search | R$ 3.00 - R$ 8.00 | R$ 4.00 |
| Google Display | R$ 0.80 - R$ 2.00 | R$ 1.50 |

**Fatores que Influenciam**:
- Segmentação (quanto mais específica, mais caro)
- Concorrência por palavras-chave
- Qualidade do anúncio (Quality Score)
- Relevância da landing page

---

#### CPL - Custo Por Lead
**Definição**: Valor médio pago por cada lead qualificado gerado

**Fórmula**: `Valor Gasto / Total de Leads`

**Meta**:
- Mínimo aceitável: R$ 80.00
- Meta saudável: R$ 40.00 - R$ 70.00
- Excepcional: < R$ 40.00

**Diferença entre Lead x Clique**:
- Clique: Pessoa clicou no anúncio
- Lead: Pessoa deixou contato (WhatsApp, telefone, formulário)

**ROI Baseado em CPL**:
- Se cada venda vale R$ 5.000 de comissão
- E taxa de fechamento é 20%
- CPL aceitável: R$ 5.000 × 20% = R$ 1.000
- CPL meta: R$ 400 - R$ 800 (conservador)

---

#### CPM - Custo Por Mil Impressões
**Definição**: Valor pago a cada 1.000 impressões do anúncio

**Fórmula**: `(Valor Gasto / Impressões) × 1.000`

**Meta**:
- Facebook/Instagram: R$ 15 - R$ 30 por 1.000
- Google Display: R$ 10 - R$ 25 por 1.000

**Uso**:
- Comparar custos entre campanhas
- Campanhas de awareness

---

#### CPA - Custo Por Aquisição
**Definição**: Valor médio pago por cada venda realizada

**Fórmula**: `Valor Gasto / Total de Vendas`

**Meta**:
- Depende do valor do veículo
- Recomendado: < 5% do valor do veículo

**Exemplo**:
- Veículo de R$ 50.000
- CPA aceitável: R$ 2.500 (5%)
- CPA meta: R$ 1.500 (3%)

---

### 2.4 Métricas de Receita

#### ROI - Retorno sobre Investimento
**Definição**: Retorno financeiro obtido em relação ao valor investido

**Fórmula**: `((Receita Gerada - Custo do Anúncio) / Custo do Anúncio) × 100`

**Meta**:
- Mínimo aceitável: 200%
- Meta saudável: 300-500%
- Excepcional: 500%+

**Exemplo**:
- Investido: R$ 1.000 em anúncios
- Receita gerada: R$ 5.000 (venda de 1 carro com R$ 5.000 de lucro)
- ROI: ((5.000 - 1.000) / 1.000) × 100 = 400%

---

#### ROAS - Return on Ad Spend
**Definição**: Receita gerada a cada R$ 1 investido em publicidade

**Fórmula**: `Receita Gerada / Custo do Anúncio`

**Meta**:
- Mínimo aceitável: 3.0
- Meta saudável: 4.0 - 6.0
- Excepcional: 7.0+

**Exemplo**:
- Investido: R$ 1.000
- Receita: R$ 5.000
- ROAS: 5.0 (a cada R$ 1 investido, gera R$ 5)

---

#### Valor do Ticket Médio
**Definição**: Valor médio das vendas geradas pelos anúncios

**Fórmula**: `Receita Total / Número de Vendas`

**Meta**:
- Depende do mix de veículos
- Usar como baseline: comparar ticket médio de vendas orgânicas vs pagas

**Análise**:
- Se ticket pago < ticket orgânico: anúncios atraindo público de menor poder aquisitivo
- Se ticket pago > ticket orgânico: anúncios atraindo público qualificado

---

## 3. Métricas do Sistema (Técnicas)

### 3.1 Métricas de Performance da IA

#### Tempo de Resposta do Agente
**Definição**: Tempo médio para o agente AI analisar um veículo e gerar sugestões

**Medição**: Do recebimento dos dados até a entrega das recomendações

**Meta**:
- Aceitável: < 10 segundos
- Saudável: 3-5 segundos
- Excepcional: < 3 segundos

**Componentes**:
- Extração de características: 1-2s
- Análise de preço: 1-2s
- Geração de copy: 2-4s
- Recomendações de segmentação: 1-2s

**Como Otimizar**:
- Cache de respostas similares
- Modelos menores quando possível
- Processamento assíncrono

---

#### Precisão das Previsões
**Definição**: Acurácia do modelo ML em prever conversões, CTR, etc.

**Fórmula**: `(Previsões Corretas / Total de Previsões) × 100`

**Meta**:
- Previsão de CTR: > 75% de precisão (±0.5%)
- Previsão de conversão: > 70% de precisão (±2%)
- Recomendação de preço: > 80% de precisão (±5%)

**Como Medir**:
- Comparar previsão vs real após 7-30 dias
- Mean Absolute Error (MAE)
- Root Mean Square Error (RMSE)

---

#### Taxa de Rejeição de Sugestões
**Definição**: Porcentagem de sugestões da IA que foram modificadas/ignoradas pelo usuário

**Fórmula**: `(Sugestões Modificadas / Total de Sugestões) × 100`

**Meta**:
- Aceitável: < 40%
- Saudável: 20-30%
- Excepcional: < 20%

**Análise Qualitativa**:
- Por que as sugestões foram rejeitadas?
- Coletar feedback dos usuários
- A/B test com/sem sugestões da IA

---

### 3.2 Métricas de Disponibilidade

#### Uptime do Sistema
**Definição**: Porcentagem de tempo que o sistema esteve disponível

**Fórmula**: `(Tempo Disponível / Tempo Total) × 100`

**Meta**:
- Mínimo aceitável: 99.0%
- Meta saudável: 99.5%
- Excepcional: 99.9%

**Monitoramento**:
- Uptime externo (Pingdom, StatusCake)
- Health checks internos
- Alertas automáticos

---

#### Tempo de Uptime Sem Interrupção
**Definição**: Maior período contínuo sem downtime

**Meta**:
- Mínimo aceitável: 7 dias
- Saudável: 30+ dias
- Excepcional: 90+ dias

---

### 3.3 Métricas de Qualidade de Código

#### Cobertura de Testes
**Definição**: Porcentagem do código coberto por testes automatizados

**Meta**:
- Backend: > 80%
- Frontend: > 70%
- Críticos (payments, auth): 100%

---

#### Taxa de Bugs em Produção
**Definição**: Número de bugs críticos encontrados em produção por mês

**Meta**:
- Aceitável: < 5 bugs/mês
- Saudável: 1-2 bugs/mês
- Excepcional: 0 bugs críticos/mês

---

## 4. Métricas de Negócio

### 4.1 Métricas de Adoção

#### Taxa de Ativação de Revendas
**Definição**: Porcentagem de revendas cadastradas que criaram pelo menos 1 anúncio

**Fórmula**: `(Revendas com Anúncios / Total de Revendas) × 100`

**Meta**:
- Mês 1: > 60%
- Mês 3: > 75%
- Mês 6: > 85%

---

#### Taxa de Retenção de Revendas
**Definição**: Porcentagem de revendas que continuam usando o sistema após X meses

**Fórmula**: `(Revendas Ativas no Mês X / Revendas do Mês Inicial) × 100`

**Meta**:
- Retenção Mês 1: > 80%
- Retenção Mês 3: > 70%
- Retenção Mês 6: > 60%
- Retenção Mês 12: > 50%

---

#### Taxa de Churn
**Definição**: Porcentagem de revendas que cancelam o serviço por mês

**Fórmula**: `(Cancelamentos no Mês / Total de Revendas) × 100`

**Meta**:
- Aceitável: < 5% ao mês
- Saudável: 2-3% ao mês
- Excepcional: < 2% ao mês

---

### 4.2 Métricas de Uso

#### Veículos Cadastrados por Revenda
**Definição**: Média de veículos cadastrados por revenda ativa

**Meta**:
- Mês 1: > 10 veículos
- Mês 3: > 25 veículos
- Mês 6: > 50 veículos

---

#### Campanhas Criadas por Semana
**Definição**: Média de campanhas criadas por revenda por semana

**Meta**:
- Mínimo: 1 campanha/semana
- Saudável: 3-5 campanhas/semana
- Excepcional: 7+ campanhas/semana

---

#### Taxa de Uso de Sugestões IA
**Definição**: Porcentagem de anúncios criados usando as sugestões da IA

**Fórmula**: `(Anúncios com Sugestões IA / Total de Anúncios) × 100`

**Meta**:
- Mês 1: > 50%
- Mês 3: > 70%
- Mês 6: > 80%

---

### 4.3 Métricas de Satisfação

#### NPS - Net Promoter Score
**Definição**: Mede lealdade e satisfação do cliente

**Pergunta**: "Em uma escala de 0-10, qual a probabilidade de você recomendar nosso sistema a outro revendedor?"

**Classificação**:
- Promotores (9-10)
- Neutros (7-8)
- Detratores (0-6)

**Fórmula**: `% Promotores - % Detratores`

**Meta**:
- Aceitável: 0-20
- Saudável: 30-50
- Excepcional: 50+

---

#### Satisfação Média (CSAT)
**Definição**: Média de avaliações de satisfação

**Escala**: 1-5 estrelas

**Meta**:
- Aceitável: 3.5/5
- Saudável: 4.0-4.5/5
- Excepcional: > 4.5/5

---

#### Tempo Resposta Suporte
**Definição**: Tempo médio para primeira resposta do suporte

**Meta**:
- Chat ao vivo: < 2 minutos
- Email: < 4 horas
- Telefone: < 1 minuto

---

## 5. Comparativo: Com Sistema vs Sem Sistema

### 5.1 Benchmarks de Mercado

#### Criando Anúncios Manualmente
- **Tempo médio**: 45-60 minutos por anúncio
- **CTR médio**: 1.2-1.8%
- **Taxa de conversão**: 2-3%
- **CPC médio**: R$ 3.00 - R$ 5.00

#### Com Sistema + IA
- **Tempo médio**: 10-15 minutos por anúncio
- **CTR meta**: 2.0-3.0% (+67%)
- **Taxa de conversão meta**: 4-6% (+100%)
- **CPC meta**: R$ 1.50 - R$ 3.00 (-40%)

### 5.2 Melhorias Esperadas

| Métrica | Manual | Com Sistema | Melhoria |
|---------|--------|-------------|----------|
| Tempo criação | 50 min | 12 min | **76% mais rápido** |
| CTR | 1.5% | 2.5% | **+67%** |
| Conversão | 2.5% | 5.0% | **+100%** |
| CPC | R$ 4.00 | R$ 2.50 | **-37%** |
| CPL | R$ 100 | R$ 50 | **-50%** |

---

## 6. Dashboards e Relatórios

### 6.1 Dashboard Principal

**Visão Geral** (Top Cards):
- Total gasto no período
- Total de impressões
- Total de cliques
- CTR médio
- Total de leads
- CPL médio
- ROI médio
- Veículos ativos

**Gráficos**:
- Impressões por dia (linha)
- Cliques por dia (linha)
- Leads por dia (barras)
- CTR semanal (linha)
- CPL semanal (linha)
- Top 5 veículos por performance (tabela)

---

### 6.2 Relatório de Veículo Individual

**Cards de Métricas**:
- Campanhas ativas
- Total impressões
- Total cliques
- CTR
- Leads gerados
- Taxa de conversão
- Custo total
- CPL
- ROI estimado (baseado no valor do veículo)

**Gráficos Temporais**:
- Métricas ao longo do tempo (7, 15, 30 dias)
- Comparação vs média da categoria

**Sugestões IA**:
- "Aumentar orçamento" (se performando bem)
- "Pausar anúncio" (se performando mal)
- "Testar novo criativo" (se fadiga)
- "Ajustar segmentação" (se CTR baixo)

---

### 6.3 Relatório Semanal Automático

**Enviado por email** toda segunda-feira:

```markdown
# Relatório Semanal - [Nome Revenda]

## Resumo da Semana
- Período: [Data Início] - [Data Fim]
- Total Gasto: R$ X.XXX
- Cliques: X.XXX
- Leads: XX
- CPL: R$ XX
- ROI: XXX%

## Top 3 Veículos
1. [Veículo] - X leads, R$ XX CPL
2. [Veículo] - X leads, R$ XX CPL
3. [Veículo] - X leads, R$ XX CPL

## Oportunidades de Melhoria
- [Veículo com baixo CTR]: Testar novo criativo
- [Veículo com alto CPL]: Ajustar segmentação

## Recomendações da IA
- [X sugestões geradas]
```

---

### 6.4 Alertas Automáticos

**Por Email/Notificação**:

**Alerta Verde (Boas Notícias)**:
- ✅ Veículo com CTR > 4%
- ✅ Veículo com CPL < R$ 30
- ✅ Campanha com ROI > 500%

**Alerta Amarelo (Atenção)**:
- ⚠️ Veículo sem impressões há 24h
- ⚠️ Veículo com CTR < 1%
- ⚠️ Veículo com CPL > R$ 100

**Alerta Vermelho (Ação Necessária)**:
- 🚨 Orçamento esgotado
- 🚨 Conta de ads suspensa
- 🚨 Anúncio reprovado

---

## 7. Acompanhamento e Review

### 7.1 Review Diário (Automático)

Sistema verifica automaticamente a cada hora:
- Status das campanhas
- Orçamentos
- Métricas anômalas

### 7.2 Review Semanal (Equipe)

Toda segunda:
- Analisar top performers
- Identificar underperformers
- Ajustar estratégias
- Planejar semana seguinte

### 7.3 Review Mensal (Executivo)

Todo dia 1 do mês:
- Análise completa do mês anterior
- Comparação vs mês anterior
- Comparação vs benchmarks
- Planejamento estratégico

---

**Próximo Documento**: [06-concorrentes-pesquisa.md](./06-concorrentes-pesquisa.md)
