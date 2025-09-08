// mobile/eventix/lib/services/funcoes_service.dart
import 'package:dio/dio.dart';
import '../utils/app_config.dart';
import '../utils/app_logger.dart';
import 'auth_service.dart';

class FuncoesService {
  static final Dio _dio = Dio();

  /// Inicializa o serviço
  static void initialize() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (AuthService.accessToken != null) {
          options.headers['Authorization'] =
              'Bearer ${AuthService.accessToken}';
        }
        handler.next(options);
      },
    ));
  }

  /// Lista todas as funções disponíveis
  static Future<List<Map<String, dynamic>>> getFuncoes() async {
    try {
      AppLogger.info('Fetching funcoes', category: LogCategory.api);

      final response = await _dio.get(AppConfig.funcoes);

      if (response.statusCode == 200) {
        final data = response.data;
        final funcoes = List<Map<String, dynamic>>.from(data['results'] ?? []);

        AppLogger.info('Funcoes fetched successfully',
            category: LogCategory.api,
            data: {
              'count': funcoes.length,
            });

        return funcoes;
      }
    } catch (e) {
      AppLogger.error('Failed to fetch funcoes',
          category: LogCategory.api, error: e);
    }

    return [];
  }

  /// Obtém as funções do freelancer logado
  static Future<List<Map<String, dynamic>>> getMinhasFuncoes() async {
    try {
      AppLogger.info('Fetching user funcoes', category: LogCategory.api);

      final response = await _dio
          .get('${AppConfig.apiUrl}/freelancers/funcoes/minhas_funcoes/');

      if (response.statusCode == 200) {
        final data = response.data;
        final funcoes = List<Map<String, dynamic>>.from(data);

        AppLogger.info('User funcoes fetched successfully',
            category: LogCategory.api,
            data: {
              'count': funcoes.length,
            });

        return funcoes;
      }
    } catch (e) {
      AppLogger.error('Failed to fetch user funcoes',
          category: LogCategory.api, error: e);
    }

    return [];
  }

  /// Adiciona uma função ao freelancer
  static Future<Map<String, dynamic>> adicionarFuncao(int funcaoId) async {
    try {
      AppLogger.info('Adding funcao',
          category: LogCategory.api, data: {'funcao_id': funcaoId});

      final response = await _dio.post(
        '${AppConfig.apiUrl}/freelancers/funcoes/adicionar_funcao/',
        data: {'funcao_id': funcaoId, 'nivel': 'iniciante'},
      );

      if (response.statusCode == 201) {
        AppLogger.info('Funcao added successfully',
            category: LogCategory.api, data: {'funcao_id': funcaoId});
        return {
          'success': true,
          'message': 'Função adicionada com sucesso!',
          'data': response.data,
        };
      }
    } catch (e) {
      AppLogger.error('Failed to add funcao',
          category: LogCategory.api, error: e, data: {'funcao_id': funcaoId});

      if (e is DioException) {
        final response = e.response;
        if (response?.statusCode == 400) {
          final data = response?.data;
          if (data is Map<String, dynamic>) {
            return {
              'success': false,
              'error': data['error'] ?? 'Erro ao adicionar função',
            };
          }
        } else if (response?.statusCode == 409) {
          return {
            'success': false,
            'error': 'Você já possui esta função',
          };
        }
      }

      return {
        'success': false,
        'error': 'Erro de conexão. Tente novamente.',
      };
    }

    return {
      'success': false,
      'error': 'Erro desconhecido',
    };
  }

  /// Remove uma função do freelancer
  static Future<Map<String, dynamic>> removerFuncao(
      int freelancerFuncaoId) async {
    try {
      AppLogger.info('Removing funcao',
          category: LogCategory.api,
          data: {'freelancer_funcao_id': freelancerFuncaoId});

      final response = await _dio.delete(
        '${AppConfig.apiUrl}/freelancers/funcoes/$freelancerFuncaoId/remover_funcao/',
      );

      if (response.statusCode == 200) {
        AppLogger.info('Funcao removed successfully',
            category: LogCategory.api,
            data: {'freelancer_funcao_id': freelancerFuncaoId});
        return {
          'success': true,
          'message': 'Função removida com sucesso!',
        };
      }
    } catch (e) {
      AppLogger.error('Failed to remove funcao',
          category: LogCategory.api,
          error: e,
          data: {'freelancer_funcao_id': freelancerFuncaoId});

      if (e is DioException) {
        final response = e.response;
        if (response?.statusCode == 404) {
          return {
            'success': false,
            'error': 'Função não encontrada',
          };
        }
      }

      return {
        'success': false,
        'error': 'Erro de conexão. Tente novamente.',
      };
    }

    return {
      'success': false,
      'error': 'Erro desconhecido',
    };
  }

  /// Atualiza o nível de uma função
  static Future<Map<String, dynamic>> atualizarNivelFuncao(
    int funcaoId,
    String nivel,
  ) async {
    try {
      AppLogger.info('Updating funcao level', category: LogCategory.api, data: {
        'funcao_id': funcaoId,
        'nivel': nivel,
      });

      final response = await _dio.patch(
        '${AppConfig.apiUrl}/freelancers/funcoes/$funcaoId/atualizar_nivel/',
        data: {'nivel': nivel},
      );

      if (response.statusCode == 200) {
        AppLogger.info('Funcao level updated successfully',
            category: LogCategory.api,
            data: {'freelancer_funcao_id': funcaoId});
        return {
          'success': true,
          'message': 'Nível da função atualizado!',
          'data': response.data,
        };
      }
    } catch (e) {
      AppLogger.error('Failed to update funcao level',
          category: LogCategory.api, error: e, data: {'funcao_id': funcaoId});

      if (e is DioException) {
        final response = e.response;
        if (response?.statusCode == 404) {
          return {
            'success': false,
            'error': 'Função não encontrada',
          };
        }
      }

      return {
        'success': false,
        'error': 'Erro de conexão. Tente novamente.',
      };
    }

    return {
      'success': false,
      'error': 'Erro desconhecido',
    };
  }
}
