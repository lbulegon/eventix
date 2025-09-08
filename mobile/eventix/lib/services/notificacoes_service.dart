// mobile/eventix/lib/services/notificacoes_service.dart
import 'package:dio/dio.dart';
import '../utils/app_config.dart';
import '../utils/app_logger.dart';
import 'auth_service.dart';

class NotificacoesService {
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

  /// Lista notificações do usuário
  static Future<List<Map<String, dynamic>>> getNotificacoes({
    int page = 1,
    bool? naoLidas,
  }) async {
    try {
      AppLogger.info('Fetching notifications',
          category: LogCategory.api,
          data: {
            'page': page,
            'nao_lidas': naoLidas,
          });

      final queryParams = <String, dynamic>{
        'page': page,
      };

      if (naoLidas != null) queryParams['nao_lidas'] = naoLidas;

      final response = await _dio.get(
        AppConfig.notificacoes,
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        final data = response.data;
        final notificacoes =
            List<Map<String, dynamic>>.from(data['results'] ?? []);

        AppLogger.info('Notifications fetched successfully',
            category: LogCategory.api,
            data: {
              'count': notificacoes.length,
              'total': data['count'],
            });

        return notificacoes;
      }
    } catch (e) {
      AppLogger.error('Failed to fetch notifications',
          category: LogCategory.api, error: e);
    }

    return [];
  }

  /// Marca uma notificação como lida
  static Future<Map<String, dynamic>> marcarComoLida(int notificacaoId) async {
    try {
      AppLogger.info('Marking notification as read',
          category: LogCategory.api, data: {'notificacao_id': notificacaoId});

      final response = await _dio.post(
        '${AppConfig.marcarNotificacaoLida}$notificacaoId/marcar_lida/',
      );

      if (response.statusCode == 200) {
        AppLogger.info('Notification marked as read successfully',
            category: LogCategory.api, data: {'notificacao_id': notificacaoId});
        return {
          'success': true,
          'message': 'Notificação marcada como lida',
        };
      }
    } catch (e) {
      AppLogger.error('Failed to mark notification as read',
          category: LogCategory.api,
          error: e,
          data: {'notificacao_id': notificacaoId});

      if (e is DioException) {
        final response = e.response;
        if (response?.statusCode == 404) {
          return {
            'success': false,
            'error': 'Notificação não encontrada',
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

  /// Marca todas as notificações como lidas
  static Future<Map<String, dynamic>> marcarTodasComoLidas() async {
    try {
      AppLogger.info('Marking all notifications as read',
          category: LogCategory.api);

      final response = await _dio.post(
        '${AppConfig.notificacoes}marcar_todas_lidas/',
      );

      if (response.statusCode == 200) {
        AppLogger.info('All notifications marked as read successfully',
            category: LogCategory.api);
        return {
          'success': true,
          'message': 'Todas as notificações foram marcadas como lidas',
        };
      }
    } catch (e) {
      AppLogger.error('Failed to mark all notifications as read',
          category: LogCategory.api, error: e);

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

  /// Obtém contador de notificações não lidas
  static Future<int> getContadorNaoLidas() async {
    try {
      AppLogger.info('Fetching unread notifications count',
          category: LogCategory.api);

      final response = await _dio.get(
        '${AppConfig.notificacoes}contador_nao_lidas/',
      );

      if (response.statusCode == 200) {
        final data = response.data;
        final count = data['count'] ?? 0;

        AppLogger.info('Unread notifications count fetched successfully',
            category: LogCategory.api, data: {'count': count});

        return count;
      }
    } catch (e) {
      AppLogger.error('Failed to fetch unread notifications count',
          category: LogCategory.api, error: e);
    }

    return 0;
  }

  /// Deleta uma notificação
  static Future<Map<String, dynamic>> deletarNotificacao(
      int notificacaoId) async {
    try {
      AppLogger.info('Deleting notification',
          category: LogCategory.api, data: {'notificacao_id': notificacaoId});

      final response = await _dio.delete(
        '${AppConfig.notificacoes}$notificacaoId/',
      );

      if (response.statusCode == 204) {
        AppLogger.info('Notification deleted successfully',
            category: LogCategory.api, data: {'notificacao_id': notificacaoId});
        return {
          'success': true,
          'message': 'Notificação deletada',
        };
      }
    } catch (e) {
      AppLogger.error('Failed to delete notification',
          category: LogCategory.api,
          error: e,
          data: {'notificacao_id': notificacaoId});

      if (e is DioException) {
        final response = e.response;
        if (response?.statusCode == 404) {
          return {
            'success': false,
            'error': 'Notificação não encontrada',
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
