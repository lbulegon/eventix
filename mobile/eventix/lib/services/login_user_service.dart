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
        "email": email,
        "password": senha,
      },
    );

    print('🔑 Resposta do login: ${response.data}');
    print('🔑 Status code: ${response.statusCode}');

    // Checar se as chaves existem
    if (response.data['access'] == null || response.data['refresh'] == null) {
      print('❌ ERRO: API não retornou tokens.');
      return null;
    }

    // Montar objeto
    final data = response.data;
    final user = data['user'] ?? {};

    return LoginResult(
      accessToken: data['access'],
      refreshToken: data['refresh'],
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
