//lib/pages/login_page.dart
import 'package:flutter/material.dart';
import 'package:eventix/services/auth_service.dart';
import 'package:provider/provider.dart';
import 'package:eventix/providers/user_provider.dart';
import 'package:eventix/utils/app_logger.dart';
import 'package:eventix/services/analytics_service.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _emailController = TextEditingController();
  final _senhaController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  bool _carregando = false;
  bool _obscurePassword = true;
  String? _erro;

  /// Faz login e salva dados do usuário + tokens
  Future<void> _fazerLogin() async {
    if (!_formKey.currentState!.validate()) {
      AppLogger.warning(
        'Login form validation failed',
        category: LogCategory.auth,
      );
      return;
    }

    setState(() {
      _carregando = true;
      _erro = null;
    });

    AppLogger.info(
      'Login attempt started',
      category: LogCategory.auth,
      data: {
        'email': _emailController.text.trim(),
      },
    );

    try {
      final loginResult = await AuthService.login(
        _emailController.text.trim(),
        _senhaController.text.trim(),
      );

      if (!mounted) return;
      setState(() => _carregando = false);

      if (loginResult != null && loginResult['success'] == true) {
        if (!mounted) return;

        final userData = loginResult['user'];

        AppLogger.info(
          'Login successful',
          category: LogCategory.auth,
          data: {
            'user_id': userData['id'],
            'user_name': userData['first_name'],
            'user_email': userData['email'],
            'user_type': userData['tipo_usuario'],
          },
        );

        // Log analytics
        await AnalyticsService.logLogin();

        // Atualiza Provider
        context.read<UserProvider>().setUserData(
              id: userData['id'],
              nome: userData['first_name'],
              email: userData['email'],
              tipoUsuario: userData['tipo_usuario'],
            );

        if (!mounted) return;
        Navigator.pushReplacementNamed(context, '/home');
      } else {
        AppLogger.warning(
          'Login failed - invalid credentials',
          category: LogCategory.auth,
          data: {
            'email': _emailController.text.trim(),
          },
        );

        setState(() {
          _erro = loginResult?['error'] ?? 'Credenciais inválidas';
        });
      }
    } catch (e) {
      if (!mounted) return;

      AppLogger.error(
        'Login error',
        category: LogCategory.auth,
        error: e,
        data: {
          'email': _emailController.text.trim(),
        },
      );

      setState(() {
        _carregando = false;
        _erro = 'Erro ao fazer login: ${e.toString()}';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D1117),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Logo
                Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(20),
                    color: const Color(0xFF6366F1),
                  ),
                  child: const Icon(
                    Icons.event,
                    size: 50,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 24),

                // Título
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
                  'Entre na sua conta',
                  style: TextStyle(
                    fontSize: 16,
                    color: Color(0xFFB0B3B8),
                  ),
                ),
                const SizedBox(height: 48),

                // Campo Email
                TextFormField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(
                    labelText: 'E-mail',
                    prefixIcon: Icon(Icons.email_outlined),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Digite seu e-mail';
                    }
                    if (!value.contains('@')) {
                      return 'E-mail inválido';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // Campo Senha
                TextFormField(
                  controller: _senhaController,
                  obscureText: _obscurePassword,
                  decoration: InputDecoration(
                    labelText: 'Senha',
                    prefixIcon: const Icon(Icons.lock_outlined),
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscurePassword
                            ? Icons.visibility
                            : Icons.visibility_off,
                      ),
                      onPressed: () {
                        setState(() {
                          _obscurePassword = !_obscurePassword;
                        });
                      },
                    ),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Digite sua senha';
                    }
                    if (value.length < 6) {
                      return 'Senha deve ter pelo menos 6 caracteres';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 24),

                // Botão Login
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: _carregando ? null : _fazerLogin,
                    child: _carregando
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text('Entrar'),
                  ),
                ),
                const SizedBox(height: 16),

                // Erro
                if (_erro != null)
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.red.withOpacity(0.3)),
                    ),
                    child: Text(
                      _erro!,
                      style: const TextStyle(color: Colors.red),
                      textAlign: TextAlign.center,
                    ),
                  ),

                const SizedBox(height: 24),

                // Links
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    TextButton(
                      onPressed: () {
                        Navigator.pushNamed(context, '/recuperar-senha');
                      },
                      child: const Text('Esqueci minha senha'),
                    ),
                    TextButton(
                      onPressed: () {
                        Navigator.pushNamed(context, '/pre-cadastro');
                      },
                      child: const Text('Criar conta'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
