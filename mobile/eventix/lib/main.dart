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
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:provider/provider.dart';
import 'package:eventix/providers/user_provider.dart';
import 'package:eventix/pages/recuperar_senha_page.dart';

//ola mundo
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    // Inicializa Firebase
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );

    // Inicializa formatação de data
    await initializeDateFormatting('pt_BR', null);

    // Inicializa serviços de logging
    await AppLogger.initialize();
    await CrashService.initialize();
    await AnalyticsService.initialize();

    // Inicializa serviços de API
    await AuthService.initialize();
    VagasService.initialize();
    EventosService.initialize();
    FreelancersService.initialize();

    AppLogger.info(
      'App started',
      category: LogCategory.analytics,
      data: {'version': '1.0.0'},
    );

    // Verifica se houve crash na execução anterior
    final didCrash = await CrashService.didCrashOnPreviousExecution();
    if (didCrash) {
      AppLogger.warning(
        'App crashed on previous execution',
        category: LogCategory.crash,
      );
    }
  } catch (e) {
    // Log de erro na inicialização
    AppLogger.fatal(
      'Failed to initialize app',
      category: LogCategory.crash,
      error: e,
    );
  }

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => UserProvider()),
      ],
      child: const MyApp(),
    ),
  );
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
