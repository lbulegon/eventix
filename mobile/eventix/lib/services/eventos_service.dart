// mobile/eventix/lib/services/eventos_service.dart
import 'package:dio/dio.dart';
import '../utils/app_config.dart';
import '../utils/app_logger.dart';
import 'auth_service.dart';

class EventosService {
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

  /// Lista eventos disponíveis
  static Future<List<Map<String, dynamic>>> getEventos() async {
    try {
      AppLogger.info('Fetching eventos', category: LogCategory.api);

      final response = await _dio.get(AppConfig.eventos);

      if (response.statusCode == 200) {
        final data = response.data;
        final eventos = List<Map<String, dynamic>>.from(data['results'] ?? []);

        AppLogger.info('Eventos fetched successfully',
            category: LogCategory.api,
            data: {
              'count': eventos.length,
            });

        return eventos;
      }
    } catch (e) {
      AppLogger.error('Failed to fetch eventos',
          category: LogCategory.api, error: e);
    }

    return [];
  }

  /// Lista eventos da empresa do usuário
  static Future<List<Map<String, dynamic>>> getMeusEventos() async {
    try {
      AppLogger.info('Fetching user eventos', category: LogCategory.api);

      final response = await _dio.get(AppConfig.meusEventos);

      if (response.statusCode == 200) {
        final eventos = List<Map<String, dynamic>>.from(response.data);

        AppLogger.info('User eventos fetched successfully',
            category: LogCategory.api,
            data: {
              'count': eventos.length,
            });

        return eventos;
      }
    } catch (e) {
      AppLogger.error('Failed to fetch user eventos',
          category: LogCategory.api, error: e);
    }

    return [];
  }

  /// Cria um novo evento
  static Future<Map<String, dynamic>> criarEvento({
    required String nome,
    required String descricao,
    required String dataInicio,
    required String dataFim,
    required int localId,
    required int empresaContratanteRecursosId,
  }) async {
    try {
      AppLogger.info('Creating evento', category: LogCategory.api, data: {
        'nome': nome,
        'local_id': localId,
        'empresa_contratante_recursos_id': empresaContratanteRecursosId,
      });

      final response = await _dio.post(
        AppConfig.criarEvento,
        data: {
          'nome': nome,
          'descricao': descricao,
          'data_inicio': dataInicio,
          'data_fim': dataFim,
          'local_id': localId,
          'empresa_contratante_recursos_id': empresaContratanteRecursosId,
        },
      );

      if (response.statusCode == 201) {
        AppLogger.info('Evento created successfully',
            category: LogCategory.api,
            data: {
              'evento_id': response.data['id'],
            });

        return {
          'success': true,
          'message': 'Evento criado com sucesso!',
          'data': response.data,
        };
      }
    } catch (e) {
      AppLogger.error('Failed to create evento',
          category: LogCategory.api, error: e, data: {'nome': nome});

      if (e is DioException) {
        final response = e.response;
        if (response?.statusCode == 400) {
          final data = response?.data;
          if (data is Map<String, dynamic>) {
            // Extrair mensagens de erro específicas
            final errors = <String>[];
            data.forEach((key, value) {
              if (value is List) {
                errors.addAll(value.map((e) => e.toString()));
              } else {
                errors.add(value.toString());
              }
            });

            return {
              'success': false,
              'error': errors.join(', '),
            };
          }
        } else if (response?.statusCode == 403) {
          return {
            'success': false,
            'error': 'Apenas empresas podem criar eventos',
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

  /// Atualiza um evento
  static Future<Map<String, dynamic>> atualizarEvento({
    required int eventoId,
    String? nome,
    String? descricao,
    String? dataInicio,
    String? dataFim,
    int? localId,
    bool? ativo,
  }) async {
    try {
      AppLogger.info('Updating evento',
          category: LogCategory.api, data: {'evento_id': eventoId});

      final data = <String, dynamic>{};
      if (nome != null) data['nome'] = nome;
      if (descricao != null) data['descricao'] = descricao;
      if (dataInicio != null) data['data_inicio'] = dataInicio;
      if (dataFim != null) data['data_fim'] = dataFim;
      if (localId != null) data['local_id'] = localId;
      if (ativo != null) data['ativo'] = ativo;

      final response = await _dio.put(
        '${AppConfig.criarEvento}$eventoId/',
        data: data,
      );

      if (response.statusCode == 200) {
        AppLogger.info('Evento updated successfully',
            category: LogCategory.api, data: {'evento_id': eventoId});

        return {
          'success': true,
          'message': 'Evento atualizado com sucesso!',
          'data': response.data,
        };
      }
    } catch (e) {
      AppLogger.error('Failed to update evento',
          category: LogCategory.api, error: e, data: {'evento_id': eventoId});

      if (e is DioException) {
        final response = e.response;
        if (response?.statusCode == 400) {
          final data = response?.data;
          if (data is Map<String, dynamic>) {
            final errors = <String>[];
            data.forEach((key, value) {
              if (value is List) {
                errors.addAll(value.map((e) => e.toString()));
              } else {
                errors.add(value.toString());
              }
            });

            return {
              'success': false,
              'error': errors.join(', '),
            };
          }
        } else if (response?.statusCode == 403) {
          return {
            'success': false,
            'error': 'Você não tem permissão para editar este evento',
          };
        } else if (response?.statusCode == 404) {
          return {
            'success': false,
            'error': 'Evento não encontrado',
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

  /// Deleta um evento
  static Future<Map<String, dynamic>> deletarEvento(int eventoId) async {
    try {
      AppLogger.info('Deleting evento',
          category: LogCategory.api, data: {'evento_id': eventoId});

      final response = await _dio.delete('${AppConfig.criarEvento}$eventoId/');

      if (response.statusCode == 204) {
        AppLogger.info('Evento deleted successfully',
            category: LogCategory.api, data: {'evento_id': eventoId});

        return {
          'success': true,
          'message': 'Evento deletado com sucesso!',
        };
      }
    } catch (e) {
      AppLogger.error('Failed to delete evento',
          category: LogCategory.api, error: e, data: {'evento_id': eventoId});

      if (e is DioException) {
        final response = e.response;
        if (response?.statusCode == 403) {
          return {
            'success': false,
            'error': 'Você não tem permissão para deletar este evento',
          };
        } else if (response?.statusCode == 404) {
          return {
            'success': false,
            'error': 'Evento não encontrado',
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
