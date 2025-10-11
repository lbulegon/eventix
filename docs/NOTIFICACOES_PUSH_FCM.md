# Sistema de Notificações Push - Firebase Cloud Messaging (FCM)

## 📱 Visão Geral

O sistema envia notificações push automaticamente para freelancers quando uma vaga compatível com suas funções cadastradas é criada.

## 🔧 Configuração

### 1. Configurar Firebase

1. Acesse o [Firebase Console](https://console.firebase.google.com/)
2. Crie um novo projeto ou use um existente
3. Vá em **Configurações do Projeto** > **Cloud Messaging**
4. Copie a **Chave do Servidor (Server Key)**

### 2. Configurar Variável de Ambiente

Adicione a chave do servidor no arquivo `.env` ou nas variáveis de ambiente:

```bash
FCM_SERVER_KEY=sua_chave_do_servidor_aqui
```

### 3. Aplicar Migração

```bash
python manage.py migrate app_eventos
```

## 🚀 Como Funciona

### Fluxo Automático

1. **Empresa cria vaga** no dashboard (`/empresa/`)
2. **Signal detecta** a criação da vaga
3. **Sistema busca** freelancers que têm a função da vaga cadastrada
4. **Filtra freelancers** com:
   - Cadastro completo
   - Notificações ativas
   - Device token configurado
5. **Envia notificação push** para todos os freelancers elegíveis

### Campos Adicionados ao Modelo Freelance

```python
device_token = models.CharField(max_length=255, blank=True, null=True)
notificacoes_ativas = models.BooleanField(default=True)
```

## 📡 API Endpoints

### Registrar Device Token

**POST** `/api/v1/notificacoes/registrar-token/`

**Headers:**
```
Authorization: Bearer {token_jwt}
Content-Type: application/json
```

**Body:**
```json
{
    "device_token": "token_fcm_do_dispositivo"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Device token registrado com sucesso",
    "device_token": "token_fcm_do_dispositivo",
    "notificacoes_ativas": true
}
```

### Desativar Notificações

**POST** `/api/v1/notificacoes/desativar/`

**Headers:**
```
Authorization: Bearer {token_jwt}
```

**Response:**
```json
{
    "success": true,
    "message": "Notificações desativadas com sucesso",
    "notificacoes_ativas": false
}
```

## 🔔 Formato da Notificação

### Título
```
Nova Vaga Disponível!
```

### Mensagem
```
{titulo_da_vaga} - R$ {remuneracao}
```

### Dados Adicionais (payload)
```json
{
    "vaga_id": "123",
    "titulo": "Segurança do Evento",
    "remuneracao": "200.00",
    "tipo_remuneracao": "por_dia",
    "evento_nome": "Show de Música",
    "setor_nome": "Segurança"
}
```

## 🧪 Teste Manual

### 1. Configurar Token de Teste

```bash
python manage.py shell -c "
from app_eventos.models import Freelance
freelancer = Freelance.objects.first()
freelancer.device_token = 'TOKEN_DE_TESTE_AQUI'
freelancer.notificacoes_ativas = True
freelancer.save()
print(f'Token configurado para: {freelancer.nome_completo}')
"
```

### 2. Criar Vaga e Testar

```bash
# No dashboard da empresa:
1. Acesse /empresa/eventos/{id}/
2. Clique em "Adicionar Setor"
3. Crie um setor
4. Clique em "Adicionar Vaga"
5. Preencha os dados da vaga
6. Salve

# A notificação será enviada automaticamente!
```

## 📊 Logs e Monitoramento

O sistema imprime logs no console:

- `✓ Notificações enviadas: X/Y freelancers para vaga: {titulo}`
- `ℹ Nenhum freelancer com notificações ativas para a vaga: {titulo}`
- `✗ Erro ao enviar notificação: {erro}`

## 🔐 Segurança

- Apenas freelancers autenticados podem registrar tokens
- Tokens são armazenados de forma segura no banco de dados
- Freelancers podem desativar notificações a qualquer momento

## 📱 Integração no App Mobile

### Flutter/Dart Example

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

// Obter token FCM
Future<String?> getDeviceToken() async {
  final FirebaseMessaging messaging = FirebaseMessaging.instance;
  final token = await messaging.getToken();
  return token;
}

// Registrar token no backend
Future<void> registrarToken(String token) async {
  final response = await http.post(
    Uri.parse('$baseUrl/api/v1/notificacoes/registrar-token/'),
    headers: {
      'Authorization': 'Bearer $jwtToken',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'device_token': token}),
  );
}
```

## ⚠️ Importante

1. **FCM_SERVER_KEY** deve estar configurado para as notificações funcionarem
2. O app mobile deve ter o **Firebase configurado**
3. Freelancers devem ter **funções cadastradas** para receber notificações relevantes
4. Apenas vagas **ativas** com **função definida** geram notificações
