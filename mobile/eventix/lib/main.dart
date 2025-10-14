//eventix/lib/main.dart
import 'package:flutter/material.dart';
import 'package:eventix/theme/app_theme.dart';
import 'package:eventix/pages/splash_screen.dart';
import 'package:eventix/pages/login_page.dart';
import 'package:eventix/pages/home_page.dart';
import 'package:eventix/pages/pre_cadastro_page.dart';
import 'package:eventix/utils/navigation_service.dart';
import 'package:eventix/utils/app_logger.dart';
import 'package:eventix/services/analytics_service.dart';
import 'package:eventix/services/crash_service.dart';
import 'package:eventix/services/auth_service.dart';
import 'package:eventix/services/vagas_service.dart';
import 'package:eventix/services/eventos_service.dart';
import 'package:eventix/services/freelancers_service.dart';
import 'package:eventix/services/notificacoes_service.dart';
import 'package:eventix/services/funcoes_service.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:provider/provider.dart';
import 'package:eventix/providers/user_provider.dart';
import 'package:eventix/pages/recuperar_senha_page.dart';
import 'package:eventix/pages/vagas_page.dart';
import 'package:eventix/pages/vagas_recomendadas_page.dart';
import 'package:eventix/pages/minhas_candidaturas_page.dart';
import 'package:eventix/pages/notificacoes_page.dart';
import 'package:eventix/pages/dashboard_freelancer_page.dart';
import 'package:eventix/pages/funcoes_page.dart';

//ola mundo
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Inicializa o app primeiro, depois os serviços em background
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => UserProvider()),
      ],
      child: const MyApp(),
    ),
  );

  // Inicializa serviços em background (não bloqueia o app)
  _initializeServicesInBackground();
}

Future<void> _initializeServicesInBackground() async {
  try {
    print('🚀 Inicializando serviços em background...');

    // Inicializa Firebase
    await Firebase.initializeApp();
    await _initializeFirebaseMessaging();

    // Inicializa formatação de data
    await initializeDateFormatting('pt_BR', null)
        .timeout(const Duration(seconds: 5));

    // Inicializa serviços de logging
    await AppLogger.initialize().timeout(const Duration(seconds: 5));
    await CrashService.initialize().timeout(const Duration(seconds: 5));
    await AnalyticsService.initialize().timeout(const Duration(seconds: 5));

    // Inicializa serviços de API
    await AuthService.initialize().timeout(const Duration(seconds: 10));
    VagasService.initialize();
    EventosService.initialize();
    FreelancersService.initialize();
    NotificacoesService.initialize();
    FuncoesService.initialize();

    AppLogger.info(
      'App started',
      category: LogCategory.analytics,
      data: {'version': '1.0.0'},
    );

    // Verifica se houve crash na execução anterior
    final didCrash = await CrashService.didCrashOnPreviousExecution()
        .timeout(const Duration(seconds: 3));
    if (didCrash) {
      AppLogger.warning(
        'App crashed on previous execution',
        category: LogCategory.crash,
      );
    }

    print('✅ Serviços inicializados com sucesso!');
  } catch (e) {
    // Log de erro na inicialização (não trava o app)
    print('❌ Erro na inicialização dos serviços: $e');
    AppLogger.fatal(
      'Failed to initialize app',
      category: LogCategory.crash,
      error: e,
    );
  }
}

/// Inicializa o Firebase Messaging e configura os handlers
Future<void> _initializeFirebaseMessaging() async {
  try {
    final messaging = FirebaseMessaging.instance;

    // Solicita permissão para notificações
    final settings = await messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print('✅ Permissão de notificações concedida');

      // Obtém o token FCM
      final token = await messaging.getToken();
      print('📱 FCM Token: $token');

      // TODO: Enviar token para o backend
      // await AuthService.updateFcmToken(token);
    } else {
      print('⚠️ Permissão de notificações negada');
    }

    // Handler para mensagens quando o app está em foreground
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print(
          '📬 Mensagem recebida em foreground: ${message.notification?.title}');
      // TODO: Exibir notificação local
    });

    // Handler para quando o usuário toca na notificação (app em background)
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print('📬 App aberto via notificação: ${message.notification?.title}');
      // TODO: Navegar para a tela apropriada
    });

    // Handler para mensagens em background (top-level function)
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  } catch (e) {
    print('❌ Erro ao inicializar Firebase Messaging: $e');
  }
}

/// Handler para mensagens em background (deve ser top-level function)
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('📬 Mensagem em background: ${message.notification?.title}');
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      navigatorKey: navigatorKey,
      debugShowCheckedModeBanner: false,
      title: 'Eventix',
      theme: AppTheme.darkTheme, // Aqui aplica o tema escuro
      // SplashScreen será a primeira tela
      home: const SplashScreen(),
      routes: {
        '/login': (context) => const LoginPage(),
        '/home': (context) => const HomePage(),
        '/pre-cadastro': (context) => const PreCadastroPage(),
        '/recuperar-senha': (context) => const RecuperarSenhaPage(),
        '/vagas': (context) => const VagasPage(),
        '/vagas_recomendadas': (context) => const VagasRecomendadasPage(),
        '/minhas_candidaturas': (context) => const MinhasCandidaturasPage(),
        '/notificacoes': (context) => const NotificacoesPage(),
        '/dashboard_freelancer': (context) => const DashboardFreelancerPage(),
        '/funcoes': (context) => const FuncoesPage(),
      },
    );
  }
}
