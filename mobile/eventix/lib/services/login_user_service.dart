// lib/services/login_user_service.dart
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:eventix/services/api_client.dart';
import 'package:eventix/utils/app_config.dart';

class LoginResult {
  final String accessToken;
  final String refreshToken;
  final String nome;
  final String email;
  final String telefone;
  final int userId;
  final String tipoUsuario;

  LoginResult({
    required this.accessToken,
    required this.refreshToken,
    required this.nome,
    required this.email,
    required this.telefone,
    required this.userId,
    required this.tipoUsuario,
  });
}

Future<LoginResult?> login(String email, String senha) async {
  try {
    print('🔑 Tentando login para: $email');
    print('🔑 URL: ${AppConfig.login}');

    final response = await ApiClient.dio.post(
      AppConfig.login,
      data: {
        "username": email,
        "password": senha,
      },
    );

    print('🔑 Resposta do login: ${response.data}');
    print('🔑 Status code: ${response.statusCode}');

    final data = response.data;
    final tokens = data['tokens'] is Map ? data['tokens'] as Map : const {};

    // Checar se as chaves existem
    if (tokens['access'] == null || tokens['refresh'] == null) {
      print('❌ ERRO: API não retornou tokens.');
      return null;
    }

    // Montar objeto
    final user = data['user'] ?? {};

    return LoginResult(
      accessToken: tokens['access'],
      refreshToken: tokens['refresh'],
      nome: user['first_name'] ?? user['nome'] ?? 'Usuário',
      email: user['email'] ?? email,
      telefone: user['telefone'] ?? '',
      userId: user['id'] ?? 0,
      tipoUsuario: user['tipo_usuario'] ?? 'freelancer',
    );
  } catch (e) {
    print('❌ ERRO no login: $e');
    if (e is DioException) {
      print('❌ DioException: ${e.response?.data}');
      print('❌ Status: ${e.response?.statusCode}');
    }
    return null;
  }
}
