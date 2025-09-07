// eventix/lib/pages/splash_screen.dart
import 'package:flutter/material.dart';
import 'package:eventix/services/local_storage.dart';
import 'package:provider/provider.dart';
import 'package:eventix/providers/user_provider.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkLogin();
  }

  Future<void> _checkLogin() async {
    try {
      print('🔑 Splash: Iniciando verificação de login...');

      // Adiciona um delay mínimo para mostrar o splash
      await Future.delayed(const Duration(seconds: 2));

      if (!mounted) return;

      // Lê token com timeout
      final token = await LocalStorage.getAccessToken().timeout(
        const Duration(seconds: 5),
        onTimeout: () {
          print('🔑 Splash: Timeout ao ler token');
          return null;
        },
      );

      debugPrint('TOKEN DIRETO 1: $token');
      print('🔑 Splash: Token encontrado: ${token != null ? "SIM" : "NÃO"}');

      if (token != null && token.isNotEmpty) {
        print('🔑 Splash: Token válido, carregando dados do usuário...');

        // Pega também os dados salvos do freelancer com timeout
        final id = await LocalStorage.getUserId().timeout(
          const Duration(seconds: 3),
          onTimeout: () {
            print('🔑 Splash: Timeout ao ler ID do usuário');
            return 0;
          },
        );

        final nome = await LocalStorage.getNome().timeout(
          const Duration(seconds: 3),
          onTimeout: () {
            print('🔑 Splash: Timeout ao ler nome');
            return '';
          },
        );

        final email = await LocalStorage.getEmail().timeout(
          const Duration(seconds: 3),
          onTimeout: () {
            print('🔑 Splash: Timeout ao ler email');
            return '';
          },
        );

        final tipoUsuario = await LocalStorage.getTipoUsuario().timeout(
          const Duration(seconds: 3),
          onTimeout: () {
            print('🔑 Splash: Timeout ao ler tipo de usuário');
            return '';
          },
        );

        print(
            '🔑 Splash: Dados carregados - ID: $id, Nome: $nome, Email: $email, Tipo: $tipoUsuario');

        if (!mounted) return;

        // Atualiza o Provider
        context.read<UserProvider>().setUserData(
              id: id,
              nome: nome,
              email: email,
              tipoUsuario: tipoUsuario,
            );

        if (!mounted) return;
        // Vai para Home
        print('🔑 Splash: Navegando para /home');
        Navigator.pushReplacementNamed(context, '/home');
      } else {
        if (!mounted) return;
        // Vai para Login
        print('🔑 Splash: Navegando para /login');
        Navigator.pushReplacementNamed(context, '/login');
      }
    } catch (e) {
      print('🔑 Splash: Erro durante verificação: $e');
      if (!mounted) return;
      // Em caso de erro, vai para login
      Navigator.pushReplacementNamed(context, '/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D1117),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo do Eventix
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                color: const Color(0xFF6366F1),
              ),
              child: const Icon(
                Icons.event,
                size: 60,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'Eventix',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Organização é o espetáculo',
              style: TextStyle(
                fontSize: 16,
                color: Color(0xFFB0B3B8),
              ),
            ),
            const SizedBox(height: 48),
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF6366F1)),
            ),
          ],
        ),
      ),
    );
  }
}
