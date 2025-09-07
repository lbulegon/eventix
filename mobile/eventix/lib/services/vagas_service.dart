// mobile/eventix/lib/services/vagas_service.dart
import 'package:dio/dio.dart';
import '../utils/app_config.dart';
import '../utils/app_logger.dart';
import 'auth_service.dart';

class VagasService {
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

  /// Lista vagas disponíveis
  static Future<List<Map<String, dynamic>>> getVagas({
    int? eventoId,
    int? funcaoId,
    String? cidade,
    String? search,
    int page = 1,
  }) async {
    try {
      AppLogger.info('Fetching vagas', category: LogCategory.api, data: {
        'evento_id': eventoId,
        'funcao_id': funcaoId,
        'cidade': cidade,
        'search': search,
        'page': page,
      });

      final queryParams = <String, dynamic>{
        'page': page,
      };

      if (eventoId != null) queryParams['evento_id'] = eventoId;
      if (funcaoId != null) queryParams['funcao_id'] = funcaoId;
      if (cidade != null && cidade.isNotEmpty) queryParams['cidade'] = cidade;
      if (search != null && search.isNotEmpty) queryParams['search'] = search;

      final response = await _dio.get(
        AppConfig.vagasDisponiveis,
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        final data = response.data;
        final vagas = List<Map<String, dynamic>>.from(data['results'] ?? []);

        AppLogger.info('Vagas fetched successfully',
            category: LogCategory.api,
            data: {
              'count': vagas.length,
              'total': data['count'],
            });

        return vagas;
      }
    } catch (e) {
      AppLogger.error('Failed to fetch vagas',
          category: LogCategory.api, error: e);
    }

    return [];
  }

  /// Candidata-se a uma vaga
  static Future<Map<String, dynamic>> candidatarVaga(int vagaId) async {
    try {
      AppLogger.info('Candidating to vaga',
          category: LogCategory.api, data: {'vaga_id': vagaId});

      final response = await _dio.post(
        AppConfig.candidaturas,
        data: {'vaga_id': vagaId},
      );

      if (response.statusCode == 201) {
        AppLogger.info('Successfully candidated to vaga',
            category: LogCategory.api, data: {'vaga_id': vagaId});
        return {
          'success': true,
          'message': 'Candidatura realizada com sucesso!',
          'data': response.data,
        };
      }
    } catch (e) {
      AppLogger.error('Failed to candidate to vaga',
          category: LogCategory.api, error: e, data: {'vaga_id': vagaId});

      if (e is DioException) {
        final response = e.response;
        if (response?.statusCode == 400) {
          final data = response?.data;
          if (data is Map<String, dynamic>) {
            return {
              'success': false,
              'error': data['error'] ?? 'Erro na candidatura',
            };
          }
        } else if (response?.statusCode == 403) {
          return {
            'success': false,
            'error': 'Você não tem permissão para se candidatar',
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

  /// Lista candidaturas do usuário
  static Future<List<Map<String, dynamic>>> getMinhasCandidaturas() async {
    try {
      AppLogger.info('Fetching user candidaturas', category: LogCategory.api);

      final response = await _dio.get(AppConfig.candidaturas);

      if (response.statusCode == 200) {
        final data = response.data;
        final candidaturas =
            List<Map<String, dynamic>>.from(data['results'] ?? []);

        AppLogger.info('Candidaturas fetched successfully',
            category: LogCategory.api,
            data: {
              'count': candidaturas.length,
            });

        return candidaturas;
      }
    } catch (e) {
      AppLogger.error('Failed to fetch candidaturas',
          category: LogCategory.api, error: e);
    }

    return [];
  }

  /// Cancela uma candidatura
  static Future<Map<String, dynamic>> cancelarCandidatura(
      int candidaturaId) async {
    try {
      AppLogger.info('Canceling candidatura',
          category: LogCategory.api, data: {'candidatura_id': candidaturaId});

      final response = await _dio.post(
        '${AppConfig.cancelarCandidatura}$candidaturaId/cancelar/',
      );

      if (response.statusCode == 200) {
        AppLogger.info('Candidatura canceled successfully',
            category: LogCategory.api, data: {'candidatura_id': candidaturaId});
        return {
          'success': true,
          'message': 'Candidatura cancelada com sucesso!',
        };
      }
    } catch (e) {
      AppLogger.error('Failed to cancel candidatura',
          category: LogCategory.api,
          error: e,
          data: {'candidatura_id': candidaturaId});

      if (e is DioException) {
        final response = e.response;
        if (response?.statusCode == 403) {
          return {
            'success': false,
            'error': 'Você não tem permissão para cancelar esta candidatura',
          };
        } else if (response?.statusCode == 404) {
          return {
            'success': false,
            'error': 'Candidatura não encontrada',
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

  /// Aprova uma candidatura (apenas empresas)
  static Future<Map<String, dynamic>> aprovarCandidatura(
      int candidaturaId) async {
    try {
      AppLogger.info('Approving candidatura',
          category: LogCategory.api, data: {'candidatura_id': candidaturaId});

      final response = await _dio.post(
        '${AppConfig.aprovarCandidatura}$candidaturaId/aprovar/',
      );

      if (response.statusCode == 200) {
        AppLogger.info('Candidatura approved successfully',
            category: LogCategory.api, data: {'candidatura_id': candidaturaId});
        return {
          'success': true,
          'message': 'Candidatura aprovada com sucesso!',
        };
      }
    } catch (e) {
      AppLogger.error('Failed to approve candidatura',
          category: LogCategory.api,
          error: e,
          data: {'candidatura_id': candidaturaId});

      if (e is DioException) {
        final response = e.response;
        if (response?.statusCode == 403) {
          return {
            'success': false,
            'error': 'Apenas empresas podem aprovar candidaturas',
          };
        } else if (response?.statusCode == 404) {
          return {
            'success': false,
            'error': 'Candidatura não encontrada',
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

  /// Rejeita uma candidatura (apenas empresas)
  static Future<Map<String, dynamic>> rejeitarCandidatura(
      int candidaturaId) async {
    try {
      AppLogger.info('Rejecting candidatura',
          category: LogCategory.api, data: {'candidatura_id': candidaturaId});

      final response = await _dio.post(
        '${AppConfig.rejeitarCandidatura}$candidaturaId/rejeitar/',
      );

      if (response.statusCode == 200) {
        AppLogger.info('Candidatura rejected successfully',
            category: LogCategory.api, data: {'candidatura_id': candidaturaId});
        return {
          'success': true,
          'message': 'Candidatura rejeitada',
        };
      }
    } catch (e) {
      AppLogger.error('Failed to reject candidatura',
          category: LogCategory.api,
          error: e,
          data: {'candidatura_id': candidaturaId});

      if (e is DioException) {
        final response = e.response;
        if (response?.statusCode == 403) {
          return {
            'success': false,
            'error': 'Apenas empresas podem rejeitar candidaturas',
          };
        } else if (response?.statusCode == 404) {
          return {
            'success': false,
            'error': 'Candidatura não encontrada',
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
