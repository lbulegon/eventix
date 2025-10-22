# 🚀 CONFIGURAÇÃO RÁPIDA - TWILIO

## ✅ PASSO 1: Criar arquivo .env

Na raiz do projeto `C:\Users\Liandro\Documents\Github\eventix\`, crie um arquivo chamado `.env` com este conteúdo:

```bash
# Django
DJANGO_SECRET_KEY=dev-secret-key-change-me
DEBUG=True

# Twilio - Suas Credenciais
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_VERIFY_SID=OBTER_NO_PASSO_2
TWILIO_MESSAGING_SERVICE_SID=OBTER_NO_PASSO_3
```

---

## ✅ PASSO 2: Criar Verify Service

1. Acesse: https://console.twilio.com/us1/develop/verify/services
2. Clique em **"Create new Service"** (botão azul)
3. **Friendly name:** `Eventix Verify`
4. Clique em **Create**
5. Copie o **SERVICE SID** (começa com `VA...`)
6. Cole no `.env` na linha `TWILIO_VERIFY_SID=`

---

## ✅ PASSO 3: Criar Messaging Service

1. Acesse: https://console.twilio.com/us1/develop/sms/services
2. Clique em **"Create Messaging Service"**
3. **Friendly name:** `Eventix Messaging`
4. **Select what you want to use Messaging for:** `Notify my users`
5. Clique em **Create Messaging Service**
6. Copie o **MESSAGING SERVICE SID** (começa com `MG...`)
7. Cole no `.env` na linha `TWILIO_MESSAGING_SERVICE_SID=`

### Adicionar WhatsApp Sandbox:
1. Na página do Messaging Service que você acabou de criar
2. Clique na aba **"Senders"**
3. Clique em **"Add Senders"**
4. Selecione **"WhatsApp Sender"**
5. Marque a checkbox do **WhatsApp Sandbox**
6. Clique em **"Add WhatsApp Senders"**

---

## ✅ PASSO 4: Conectar seu WhatsApp ao Sandbox

1. Acesse: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Você verá algo como:

```
Join your sandbox
Send this message:
  join happy-tiger
  
To WhatsApp number:
  +1 415 523 8886
```

3. No seu celular:
   - Abra WhatsApp
   - Envie mensagem para `+1 415 523 8886`
   - Texto: `join [o-código-que-aparece]`
   - Exemplo: `join happy-tiger`

4. Você receberá: **"You are all set! ✨"**

**⚠️ IMPORTANTE:** Só números que enviarem "join" recebem mensagens!

---

## ✅ PASSO 5: Testar o Envio

Depois de configurar tudo:

```bash
# 1. Verificar configuração
python manage.py shell -c "from app_eventos.services.twilio_service import TwilioService; t = TwilioService(); print('Configurado:', t.is_configured())"

# 2. Testar com dry-run
python manage.py enviar_whatsapp_freelancers --mensagem "Teste" --dry-run

# 3. Enviar mensagem real
python manage.py enviar_whatsapp_freelancers --mensagem "🎉 Olá do Eventix!"
```

---

## 📱 Arquivo .env Completo

```bash
# Django
DJANGO_SECRET_KEY=dev-secret-key-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# Database Local (SQLite)
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# Twilio - WhatsApp & SMS
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_VERIFY_SID=VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_MESSAGING_SERVICE_SID=MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Firebase (Push Notifications)
FCM_SERVER_KEY=

# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN=
```

Substitua os `xxxxxx` pelos SIDs que você obtiver nos passos 2 e 3!

---

## 🎯 Checklist Final

- [ ] Arquivo `.env` criado na raiz do projeto
- [ ] TWILIO_ACCOUNT_SID configurado (AC40427...)
- [ ] TWILIO_AUTH_TOKEN configurado (d465dc94...)
- [ ] Verify Service criado e SID copiado
- [ ] Messaging Service criado e SID copiado
- [ ] WhatsApp Sandbox adicionado ao Messaging Service
- [ ] Seu celular conectado ao sandbox (enviou "join")
- [ ] Testado com dry-run
- [ ] Primeiro envio real funcionou ✅

---

**Dúvidas? Me chame! 😊**

