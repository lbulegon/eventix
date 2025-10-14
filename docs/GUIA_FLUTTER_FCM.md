# Guia Flutter FCM - Sistema Eventix

## 📱 Integração Flutter com Backend Django

## 🔧 Configuração Inicial

### Passo 1: Baixar o arquivo `google-services.json`

1. Acesse o [Console do Firebase](https://console.firebase.google.com/)
2. Selecione seu projeto
3. Vá em **Configurações do Projeto** (ícone de engrenagem)
4. Na aba **Geral**, role até **Seus apps**
5. Clique no ícone do Android e faça o download do `google-services.json`

### Passo 2: Colocar o arquivo no lugar correto

**📍 Localização:** `mobile/eventix/android/app/google-services.json`

```
mobile/eventix/
└── android/
    └── app/
        ├── build.gradle.kts
        └── google-services.json  ✅ AQUI!
```

### Passo 3: Configurar o Package Name

No Firebase Console, o **Package Name** deve ser: `com.example.eventix`

Este nome deve corresponder ao `applicationId` em `android/app/build.gradle.kts`:

```kotlin
defaultConfig {
    applicationId = "com.example.eventix"  // Deve corresponder ao Firebase
    // ...
}
```

### Passo 4: Dependências Flutter (pubspec.yaml)

**✅ Versões já instaladas:**

```yaml
dependencies:
  firebase_core: ^2.24.2
  firebase_messaging: ^14.7.10
  firebase_analytics: ^10.8.0
  firebase_crashlytics: ^3.4.9
  dio: ^5.2.0
```

### Passo 5: Gradle Build Files

**✅ Configuração seguindo as instruções oficiais do Firebase!**

**Arquivo do Gradle no nível raiz** (`android/build.gradle.kts`):
```kotlin
plugins {
    // Add the dependency for the Google services Gradle plugin
    id("com.google.gms.google-services") version "4.4.3" apply false
}
```

**Arquivo do Gradle do módulo app** (`android/app/build.gradle.kts`):
```kotlin
plugins {
    id("com.android.application")
    id("kotlin-android")
    id("dev.flutter.flutter-gradle-plugin")
    // Add the Google services Gradle plugin
    id("com.google.gms.google-services")
}

dependencies {
    // Import the Firebase BoM
    implementation(platform("com.google.firebase:firebase-bom:34.3.0"))

    // Firebase products (quando usar BoM, não especificar versões)
    implementation("com.google.firebase:firebase-analytics")
    implementation("com.google.firebase:firebase-messaging")
    implementation("com.google.firebase:firebase-crashlytics")
}
```

**⚡ Vantagem do Firebase BoM:**
Ao usar o BoM (Bill of Materials) do Firebase, você não precisa especificar versões individuais para cada biblioteca Firebase. O BoM garante que todas as bibliotecas sejam compatíveis entre si.

### 2. Inicialização (main.dart)

**✅ Código já implementado no projeto!**

```dart
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:dio/dio.dart';

// Handler de mensagens em background
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('Notificação em background: ${message.notification?.title}');
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  runApp(const EventixApp());
}

class EventixApp extends StatefulWidget {
  const EventixApp({super.key});
  @override
  State<EventixApp> createState() => _EventixAppState();
}

class _EventixAppState extends State<EventixApp> {
  final FirebaseMessaging _fcm = FirebaseMessaging.instance;
  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: "http://localhost:8000/api/v1",  // ou seu URL de produção
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 15),
    ),
  );
  
  String? _jwtToken;  // Token JWT do usuário logado

  @override
  void initState() {
    super.initState();
    _initFCM();
    _listenFCM();
  }

  Future<void> _initFCM() async {
    // Solicitar permissão
    final settings = await _fcm.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );
    
    print('Status permissão: ${settings.authorizationStatus}');

    // Obter token FCM
    final token = await _fcm.getToken();
    if (token != null) {
      print('Token FCM: $token');
      await _registerTokenToBackend(token);
    }

    // Atualizar quando o token mudar
    FirebaseMessaging.instance.onTokenRefresh.listen((newToken) async {
      print('Token atualizado: $newToken');
      await _registerTokenToBackend(newToken);
    });
  }

  void _listenFCM() {
    // App em foreground (app aberto)
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('Mensagem recebida (foreground):');
      print('Título: ${message.notification?.title}');
      print('Corpo: ${message.notification?.body}');
      print('Dados: ${message.data}');
      
      // TODO: Exibir notificação local ou atualizar UI
      _showLocalNotification(message);
    });

    // Usuário clicou na notificação
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print('App aberto via notificação');
      print('Dados: ${message.data}');
      
      // TODO: Navegar para tela da vaga
      if (message.data.containsKey('vaga_id')) {
        final vagaId = message.data['vaga_id'];
        // Navigator.push(...) para tela de detalhes da vaga
      }
    });
  }

  Future<void> _registerTokenToBackend(String token) async {
    try {
      final response = await _dio.post(
        "/notificacoes/registrar-token/",
        data: {"device_token": token},
        options: Options(
          headers: {
            "Authorization": "Bearer $_jwtToken",  // JWT do usuário
            "Content-Type": "application/json",
          },
        ),
      );
      
      print('Token registrado no backend: ${response.data}');
    } catch (e) {
      print('Erro ao registrar token: $e');
    }
  }
  
  void _showLocalNotification(RemoteMessage message) {
    // TODO: Implementar com flutter_local_notifications
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(message.notification?.title ?? 'Nova Notificação'),
        content: Text(message.notification?.body ?? ''),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text('Eventix')),
        body: const Center(child: Text('Sistema de Notificações Configurado ✨')),
      ),
    );
  }
}
```

### 3. Serviço de Autenticação (exemplo)

```dart
class AuthService {
  final Dio _dio;
  
  AuthService(this._dio);
  
  Future<String?> login(String username, String password) async {
    try {
      final response = await _dio.post(
        '/auth/login/',
        data: {
          'username': username,
          'password': password,
        },
      );
      
      final jwtToken = response.data['tokens']['access'];
      
      // Após login bem-sucedido, registrar token FCM
      await _registerFCMToken(jwtToken);
      
      return jwtToken;
    } catch (e) {
      print('Erro no login: $e');
      return null;
    }
  }
  
  Future<void> _registerFCMToken(String jwtToken) async {
    final fcmToken = await FirebaseMessaging.instance.getToken();
    if (fcmToken != null) {
      await _dio.post(
        '/notificacoes/registrar-token/',
        data: {'device_token': fcmToken},
        options: Options(
          headers: {'Authorization': 'Bearer $jwtToken'},
        ),
      );
    }
  }
}
```

## 🔔 Endpoints da API

### Registrar Token
```
POST /api/v1/notificacoes/registrar-token/
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "device_token": "fcm_token_aqui"
}
```

### Desativar Notificações
```
POST /api/v1/notificacoes/desativar/
Authorization: Bearer {jwt_token}
```

## 📦 Formato da Notificação Recebida

```json
{
  "notification": {
    "title": "Nova Vaga Disponível!",
    "body": "Segurança do Evento - R$ 200.00"
  },
  "data": {
    "vaga_id": "134",
    "titulo": "Segurança do Evento",
    "remuneracao": "200.00",
    "tipo_remuneracao": "por_dia",
    "evento_nome": "Evento Teste Diego",
    "setor_nome": "Segurança"
  }
}
```

## 🎯 Fluxo Completo

1. **Freelancer faz login** no app
2. **App obtém token FCM** e envia para backend
3. **Backend associa token** ao freelancer
4. **Empresa cria vaga** no dashboard
5. **Signal detecta** e busca freelancers compatíveis
6. **Notificação enviada** automaticamente! 🎉

## ⚠️ Importante

- Configure `FCM_SERVER_KEY` nas variáveis de ambiente
- Freelancer deve ter **funções cadastradas** (FreelancerFuncao)
- Freelancer deve ter **cadastro completo**
- Apenas vagas **ativas** geram notificações

