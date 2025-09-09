// mobile/eventix/lib/services/auth_service.dart
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_config.dart';
import '../utils/app_logger.dart';

class AuthService {
  static final Dio _dio = Dio();
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const String _userDataKey = 'user_data';

  static String? _accessToken;
  static String? _refreshToken;
  static Map<String, dynamic>? _userData;

  /// Getter para a instância do Dio
  static Dio get dio => _dio;

  /// Inicializa o serviço de autenticação
  static Future<void> initialize() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _accessToken = prefs.getString(_accessTokenKey);
      _refreshToken = prefs.getString(_refreshTokenKey);
      final userDataString = prefs.getString(_userDataKey);

      print('🔧 [AUTH_SERVICE] Token carregado: ${_accessToken != null ? "SIM" : "NÃO"}');
      print('🔧 [AUTH_SERVICE] Refresh token carregado: ${_refreshToken != null ? "SIM" : "NÃO"}');
      print('🔧 [AUTH_SERVICE] Dados do usuário carregados: ${userDataString != null ? "SIM" : "NÃO"}');

      if (userDataString != null) {
        _userData = jsonDecode(userDataString);
      }

      // Configurar interceptor de autenticação
      _dio.interceptors.add(InterceptorsWrapper(
        onRequest: (options, handler) {
          if (_accessToken != null) {
            options.headers['Authorization'] = 'Bearer $_accessToken';
          }
          handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            // Token expirado, tentar renovar
            final refreshed = await _refreshAccessToken();
            if (refreshed) {
              // Repetir a requisição com o novo token
              final options = error.requestOptions;
              options.headers['Authorization'] = 'Bearer $_accessToken';
              final response = await _dio.fetch(options);
              handler.resolve(response);
              return;
            } else {
              // Falha ao renovar, fazer logout
              await logout();
            }
          }
          handler.next(error);
        },
      ));

      AppLogger.info('AuthService initialized', category: LogCategory.auth);
    } catch (e) {
      AppLogger.error('Failed to initialize AuthService',
          category: LogCategory.auth, error: e);
    }
  }

  /// Faz login do usuário
  static Future<Map<String, dynamic>?> login(
      String email, String password) async {
    try {
      AppLogger.info('Login attempt started',
          category: LogCategory.auth, data: {'email': email});

      print('🔐 [AUTH_SERVICE] URL do login: ${AppConfig.login}');
      print('📧 [AUTH_SERVICE] Email: $email');
      print('🔑 [AUTH_SERVICE] Password: ${password.length} caracteres');

      // Django pode esperar 'username' em vez de 'email'
      final loginData = {
        'username': email, // Tentar username primeiro
        'password': password,
      };

      print('📦 [AUTH_SERVICE] Dados do login: $loginData');

      final response = await _dio.post(
        AppConfig.login,
        data: loginData,
      );

      if (response.statusCode == 200) {
        final data = response.data;

        _accessToken = data['tokens']['access'];
        _refreshToken = data['tokens']['refresh'];
        _userData = data['user'];

        print('🔧 [AUTH_SERVICE] Token recebido: ${_accessToken != null ? "SIM" : "NÃO"}');
        print('🔧 [AUTH_SERVICE] Refresh token recebido: ${_refreshToken != null ? "SIM" : "NÃO"}');
        print('🔧 [AUTH_SERVICE] Dados do usuário recebidos: ${_userData != null ? "SIM" : "NÃO"}');

        // Salvar tokens e dados do usuário
        await _saveTokens();
        await _saveUserData();

        print('🔧 [AUTH_SERVICE] Tokens salvos com sucesso');

        AppLogger.info('Login successful', category: LogCategory.auth, data: {
          'user_id': _userData?['id'],
          'tipo_usuario': _userData?['tipo_usuario'],
        });

        return {
          'success': true,
          'user': _userData,
          'access_token': _accessToken,
          'refresh_token': _refreshToken,
        };
      }
    } catch (e) {
      AppLogger.error('Login failed',
          category: LogCategory.auth, error: e, data: {'email': email});

      if (e is DioException) {
        final response = e.response;
        final statusCode = response?.statusCode;

        print('🔴 [AUTH_SERVICE] Erro DioException');
        print('🔴 [AUTH_SERVICE] Status Code: $statusCode');
        print('🔴 [AUTH_SERVICE] Dados da resposta: ${response?.data}');
        print('🔴 [AUTH_SERVICE] Headers da resposta: ${response?.headers}');

        if (statusCode == 401) {
          return {'success': false, 'error': 'Credenciais inválidas'};
        } else if (statusCode == 400) {
          final data = response?.data;
          print('🔍 [AUTH_SERVICE] Dados do erro 400: $data');

          if (data is Map<String, dynamic>) {
            // Verificar se há mensagens específicas de erro
            if (data.containsKey('email')) {
              return {'success': false, 'error': 'Email: ${data['email']}'};
            } else if (data.containsKey('password')) {
              return {'success': false, 'error': 'Senha: ${data['password']}'};
            } else if (data.containsKey('non_field_errors')) {
              return {'success': false, 'error': data['non_field_errors']};
            } else {
              return {
                'success': false,
                'error': data['error'] ?? 'Erro no login'
              };
            }
          } else if (data is String) {
            return {'success': false, 'error': data};
          }
        }
      }

      return {'success': false, 'error': 'Erro de conexão. Tente novamente.'};
    }

    return {'success': false, 'error': 'Erro desconhecido'};
  }

  /// Faz logout do usuário
  static Future<void> logout() async {
    try {
      if (_accessToken != null) {
        await _dio.post(AppConfig.logout);
      }
    } catch (e) {
      AppLogger.warning('Logout request failed',
          category: LogCategory.auth, error: e);
    } finally {
      // Limpar dados locais independente do resultado da requisição
      _accessToken = null;
      _refreshToken = null;
      _userData = null;

      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_accessTokenKey);
      await prefs.remove(_refreshTokenKey);
      await prefs.remove(_userDataKey);

      AppLogger.info('User logged out', category: LogCategory.auth);
    }
  }

  /// Verifica se o usuário está logado
  static bool get isLoggedIn => _accessToken != null;

  /// Retorna o token de acesso
  static String? get accessToken => _accessToken;

  /// Retorna os dados do usuário
  static Map<String, dynamic>? get userData => _userData;

  /// Retorna o tipo de usuário
  static String? get userType => _userData?['tipo_usuario'];

  /// Verifica se é freelancer
  static bool get isFreelancer => userType == 'freelancer';

  /// Verifica se é empresa
  static bool get isEmpresa =>
      userType == 'admin_empresa' || userType == 'empresa_user';

  /// Renova o token de acesso
  static Future<bool> _refreshAccessToken() async {
    try {
      if (_refreshToken == null) return false;

      final response = await _dio.post(
        AppConfig.refreshToken,
        data: {'refresh': _refreshToken},
      );

      if (response.statusCode == 200) {
        final data = response.data;
        _accessToken = data['access'];
        await _saveTokens();

        AppLogger.info('Token refreshed successfully',
            category: LogCategory.auth);
        return true;
      }
    } catch (e) {
      AppLogger.error('Token refresh failed',
          category: LogCategory.auth, error: e);
    }

    return false;
  }

  /// Salva os tokens no armazenamento local
  static Future<void> _saveTokens() async {
    final prefs = await SharedPreferences.getInstance();
    if (_accessToken != null) {
      await prefs.setString(_accessTokenKey, _accessToken!);
    }
    if (_refreshToken != null) {
      await prefs.setString(_refreshTokenKey, _refreshToken!);
    }
  }

  /// Salva os dados do usuário no armazenamento local
  static Future<void> _saveUserData() async {
    if (_userData != null) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userDataKey, jsonEncode(_userData));
    }
  }

  /// Atualiza os dados do usuário
  static Future<void> updateUserData(Map<String, dynamic> newUserData) async {
    _userData = newUserData;
    await _saveUserData();
  }

  /// Verifica se o token é válido
  static Future<bool> verifyToken() async {
    try {
      if (_accessToken == null) return false;

      final response = await _dio.post(
        AppConfig.tokenVerify,
        data: {'token': _accessToken},
      );

      return response.statusCode == 200;
    } catch (e) {
      AppLogger.error('Token verification failed',
          category: LogCategory.auth, error: e);
      return false;
    }
  }

  /// Obtém o perfil do usuário
  static Future<Map<String, dynamic>?> getUserProfile() async {
    try {
      final response = await _dio.get(AppConfig.userProfile);

      if (response.statusCode == 200) {
        final userData = response.data;
        await updateUserData(userData);
        return userData;
      }
    } catch (e) {
      AppLogger.error('Failed to get user profile',
          category: LogCategory.auth, error: e);
    }

    return null;
  }
}
