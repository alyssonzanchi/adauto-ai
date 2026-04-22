# Facebook Ads Integration - Setup Guide

## 📋 Pré-requisitos

### Contas Necessárias
1. **Facebook Developer Account**
   - Acesse: https://developers.facebook.com
   - Crie uma conta (gratuita)

2. **Facebook Business Manager** (opcional mas recomendado)
   - Acesse: https://business.facebook.com
   - Crie um Business Manager

3. **Facebook Ad Account**
   - Conta de anúncios ativa
   - Permissões de admin

---

## 🔧 Passo 1: Criar Facebook App

### 1.1 Acessar Facebook Developers
1. Vá para: https://developers.facebook.com/apps
2. Clique em "Create App"
3. Selecione o tipo de app: **"Business"**
4. Preencha os dados:
   - **App Name**: Car Ads Platform (ou seu nome)
   - **App Contact**: Seu email

### 1.2 Configurar App Básico
1. No dashboard do app, vá em **"Basic Settings"**
2. Preencha:
   - **App Domains**: Seu domínio (ex: adauto.com.br)
   - **Contact Email**: Seu email
   - **Privacy Policy URL**: URL da sua política de privacidade
   - **User Data Deletion**: URL de callback de deleção
   - **App Icon**: Upload do logo

### 1.3 Adicionar Products
1. No dashboard, clique em **"Add Product"**
2. Adicione:
   - ✅ **Marketing API**
   - ✅ **Facebook Login**

---

## 🔐 Passo 2: Configurar Facebook Login

### 2.1 Configurar OAuth Redirect
1. Vá em **"Facebook Login"** → **"Settings"**
2. Em **"Valid OAuth Redirect URIs"**, adicione:

```
# Development
http://localhost:8000/api/v1/integrations/facebook/callback

# Production
https://api.adauto.com.br/api/v1/integrations/facebook/callback

# Staging
https://staging-api.adauto.com.br/api/v1/integrations/facebook/callback
```

3. Clique em **"Save Changes"**

### 2.2 Configurar Permissions (App Review)
**Importante**: Você precisará submeter seu app para revisão para obter as permissões necessárias.

#### Permissões Padrão (não requer revisão)
- `public_profile`
- `email`

#### Permissões que Requerem Revisão
Para produção, você precisará solicitar acesso a:
- `ads_management`
- `ads_read`
- `pages_manage_ads`
- `pages_read_engagement`
- `read_insights`

**Nota**: Durante desenvolvimento, você pode usar **Test Apps** ou **Test Users** para testar sem revisão.

---

## 📱 Passo 3: Configurar Marketing API

### 3.1 Ativar Marketing API
1. Vá em **"Marketing API"** → **"Settings"**
2. Clique em **"Set Up"**
3. Aceite os termos de uso

### 3.2 Configurar Ad Account
1. Em **"Ad Account"**, selecione sua conta de anúncios
2. Anote o **Account ID** (formato: act_XXXXXXXXX)

### 3.3 Configurar System User (Opcional mas Recomendado)
Para produção, crie um System User:
1. Vá para **Business Settings** → **"System Users"**
2. Crie um novo System User com role **"Admin"**
3. Gere um token de acesso permanente
4. Use este token ao invés de tokens de usuário

---

## 🔑 Passo 4: Obter Credenciais

### 4.1 App ID e App Secret
1. No dashboard do app, vá em **"Basic Settings"**
2. Copie:
   - **App ID**: ID público do app
   - **App Secret**: Chave secreta (não compartilhe!)

### 4.2 Access Token de Teste
Para desenvolvimento:
1. Vá em **"Tools & Support"** → **"Graph API Explorer"**
2. Selecione seu app
3. Clique em **"Generate Access Token"**
4. Selecione as permissões necessárias
5. Copie o token gerado

---

## 🔧 Passo 5: Configurar Variáveis de Ambiente

### 5.1 Backend (.env)
Adicione ao arquivo `backend/.env`:

```env
# Facebook Ads Integration
FACEBOOK_APP_ID=your_facebook_app_id_here
FACEBOOK_APP_SECRET=your_facebook_app_secret_here
FACEBOOK_API_VERSION=v18.0
FACEBOOK_REDIRECT_URI=http://localhost:8000/api/v1/integrations/facebook/callback
```

### 5.2 Frontend (.env.local)
Adicione ao arquivo `frontend/.env.local`:

```env
# Facebook Integration
NEXT_PUBLIC_FACEBOOK_APP_ID=your_facebook_app_id_here
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
curl -X POST http://localhost:8000/api/v1/integrations/facebook/connect \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

3. Resposta esperada:
```json
{
  "authorization_url": "https://www.facebook.com/v18.0/dialog/oauth?...",
  "state": "random_state_string"
}
```

4. Abra a URL no navegador
5. Faça login e autorize o app
6. Você será redirecionado para o callback

### 6.2 Testar Publicação de Ad
```bash
curl -X POST http://localhost:8000/api/v1/ads/AD_ID/publish \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d "facebook_account_id=act_123456789" \
  -d "campaign_name=Test Campaign" \
  -d "adset_name=Test AdSet"
```

### 6.3 Testar Sync de Métricas
```bash
curl -X POST http://localhost:8000/api/v1/integrations/facebook/sync/act_123456789/metrics \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🚨 Troubleshooting

### Erro 1: "Invalid OAuth redirect URI"
**Causa**: URI de redirect não configurada ou incorreta
**Solução**:
1. Verifique se a URI exata está configurada no Facebook App
2. Verifique se não há barras extras ou faltando
3. Certifique-se de usar http:// para localhost

### Erro 2: "Can't load URL: The domain of this URL isn't included in the app's domains"
**Causa**: Domínio não configurado no app
**Solução**:
1. Vá em Basic Settings
2. Adicione o domínio em "App Domains"
3. Use localhost para desenvolvimento

### Erro 3: "Permission denied"
**Causa**: App não tem permissões necessárias
**Solução**:
1. Verifique se as permissões estão solicitadas
2. Para produção, submeta o app para revisão
3. Para desenvolvimento, use Test Users

### Erro 4: "Invalid access token"
**Causa**: Token expirado ou inválido
**Solução**:
1. Gere um novo token no Graph API Explorer
2. Verifique se o token tem as permissões necessárias
3. Para produção, use tokens de longa duração ou System Users

### Erro 5: "Account not found"
**Causa**: Account ID incorreto ou sem permissão
**Solução**:
1. Verifique se o usuário tem acesso à conta
2. Use Graph API Explorer para listar contas disponíveis
3. Verifique se a conta está ativa no Facebook Ads Manager

---

## 📊 Facebook Ads API Limits

### Rate Limits
- **Standard Access**: 200 calls per hour per user
- **High Volume**: Request increased limits

### Best Practices
1. **Cache responses**: Reduza chamadas repetidas
2. **Batch requests**: Use batch API sempre que possível
3. **Webhooks**: Configure webhooks para atualizações em tempo real
4. **Insights**: Use date ranges eficientes

---

## 🔒 Segurança

### Proteção de Access Tokens
1. **Never log tokens**
2. **Use HTTPS em produção**
3. **Encrypt tokens no banco**
4. **Use System Users em produção**
5. **Rotate tokens periodicamente**

### OAuth Security
1. **Use state parameter** (já implementado)
2. **Validate redirect URI**
3. **Short-lived tokens para desenvolvedores**
4. **Long-lived tokens para system users**

---

## 📚 Recursos Adicionais

### Documentação Oficial
- [Facebook Marketing API Docs](https://developers.facebook.com/docs/marketing-apis/)
- [Facebook Business SDK Python](https://github.com/facebook/facebook-business-sdk-python)
- [Facebook Ads Help Center](https://www.facebook.com/business/help)

### Exemplos de Código
- [Marketing API Samples](https://developers.facebook.com/docs/marketing-apis/samples/)
- [Ad Creation Guide](https://developers.facebook.com/docs/marketing-apis/creating-ads)

### Ferramentas
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
- [Share Debug](https://developers.facebook.com/tools/debug/sharing/)

---

## 🚀 Deploy Checklist

### Pré-Produção
- [ ] Submeter app para revisão
- [ ] Configurar domínios de produção
- [ ] Criar System User
- [ ] Configurar webhooks
- [ ] Implementar retry logic
- [ ] Implementar rate limiting
- [ ] Testar com contas reais

### Produção
- [ ] Usar System User tokens
- [ ] Implementar refresh de tokens
- [ ] Configurar monitoramento
- [ ] Implementar alertas de rate limit
- [ ] Documentar OAuth flow
- [ ] Testar disaster recovery

---

## ✅ Checklist Final

- [x] Facebook App criado
- [x] Marketing API ativada
- [x] Facebook Login configurado
- [x] OAuth redirect URI configurada
- [x] Permissões solicitadas
- [ ] App review submetido (produção)
- [x] Variáveis de ambiente configuradas
- [x] Testes executados
- [x] Documentação lida

---

**Pronto para usar Facebook Ads Integration!** 🚀

Para suporte, consulte:
- [Facebook Developers Community](https://developers.facebook.com/community/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/facebook-ads-api)
