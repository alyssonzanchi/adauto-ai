# Google Ads Integration - Setup Guide

## 📋 Pré-requisitos

### Contas Necessárias
1. **Google Account**
   - Acesse: https://accounts.google.com
   - Crie uma conta (gratuita)

2. **Google Ads Manager Account** (opcional mas recomendado)
   - Acesse: https://ads.google.com/aw/ap
   - Crie uma conta de administrador
   - Anote o Customer ID (formato: XXX-XXX-XXXX)

3. **Google Cloud Project**
   - Projeto no Google Cloud Console
   - APIs habilitadas

---

## 🔧 Passo 1: Criar Google Cloud Project

### 1.1 Acessar Google Cloud Console
1. Vá para: https://console.cloud.google.com
2. Crie um novo projeto
3. Nome do projeto: "Car Ads Platform" (ou seu nome preferido)
4. Anote o Project ID

### 1.2 Habilitar APIs
1. No menu, vá em **"APIs & Services"** → **"Library"**
2. Pesquise e habilite:
   - ✅ **Google Ads API**

### 1.3 Configurar OAuth Consent Screen
1. Vá em **"APIs & Services"** → **"OAuth consent screen"**
2. Selecione **"External"** (para produção)
3. Preencha os dados:
   - **App name**: Car Ads Platform
   - **User support email**: Seu email
   - **Developer contact**: Seu email
   - **Scopes**: Adicione `https://www.googleapis.com/auth/adwords`
4. Clique em **"Save"** e depois verifique o app (requer verificação para produção)

---

## 🔐 Passo 2: Configurar OAuth 2.0

### 2.1 Criar OAuth Client IDs
1. Vá em **"APIs & Services"** → **"Credentials"**
2. Clique em **"Create Credentials"** → **"OAuth client ID"**
3. Selecione o tipo de aplicação: **"Web application"**

### 2.2 Configurar Redirect URIs
Em **"Authorized redirect URIs"**, adicione:

```
# Development
http://localhost:8000/api/v1/integrations/google/callback

# Production
https://api.adauto.com.br/api/v1/integrations/google/callback

# Staging
https://staging-api.adauto.com.br/api/v1/integrations/google/callback
```

### 2.3 Obter Credenciais
1. Clique em **"Create"**
2. Copie:
   - **Client ID**: ID público do cliente OAuth
   - **Client Secret**: Segredo do cliente OAuth (não compartilhe!)

---

## 📱 Passo 3: Obter Developer Token

### 3.1 Solicitar Developer Token
1. Acesse: https://ads.google.com/aw/ap
2. Faça login com sua conta do Google Ads
3. Vá em **"Tools & Settings"** (ícone de ferramentas)
4. Em **"Setup"**, clique em **"API Center"**
5. Clique em **"Apply for API access"**
6. Preencha os dados:
   - **API Access Level**: Basic ou Standard
   - **Purpose**: Integration with Car Ads Platform
   - **Website URL**: Seu website
7. Aguarde aprovação (pode levar de 1 a 5 dias úteis)

### 3.2 Anotar Developer Token
1. Após aprovação, o Developer Token estará disponível
2. Copie o token (formato alfanumérico longo)
3. Mantenha seguro!

---

## 🔑 Passo 4: Obter Customer ID

### 4.1 Verificar Customer ID
1. Acesse: https://ads.google.com/aw/ap
2. No canto superior direito, você verá o Customer ID
3. Formato: XXX-XXX-XXXX
4. Anote este ID

### 4.2 Criar Conta de Teste (Opcional)
Para testes, você pode criar uma conta de teste:
1. No Google Ads Manager, vá em **"Tools & Settings"**
2. Clique em **"Account Management"**
3. Clique no botão **"+"** → **"New Account"**
4. Preencha os dados da conta de teste

---

## 🔧 Passo 5: Configurar Variáveis de Ambiente

### 5.1 Backend (.env)
Adicione ao arquivo `backend/.env`:

```env
# Google Ads Integration
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token_here
GOOGLE_ADS_CLIENT_ID=your_oauth_client_id_here
GOOGLE_ADS_CLIENT_SECRET=your_oauth_client_secret_here
GOOGLE_ADS_REDIRECT_URI=http://localhost:8000/api/v1/integrations/google/callback
GOOGLE_ADS_API_VERSION=v12
```

### 5.2 Frontend (.env.local)
Adicione ao arquivo `frontend/.env.local`:

```env
# Google Integration
NEXT_PUBLIC_GOOGLE_ADS_CLIENT_ID=your_oauth_client_id_here
```

---

## 🧪 Passo 6: Testar Integração

### 6.1 Testar OAuth Flow
1. Inicie o backend:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Teste o endpoint de conexão:
```bash
curl -X POST http://localhost:8000/api/v1/integrations/google/connect \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

3. Resposta esperada:
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "random_state_string"
}
```

4. Abra a URL no navegador
5. Faça login e autorize o app
6. Você será redirecionado para o callback

### 6.2 Testar Publicação de Ad
```bash
curl -X POST http://localhost:8000/api/v1/ads/AD_ID/publish/google \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d "google_customer_id=123-456-7890" \
  -d "campaign_name=Test Campaign" \
  -d "ad_group_name=Test AdGroup" \
  -d "budget_amount=100.0"
```

### 6.3 Testar Sync de Métricas
```bash
curl -X POST http://localhost:8000/api/v1/integrations/google/sync/123-456-7890/metrics \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🚨 Troubleshooting

### Erro 1: "Invalid developer token"
**Causa**: Developer token não configurado ou inválido
**Solução**:
1. Verifique se GOOGLE_ADS_DEVELOPER_TOKEN está configurado
2. Verifique se o token foi aprovado pelo Google
3. Aguarde aprovação (pode levar dias)

### Erro 2: "OAuth client ID invalid"
**Causa**: Client ID ou Secret incorretos
**Solução**:
1. Verifique se GOOGLE_ADS_CLIENT_ID está correto
2. Verifique se GOOGLE_ADS_CLIENT_SECRET está correto
3. Recrie OAuth Client IDs no Google Cloud Console
4. Verifique se a redirect URI está correta

### Erro 3: "Access token expired"
**Causa**: Access token expirou (60 min)
**Solução**:
1. Use refresh_token para obter novo access token
2. Implemente refresh automático de tokens
3. Verifique se a função `refresh_access_token` está sendo chamada

### Erro 4: "Customer ID not found"
**Causa**: Customer ID incorreto ou sem permissão
**Solução**:
1. Verifique se o Customer ID está correto (formato: XXX-XXX-XXXX)
2. Verifique se a conta está ativa
3. Verifique se o usuário tem acesso à conta
4. Use uma conta de teste para desenvolvimento

### Erro 5: "Quota exceeded"
**Causa**: Limite de quota da API do Google Ads
**Solução**:
1. Aguarde reset da quota (diário)
2. Otimize queries GAQL para reduzir chamadas
3. Implemente rate limiting
4. Considere aumentar quota (contatar Google)

### Erro 6: "Invalid redirect URI"
**Causa**: Redirect URI não configurada ou incorreta
**Solução**:
1. Verifique se a URI exata está configurada no Google Cloud Console
2. Verifique se não há barras extras ou faltando
3. Certifique-se de usar http:// para localhost

---

## 📊 Google Ads API Limits

### Quotas
- **Basic Access**: 5.000 unidades/dia
- **Standard Access**: 25.000 unidades/dia
- **Operations**: Cada operação consome unidades

### Costos por Operação
- **Search**: 100 unidades
- **Mutate**: 500 unidades
- **Query (GAQL)**: 10-100 unidades (depende da complexidade)

### Best Practices
1. **Use GAQL efficiently**: Queries otimizadas
2. **Batch operations**: Múltiplas operações em um request
3. **Cache responses**: Reduza chamadas repetidas
4. **Minimize polling**: Use webhooks quando disponível
5. **Handle quotas**: Implemente rate limiting

---

## 🔒 Segurança

### Proteção de Credenciais
1. **Never log tokens**
2. **Use HTTPS em produção**
3. **Encrypt tokens no banco** (refresh tokens)
4. **Use system users em produção**
5. **Rotate tokens periodicamente**

### OAuth Security
1. **Use state parameter** (já implementado)
2. **Validate redirect URI**
3. **PKCE flow recomendado** (opcional para mobile)
4. **Token storage**: Store refresh tokens encrypted
5. **Auto-refresh**: Implement refresh automático

---

## 📚 Recursos Adicionais

### Documentação Oficial
- [Google Ads API Docs](https://developers.google.com/google-ads/api/docs)
- [Python Client Library](https://github.com/googleads/google-ads-python)
- [OAuth 2.0 Guide](https://developers.google.com/google-ads/api/docs/oauth/overview)
- [GAQL Reference](https://developers.google.com/google-ads/api/docs/query/gaql-reference)

### Exemplos de Código
- [Python Samples](https://github.com/googleads/google-ads-python/tree/main/examples)
- [Ad Creation](https://developers.google.com/google-ads/api/docs/fields/v15/ad_group_ad)
- [Query Builder](https://developers.google.com/google-ads/api/docs/query-builder)

### Ferramentas
- [Google Ads Query Builder](https://developers.google.com/google-ads/api/docs/query-builder)
- [OAuth Playground](https://developers.google.com/oauthplayground/)
- [Google Ads Manager](https://ads.google.com/aw/ap)

---

## 🚀 Deploy Checklist

### Pré-Produção
- [ ] Google Cloud Project criado
- [ ] APIs habilitadas
- [ ] OAuth consent screen configurado
- [ ] OAuth Client IDs criados
- [ ] Developer token aprovado
- [ ] Contas de teste criadas
- [ ] Variáveis de ambiente configuradas
- [ ] Testes executados

### Produção
- [ ] OAuth consent screen verificado
- [ ] Client IDs de produção criados
- [ ] Developer token de produção
- [ ] Redirect URIs de produção
- [ ] Implementar refresh automático de tokens
- [ ] Configurar monitoramento
- [ ] Implementar alertas de quota
- [ ] Documentar OAuth flow
- [ ] Testar com contas reais
- [ ] Implementar disaster recovery

---

## ✅ Checklist Final

- [x] Google Cloud Project criado
- [x] APIs habilitadas
- [x] OAuth consent screen configurado
- [x] OAuth Client IDs criados
- [x] Developer token obtido (ou em processo)
- [x] Customer ID anotado
- [x] Variáveis de ambiente configuradas
- [x] Testes executados
- [x] Documentação lida

---

**Pronto para usar Google Ads Integration!** 🚀

Para suporte, consulte:
- [Google Ads Community](https://support.google.com/google-ads/community)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/google-ads-api)
- [Google Ads API Forum](https://groups.google.com/g/adwords-api)
