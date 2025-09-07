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
// Firebase removido
import 'package:intl/date_symbol_data_local.dart';
import 'package:provider/provider.dart';
import 'package:eventix/providers/user_provider.dart';
import 'package:eventix/pages/recuperar_senha_page.dart';

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

    // Firebase removido

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
      },
    );
  }
}
