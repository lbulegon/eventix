# 🚀 Setup Twilio - Passo a Passo

## ✅ Suas Credenciais

```
Account Name: Eventix
Account SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 📋 Passo 1: Obter Auth Token

1. Acesse: [https://console.twilio.com/](https://console.twilio.com/)
2. Faça login
3. No Dashboard, você verá:
   - **Account SID:** `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` ✅
   - **Auth Token:** Clique em "Show" para revelar
4. Copie o **Auth Token**

---

## 📋 Passo 2: Configurar WhatsApp Sandbox (Desenvolvimento)

### **A. Ativar WhatsApp Sandbox**

1. No Console Twilio: [https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Você verá algo como:

```
Join your sandbox:
Send "join [código]" to: +1 415 523 8886

Exemplo: join happy-tiger
```

### **B. Conectar Seu Celular**

1. No seu celular, abra WhatsApp
2. Adicione o número: `+1 415 523 8886` nos contatos
3. Envie a mensagem: `join [seu-código]` (o código aparece no console)
4. Você receberá uma confirmação: "You are all set!"

**⚠️ IMPORTANTE:** Só números que enviarem "join" receberão mensagens do sandbox!

---

## 📋 Passo 3: Criar Messaging Service

1. Console → **Messaging** → **Services**
2. Clique em **Create Messaging Service**
3. Friendly Name: `Eventix Notifications`
4. Use Case: `Notifications`
5. Clique em **Create Messaging Service**
6. Copie o **Messaging Service SID** (formato: `MGxxxxxxxx...`)

### **Adicionar Sender ao Service**

1. Na página do Messaging Service criado
2. Aba **Senders** → **Add Senders**
3. Selecione o **WhatsApp Sandbox**
4. Salve

---

## 📋 Passo 4: Criar Verify Service (para OTP)

1. Console → **Verify** → **Services**
2. Clique em **Create new Service**
3. Friendly Name: `Eventix Verify`
4. Clique em **Create**
5. Copie o **Verify Service SID** (formato: `VAxxxxxxxx...`)

---

## 📋 Passo 5: Configurar .env

Crie/edite o arquivo `.env` na raiz do projeto:

```bash
# Twilio - WhatsApp & SMS
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=seu_auth_token_aqui
TWILIO_VERIFY_SID=VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_MESSAGING_SERVICE_SID=MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Substitua:**
- `seu_auth_token_aqui` → Auth Token do Dashboard
- `VAxxxxx...` → Verify Service SID
- `MGxxxxx...` → Messaging Service SID

---

## 📋 Passo 6: Configurar no Railway (Produção)

1. Acesse o projeto no Railway
2. Vá em **Variables**
3. Adicione as mesmas variáveis:

```
TWILIO_ACCOUNT_SID = ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN = seu_auth_token_aqui
TWILIO_VERIFY_SID = VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_MESSAGING_SERVICE_SID = MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🧪 Passo 7: Testar

### **A. Verificar Configuração**

```bash
python manage.py shell -c "from app_eventos.services.twilio_service import TwilioService; t = TwilioService(); print('Twilio configurado:', t.is_configured())"
```

Deve retornar: `Twilio configurado: True`

### **B. Testar com Dry-Run**

```bash
python manage.py enviar_whatsapp_freelancers \
  --mensagem "🎉 Teste do Eventix!" \
  --dry-run
```

### **C. Enviar Teste Real**

**⚠️ IMPORTANTE:** Antes de enviar, certifique-se que:
1. ✅ Seu número está conectado ao Sandbox (enviou "join")
2. ✅ Variáveis .env configuradas
3. ✅ Freelancer tem telefone válido

```bash
python manage.py enviar_whatsapp_freelancers \
  --mensagem "🎉 Olá! Este é um teste do sistema Eventix."
```

---

## 🔍 Verificar Telefone Cadastrado

```bash
python manage.py shell -c "from app_eventos.models import Freelance; f = Freelance.objects.first(); print(f'Nome: {f.nome_completo}'); print(f'Telefone: {f.telefone}')"
```

**Formato esperado:**
- Seu telefone: `51994523847` (precisa formatar)
- Formato E.164: `+5551994523847`

O serviço adiciona o `+55` automaticamente!

---

## ⚠️ Troubleshooting

### **Não Recebo a Mensagem?**

**Checklist:**
1. ✅ Você enviou "join [código]" para o número sandbox?
2. ✅ Recebeu confirmação "You are all set!"?
3. ✅ Auth Token está correto no .env?
4. ✅ Messaging Service tem o WhatsApp Sandbox adicionado?
5. ✅ Número do freelancer está no formato correto?

### **Erro "Not Configured"**

```bash
# Reinicie o servidor após configurar .env
# Ctrl+C para parar
python manage.py runserver
```

### **Ver Logs Detalhados**

```bash
# No comando de envio, verá logs como:
✓ WhatsApp enviado para +5551994523847 (SID: SMxxxxxxxx)
```

---

## 📞 Próximo: Adicionar Mais Números ao Sandbox

Para testar com outros números:

1. Pessoa abre WhatsApp
2. Envia mensagem para `+1 415 523 8886`
3. Mensagem: `join [seu-código-sandbox]`
4. Pronto! Pode receber mensagens

**Limite do Sandbox:** Até 5 números conectados

---

## 🎯 Resumo Rápido

```bash
# 1. Configure .env com as 4 variáveis
# 2. Conecte seu WhatsApp ao sandbox
# 3. Teste:

python manage.py enviar_whatsapp_freelancers \
  --mensagem "Teste Eventix" \
  --dry-run

# 4. Se ok, envie de verdade (sem --dry-run)
```

---

Precisa de ajuda com algum passo específico? 😊

