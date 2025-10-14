# ⚡ Setup Rápido - Notificações Push FCM

## 🚀 Sistema Já Implementado!

O sistema de notificações push está **completamente funcional**. Quando uma vaga é criada, freelancers com a função compatível recebem notificação automaticamente.

## 📋 Configuração Necessária

### 1. Instalar Firebase Admin SDK

```bash
pip install firebase-admin==6.5.0
```

Ou:
```bash
pip install -r requirements.txt
```

### 2. Obter Credenciais do Firebase

1. Acesse: [Firebase Console](https://console.firebase.google.com/)
2. Selecione seu projeto (ou crie um novo)
3. Vá em **⚙️ Configurações do Projeto** > **Contas de Serviço**
4. Clique em **Gerar nova chave privada**
5. Baixe o arquivo JSON

### 3. Configurar Variável de Ambiente

**Opção A - Arquivo JSON:**
```bash
FIREBASE_SA_PATH=/caminho/para/seu-projeto-firebase-adminsdk.json
```

**Opção B - JSON Inline (Railway/Heroku):**
```bash
FIREBASE_SA_JSON='{"type":"service_account","project_id":"...","private_key":"...",...}'
```

### 4. Aplicar Migração (se ainda não aplicou)

```bash
python manage.py migrate app_eventos
```

## ✅ Como Testar

### Teste 1: Verificar se Firebase está configurado

```bash
python manage.py shell -c "from app_eventos.services.firebase_config import inicializar_firebase; inicializar_firebase()"
```

Deve mostrar: `✓ Firebase inicializado com ...`

### Teste 2: Criar vaga e verificar logs

1. Acesse dashboard: `http://localhost:8000/empresa/login/`
2. Login: `admin_diego` / `diego123`
3. Vá em Eventos > Clique em um evento > Adicionar Vaga
4. Crie uma vaga
5. Verifique no console: `✓ Notificações enviadas: X/Y freelancers`

## 📱 API para App Mobile

### Registrar Token FCM

```http
POST /api/v1/notificacoes/registrar-token/
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "device_token": "token_fcm_do_dispositivo"
}
```

### Response

```json
{
  "success": true,
  "message": "Device token registrado com sucesso",
  "device_token": "...",
  "notificacoes_ativas": true
}
```

## 🔔 Quando as Notificações São Enviadas?

**Automaticamente quando:**
1. Vaga é criada (`created=True`)
2. Vaga está ativa (`ativa=True`)
3. Vaga tem função definida (`funcao` não é null)

**Freelancers notificados:**
1. Têm a função da vaga cadastrada (FreelancerFuncao)
2. Cadastro completo (`cadastro_completo=True`)
3. Notificações ativas (`notificacoes_ativas=True`)
4. Device token configurado (`device_token` não é null)

## 📚 Documentação Completa

- **Guia Flutter:** `docs/GUIA_FLUTTER_FCM.md`
- **Documentação API:** `docs/NOTIFICACOES_PUSH_FCM.md`

## ⚠️ Importante

- **Sem Firebase configurado:** Sistema funciona normalmente, mas não envia notificações
- **Com Firebase configurado:** Notificações são enviadas automaticamente! 🎉

