# 📱 Sistema Twilio - WhatsApp & SMS - Guia Completo

## 📖 Visão Geral

Sistema completo de notificações via WhatsApp e SMS usando Twilio, integrado ao Eventix para comunicação com freelancers que não têm o app instalado.

---

## 🎯 Casos de Uso

### **1. Verificação de Telefone (OTP)**
- Onboarding de novos usuários
- Recuperação de acesso
- Verificação de número em 2FA

### **2. Notificações de Vagas**
- Alertar freelancers sobre novas vagas
- Matching automático por função
- Fallback automático WhatsApp → SMS

### **3. Alertas e Emergências**
- Avisos de última hora
- Mudanças no evento
- Comunicação urgente

### **4. Broadcast (Envio em Massa)**
- Campanhas para múltiplos freelancers
- Atualizações gerais
- Lembretes de eventos

---

## ⚙️ Configuração

### **1. Criar Conta no Twilio**

1. Acesse: [https://www.twilio.com/](https://www.twilio.com/)
2. Crie uma conta (tem trial gratuito com créditos)
3. Acesse o Console: [https://console.twilio.com/](https://console.twilio.com/)

### **2. Obter Credenciais**

**Account SID e Auth Token:**
- Dashboard → Account Info
- Copie o **Account SID** e **Auth Token**

**Verify Service (para OTP):**
- Products → Verify → Create Service
- Copie o **Verify Service SID**

**Messaging Service (para WhatsApp/SMS):**
- Products → Messaging → Services → Create Service
- Copie o **Messaging Service SID**

### **3. Configurar WhatsApp**

**WhatsApp Sandbox (Desenvolvimento):**
1. Console → Messaging → Try WhatsApp
2. Envie mensagem do seu celular: `join [seu-código]`
3. Use o número sandbox fornecido

**WhatsApp Business (Produção):**
1. Console → Messaging → Senders → WhatsApp
2. Conecte número WhatsApp Business
3. Submeta templates para aprovação do Meta
4. Aguarde aprovação (1-2 dias)

### **4. Variáveis de Ambiente (.env)**

```bash
# Twilio - WhatsApp & SMS
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_VERIFY_SID=VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_MESSAGING_SERVICE_SID=MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### **5. Instalar Dependência**

```bash
pip install twilio==9.8.4
```

Ou atualizar requirements.txt e rodar:
```bash
pip install -r requirements.txt
```

---

## 🗃️ Modelos de Dados

### **UserContact**
Contatos de usuários para WhatsApp/SMS

```python
- empresa_contratante: FK (multi-tenant)
- user: FK User (opcional)
- freelancer: FK Freelance (opcional)
- channel_type: 'whatsapp' | 'sms'
- address: '+5511999999999' (E.164)
- consent: boolean
- is_verified: boolean
```

### **OtpLog**
Log de códigos OTP enviados

```python
- empresa_contratante: FK
- address: número telefone
- purpose: 'signup' | 'login' | 'password_reset'
- status: 'sent' | 'verified' | 'expired'
- provider_sid: Twilio SID
```

### **BroadcastLog**
Campanhas de envio em massa

```python
- empresa_contratante: FK
- campaign_name: nome da campanha
- total_targets: total de destinatários
- sent, delivered, failed: estatísticas
- evento: FK (opcional)
```

### **BroadcastMessage**
Mensagens individuais de um broadcast

```python
- broadcast: FK BroadcastLog
- to_address: número destinatário
- status: 'sent' | 'delivered' | 'failed'
- message_sid: Twilio SID
```

---

## 🔌 Endpoints da API

### **POST /api/v1/twilio/verify/start**
Inicia verificação de telefone (envia código OTP)

**Request:**
```json
{
  "phone_e164": "+5511999999999",
  "empresa_id": 8,
  "channel": "whatsapp",
  "purpose": "signup"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Código enviado via whatsapp",
  "channel": "whatsapp",
  "to": "+5511999999999",
  "sid": "VExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

---

### **POST /api/v1/twilio/verify/check**
Verifica código OTP

**Request:**
```json
{
  "phone_e164": "+5511999999999",
  "code": "123456",
  "empresa_id": 8,
  "channel": "whatsapp"
}
```

**Response:**
```json
{
  "verified": true,
  "message": "Telefone verificado com sucesso",
  "contact_id": 15
}
```

---

### **POST /api/v1/twilio/broadcast**
Envio em massa (requer autenticação de admin)

**Request:**
```json
{
  "campaign_name": "Alerta Portão B",
  "body": "⚠️ *Eventix*: Portão B fechado. Use o Portão C.",
  "targets": ["+5511999999999", "+5521988888888"],
  "preferred_channel": "whatsapp",
  "evento_id": 5
}
```

**Response:**
```json
{
  "success": true,
  "broadcast_id": 42,
  "stats": {
    "total": 2,
    "sent": 2,
    "failed": 0
  }
}
```

---

### **POST /api/v1/twilio/notificar-vaga**
Notifica freelancers sobre nova vaga

**Request:**
```json
{
  "vaga_id": 147
}
```

**Response:**
```json
{
  "success": true,
  "total_freelancers": 15,
  "notificados": 14,
  "erros": 1
}
```

---

### **POST /api/v1/twilio/status**
Webhook do Twilio (atualiza status de mensagens)

---

## 🚀 Como Usar (Linha de Comando)

### **Enviar para Todos os Freelancers**

```bash
python manage.py enviar_whatsapp_freelancers \
  --mensagem "🎉 Bem-vindo ao Eventix! Confira as vagas disponíveis no app."
```

### **Apenas Cadastros Completos**

```bash
python manage.py enviar_whatsapp_freelancers \
  --mensagem "Nova vaga disponível!" \
  --apenas-completos
```

### **Filtrar por Função**

```bash
python manage.py enviar_whatsapp_freelancers \
  --mensagem "Vagas de Segurança disponíveis!" \
  --funcao "Segurança"
```

### **Enviar por SMS**

```bash
python manage.py enviar_whatsapp_freelancers \
  --mensagem "Alerta importante!" \
  --canal sms
```

### **Testar (Dry-Run)**

```bash
python manage.py enviar_whatsapp_freelancers \
  --mensagem "Teste" \
  --dry-run
```

---

## 💡 Exemplos de Uso (Python/Django)

### **1. Enviar Código de Verificação**

```python
from app_eventos.services.twilio_service import TwilioService

twilio = TwilioService()

# Enviar código OTP via WhatsApp
verification = twilio.start_verify(
    phone_e164='+5511999999999',
    channel='whatsapp'
)

# Verificar código
is_valid = twilio.check_verify(
    phone_e164='+5511999999999',
    code='123456',
    channel='whatsapp'
)
```

### **2. Notificar Freelancers sobre Vaga**

```python
from app_eventos.models import Vaga
from app_eventos.services.twilio_service import TwilioService

vaga = Vaga.objects.get(id=147)
twilio = TwilioService()

# Buscar freelancers com a função
freelancers = vaga.funcao.freelancers.filter(cadastro_completo=True)

for freelancer in freelancers:
    phone = twilio.format_phone_e164(freelancer.telefone)
    twilio.send_vaga_notification(phone, vaga, vaga.evento)
```

### **3. Broadcast para Lista**

```python
twilio = TwilioService()

phones = ['+5511999999999', '+5521988888888', '+5531977777777']
mensagem = "⚠️ Atualização: Evento adiado para amanhã."

stats = twilio.send_broadcast(
    phone_list=phones,
    body=mensagem,
    preferred_channel='whatsapp'
)

print(f"Enviados: {stats['sent']}/{stats['total']}")
```

---

## 📝 Templates de Mensagens

### **WhatsApp - Código de Acesso**
```
🎉 *Eventix*

Seu código de acesso é: *123456*

⏰ Expira em 10 minutos.
🔒 Não compartilhe este código.

Bem-vindo ao Eventix!
```

### **WhatsApp - Nova Vaga**
```
💼 *Nova Vaga Disponível!*

*Segurança de Portaria*
💰 R$ 250.00 (Por Dia)

📅 Evento: Festival de Música 2025
📍 Local: Centro de Convenções SP

🔗 Acesse o app Eventix para se candidatar!
```

### **WhatsApp - Candidatura Aprovada**
```
✅ *Candidatura Aprovada!*

Parabéns! Você foi aprovado para:

*Segurança de Portaria*
📅 Evento: Festival de Música 2025
📍 Centro de Convenções SP
🗓️ Data: 15/11/2025

Em breve você receberá mais informações.

🎉 Nos vemos lá!
```

### **WhatsApp - Alerta de Emergência**
```
⚠️ *EVENTIX - Atualização Importante*

Portão B temporariamente fechado.
Dirija-se ao Portão C.

Para mais informações, acesse o app Eventix.
```

### **SMS - Código (Curto)**
```
Eventix: seu código é 123456. Expira em 10 min. Não compartilhe.
```

---

## 🛡️ Boas Práticas

### **1. Formato E.164**
Sempre use formato internacional:
- ✅ `+5511999999999`
- ❌ `(11) 99999-9999`
- ❌ `11999999999`

O serviço converte automaticamente com `format_phone_e164()`.

### **2. Rate Limiting**
- Máximo 1 código OTP a cada 60 segundos
- Máximo 5 tentativas por hora por número
- Implementar cooldown no backend

### **3. Opt-Out (STOP)**
- Respeitar quando usuário enviar "STOP"
- Remover da lista de broadcast
- Atualizar campo `consent` para `False`

### **4. Logs e Observabilidade**
- Todos os envios são logados (OtpLog, BroadcastLog)
- MessageSid do Twilio salvo para rastreamento
- Status atualizado via webhook

### **5. Fallback Inteligente**
- Tentar WhatsApp primeiro (mais rico e barato)
- Se falhar, enviar SMS automaticamente
- Sistema implementa isso com `send_with_fallback()`

---

## 🔧 Comandos Úteis

### **Verificar Configuração**
```bash
python manage.py shell -c "from app_eventos.services.twilio_service import TwilioService; t = TwilioService(); print('Configurado:', t.is_configured())"
```

### **Listar Freelancers com Telefone**
```bash
python manage.py shell -c "from app_eventos.models import Freelance; print(f'Total: {Freelance.objects.filter(telefone__isnull=False).exclude(telefone=\"\").count()}')"
```

### **Envio de Teste**
```bash
# Simulação (não envia)
python manage.py enviar_whatsapp_freelancers \
  --mensagem "Teste" \
  --dry-run

# Envio real
python manage.py enviar_whatsapp_freelancers \
  --mensagem "Olá! Confira as novas vagas no Eventix!" \
  --apenas-completos
```

---

## 📊 Monitoramento

### **Ver Logs de OTP**
```python
from app_eventos.models_twilio import OtpLog

# Últimos 10 códigos enviados
logs = OtpLog.objects.all()[:10]
for log in logs:
    print(f"{log.address} - {log.purpose} - {log.status}")
```

### **Ver Broadcasts**
```python
from app_eventos.models_twilio import BroadcastLog

# Últimas campanhas
broadcasts = BroadcastLog.objects.all()[:5]
for b in broadcasts:
    print(f"{b.campaign_name}: {b.delivered}/{b.total_targets} ({b.success_rate:.1f}%)")
```

### **Painel Twilio**
- Console: [https://console.twilio.com/](https://console.twilio.com/)
- Logs → Messaging → Message Logs
- Monitor de custos e limites

---

## 💰 Custos (Referência)

| Tipo | Custo Aproximado |
|------|------------------|
| WhatsApp (Twilio Sandbox) | Grátis (desenvolvimento) |
| WhatsApp Business | $0.005 - $0.01 por mensagem |
| SMS Brasil | $0.02 - $0.05 por mensagem |
| Verify (OTP) | $0.05 por verificação |

**Trial do Twilio:** $15 em créditos grátis

---

## 🎨 Interface Web (Futuro)

### **Dashboard Empresa - Broadcast**

Você pode criar uma interface no dashboard para enviar broadcasts:

**URL:** `/empresa/broadcast/`

**Funcionalidades:**
- Selecionar evento
- Filtrar freelancers por função
- Escrever mensagem com preview
- Ver histórico de campanhas
- Estatísticas em tempo real

---

## 🔐 Segurança

### **Webhook do Twilio**

Para validar que o webhook vem realmente do Twilio:

```python
from twilio.request_validator import RequestValidator

validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)

# No webhook
signature = request.META.get('HTTP_X_TWILIO_SIGNATURE')
url = request.build_absolute_uri()
params = request.POST

if validator.validate(url, params, signature):
    # Requisição válida do Twilio
    pass
else:
    # Possível ataque, rejeitar
    return Response(status=403)
```

### **Rate Limiting**

Implementar no Django:
```python
from django.core.cache import cache

def check_rate_limit(phone, action='verify'):
    key = f'twilio_{action}_{phone}'
    attempts = cache.get(key, 0)
    
    if attempts >= 5:  # Máximo 5 em 1 hora
        return False
    
    cache.set(key, attempts + 1, 3600)  # 1 hora
    return True
```

---

## 📱 Integração com Mobile (Flutter)

### **Verificação de Telefone no App**

```dart
// 1. Enviar código
Future<void> enviarCodigoVerificacao(String telefone) async {
  final response = await dio.post(
    '/api/v1/twilio/verify/start/',
    data: {
      'phone_e164': telefone,
      'empresa_id': empresaId,
      'channel': 'whatsapp',
      'purpose': 'signup'
    }
  );
  
  if (response.data['success']) {
    // Mostrar tela de inserir código
    Navigator.push(...);
  }
}

// 2. Verificar código
Future<bool> verificarCodigo(String telefone, String codigo) async {
  final response = await dio.post(
    '/api/v1/twilio/verify/check/',
    data: {
      'phone_e164': telefone,
      'code': codigo,
      'empresa_id': empresaId,
      'channel': 'whatsapp'
    }
  );
  
  return response.data['verified'] == true;
}
```

---

## ⚡ Situação Atual

### ✅ **Implementado:**
1. ✅ Modelos de dados (UserContact, OtpLog, BroadcastLog)
2. ✅ Serviço Twilio completo
3. ✅ Endpoints API (verify, broadcast, webhook)
4. ✅ Comando CLI para envio em massa
5. ✅ Sistema de fallback automático
6. ✅ Templates pré-definidos de mensagens
7. ✅ Configurações no settings.py

### ⏳ **Próximos Passos:**
1. ⏳ Configurar conta Twilio (você precisa fazer)
2. ⏳ Aplicar migration no Railway
3. ⏳ Configurar variáveis de ambiente no Railway
4. ⏳ Testar envio real
5. ⏳ Criar interface web para broadcasts (opcional)

---

## 🧪 Como Testar

### **1. Configurar Twilio Sandbox**

```bash
# No seu celular, envie WhatsApp para:
+1 415 523 8886

# Mensagem:
join [seu-código-sandbox]
```

### **2. Testar Localmente**

```bash
# Dry-run (simulação)
python manage.py enviar_whatsapp_freelancers \
  --mensagem "Teste do sistema" \
  --dry-run

# Se tudo ok, enviar de verdade
python manage.py enviar_whatsapp_freelancers \
  --mensagem "Olá! Sistema Eventix em teste." \
  --apenas-completos
```

### **3. Ver Logs**

```bash
python manage.py shell -c "from app_eventos.models_twilio import OtpLog; [print(f'{l.address} - {l.status}') for l in OtpLog.objects.all()[:10]]"
```

---

## 📚 Recursos

- **Twilio Docs:** [https://www.twilio.com/docs](https://www.twilio.com/docs)
- **WhatsApp API:** [https://www.twilio.com/docs/whatsapp](https://www.twilio.com/docs/whatsapp)
- **Verify API:** [https://www.twilio.com/docs/verify](https://www.twilio.com/docs/verify)
- **Templates WhatsApp:** [https://www.twilio.com/docs/whatsapp/tutorial/send-whatsapp-notification-messages-templates](https://www.twilio.com/docs/whatsapp/tutorial/send-whatsapp-notification-messages-templates)

---

## 🎯 Credenciais de Teste

**Admin Diego:**
```
Login: admin_diego
Senha: diego123
Empresa: Diego Segurança (ID: 8)
```

**Admin Simone:**
```
Login: admin_simone
Senha: simone123
Empresa: Irmãos Trevisan (ID: 1)
```

---

*Documento criado em: Outubro 2025*  
*Projeto: Eventix - Sistema de Gestão de Eventos*  
*Integração: Twilio WhatsApp & SMS*

