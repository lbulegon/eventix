# 📊 Sistema de Logging - Eventix

## 🎯 Visão Geral

O Eventix implementa um sistema completo de logging que permite monitorar, analisar e evoluir o aplicativo de forma consistente. O sistema inclui:

- **Logging Estruturado**: Logs organizados por categorias e níveis
- **Analytics**: Métricas de uso e comportamento do usuário
- **Crash Reporting**: Relatórios automáticos de erros e crashes
- **Performance Monitoring**: Monitoramento de performance de operações
- **API Logging**: Logs detalhados de todas as requisições HTTP

## 🏗️ Arquitetura

### Componentes Principais

1. **AppLogger** (`lib/utils/app_logger.dart`)
   - Sistema central de logging
   - Múltiplos níveis: debug, info, warning, error, fatal
   - Categorias: auth, api, ui, navigation, storage, network, performance, crash, analytics, business

2. **AnalyticsService** (`lib/services/analytics_service.dart`)
   - Integração com Firebase Analytics
   - Eventos personalizados do app
   - Métricas de negócio

3. **CrashService** (`lib/services/crash_service.dart`)
   - Integração com Firebase Crashlytics
   - Relatórios automáticos de crashes
   - Dados customizados do usuário

4. **PerformanceService** (`lib/services/performance_service.dart`)
   - Monitoramento de performance
   - Timers automáticos
   - Estatísticas de operações

5. **LoggingInterceptor** (`lib/services/logging_interceptor.dart`)
   - Interceptor para requisições HTTP
   - Logs automáticos de API calls

## 📝 Como Usar

### 1. Logs Básicos

```dart
import 'package:eventix/utils/app_logger.dart';

// Log de informação
AppLogger.info(
  'User performed action',
  category: LogCategory.business,
  data: {'action': 'view_vaga', 'vaga_id': '123'},
);

// Log de erro
AppLogger.error(
  'API request failed',
  category: LogCategory.api,
  error: exception,
  data: {'endpoint': '/api/vagas', 'status_code': 500},
);

// Log de warning
AppLogger.warning(
  'Slow network detected',
  category: LogCategory.network,
  data: {'response_time_ms': 5000},
);
```

### 2. Logs de Performance

```dart
import 'package:eventix/services/performance_service.dart';

// Medir operação assíncrona
final result = await PerformanceService.measureOperation(
  'load_vagas',
  () async => await ApiClient.get('/api/vagas'),
);

// Medir operação síncrona
final data = PerformanceService.measureSyncOperation(
  'process_data',
  () => processLargeDataset(),
);

// Timer manual
PerformanceService.startTimer('custom_operation');
// ... fazer operação ...
final duration = PerformanceService.stopTimer('custom_operation');
```

### 3. Analytics

```dart
import 'package:eventix/services/analytics_service.dart';

// Eventos específicos do app
await AnalyticsService.logVagaView('vaga_123', 'Garçom para Evento');
await AnalyticsService.logCandidatura('vaga_123', 'Garçom para Evento');
await AnalyticsService.logSearch('garçom', 'vagas');

// Eventos customizados
await AnalyticsService.logEvent(
  'custom_event',
  parameters: {
    'category': 'user_action',
    'value': 100,
  },
);
```

### 4. Crash Reporting

```dart
import 'package:eventix/services/crash_service.dart';

// Configurar dados do usuário
await CrashService.setUserData(
  userId: 'user_123',
  userType: 'freelancer',
  userStatus: 'active',
);

// Log customizado
await CrashService.log('User started important operation');

// Dados customizados
await CrashService.setCustomKey('app_version', '1.0.0');
await CrashService.setCustomKey('user_premium', true);
```

### 5. Logs de Navegação

```dart
// Log automático de navegação
AppLogger.logNavigation(
  '/login',
  '/home',
  parameters: {'user_type': 'freelancer'},
);
```

### 6. Logs de API

```dart
// Logs automáticos via interceptor
// Todas as requisições HTTP são logadas automaticamente

// Log manual de API
AppLogger.logApi(
  'POST',
  '/api/login',
  200,
  requestData: {'email': 'user@example.com'},
  responseData: {'token': 'abc123'},
  duration: Duration(milliseconds: 500),
);
```

## 📊 Categorias de Log

### LogCategory.auth
- Logins, logouts, autenticação
- Falhas de autenticação
- Renovação de tokens

### LogCategory.api
- Requisições HTTP
- Respostas de API
- Erros de rede

### LogCategory.ui
- Interações do usuário
- Navegação entre telas
- Estados da interface

### LogCategory.navigation
- Mudanças de rota
- Parâmetros de navegação
- Histórico de navegação

### LogCategory.storage
- Operações de armazenamento local
- Cache de dados
- Sincronização

### LogCategory.network
- Status de conectividade
- Qualidade da rede
- Timeouts

### LogCategory.performance
- Tempo de execução
- Uso de memória
- Operações lentas

### LogCategory.crash
- Erros fatais
- Crashes do app
- Exceções não tratadas

### LogCategory.analytics
- Métricas de uso
- Eventos de negócio
- KPIs do app

### LogCategory.business
- Ações do usuário
- Conversões
- Métricas de negócio

## 🔧 Configuração

### Inicialização

O sistema é inicializado automaticamente no `main.dart`:

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Inicializa Firebase
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  
  // Inicializa serviços de logging
  await AppLogger.initialize();
  await CrashService.initialize();
  await AnalyticsService.initialize();
  
  runApp(MyApp());
}
```

### Configuração do Firebase

1. Configure o projeto Firebase
2. Adicione os arquivos de configuração:
   - `android/app/google-services.json`
   - `ios/Runner/GoogleService-Info.plist`
3. Atualize `firebase_options.dart` com as configurações reais

## 📈 Monitoramento

### Firebase Console

- **Analytics**: Eventos e métricas de uso
- **Crashlytics**: Relatórios de crashes e erros
- **Performance**: Métricas de performance

### Logs Locais

Em modo debug, todos os logs são exibidos no console com formatação colorida.

### Logs Remotos

Em produção, logs críticos são enviados automaticamente para o Firebase.

## 🎯 Boas Práticas

### 1. Use Categorias Apropriadas
```dart
// ✅ Bom
AppLogger.info('User logged in', category: LogCategory.auth);

// ❌ Ruim
AppLogger.info('User logged in', category: LogCategory.api);
```

### 2. Inclua Dados Relevantes
```dart
// ✅ Bom
AppLogger.info(
  'Vaga viewed',
  category: LogCategory.business,
  data: {
    'vaga_id': '123',
    'vaga_title': 'Garçom',
    'user_type': 'freelancer',
  },
);

// ❌ Ruim
AppLogger.info('Vaga viewed', category: LogCategory.business);
```

### 3. Use Níveis Apropriados
```dart
// ✅ Bom
AppLogger.debug('Cache hit', category: LogCategory.storage);
AppLogger.info('User action', category: LogCategory.business);
AppLogger.warning('Slow network', category: LogCategory.network);
AppLogger.error('API failed', category: LogCategory.api);
AppLogger.fatal('App crash', category: LogCategory.crash);
```

### 4. Não Logue Informações Sensíveis
```dart
// ✅ Bom
AppLogger.info(
  'Login attempt',
  data: {'email': 'user@example.com'},
);

// ❌ Ruim
AppLogger.info(
  'Login attempt',
  data: {
    'email': 'user@example.com',
    'password': 'secret123', // ❌ Nunca logue senhas!
  },
);
```

### 5. Use Performance Monitoring
```dart
// ✅ Bom
final result = await PerformanceService.measureOperation(
  'load_vagas',
  () => ApiClient.get('/api/vagas'),
);

// ❌ Ruim
final start = DateTime.now();
final result = await ApiClient.get('/api/vagas');
final duration = DateTime.now().difference(start);
// Log manual desnecessário
```

## 🚀 Próximos Passos

1. **Configurar Firebase**: Adicionar configurações reais do Firebase
2. **Implementar Logs**: Adicionar logging em todas as funcionalidades
3. **Monitorar Métricas**: Acompanhar logs no Firebase Console
4. **Otimizar Performance**: Usar dados de performance para otimizações
5. **Alertas**: Configurar alertas para erros críticos

## 📚 Recursos Adicionais

- [Firebase Analytics](https://firebase.google.com/docs/analytics)
- [Firebase Crashlytics](https://firebase.google.com/docs/crashlytics)
- [Flutter Logging Best Practices](https://docs.flutter.dev/development/tools/logging)
