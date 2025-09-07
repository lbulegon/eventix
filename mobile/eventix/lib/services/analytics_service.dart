// lib/services/analytics_service.dart
import 'package:firebase_analytics/firebase_analytics.dart';
import 'package:eventix/utils/app_logger.dart';

class AnalyticsService {
  static final FirebaseAnalytics _analytics = FirebaseAnalytics.instance;
  static bool _isInitialized = false;

  /// Inicializa o serviço de analytics
  static Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      await _analytics.setAnalyticsCollectionEnabled(true);
      _isInitialized = true;

      AppLogger.info(
        'Analytics service initialized',
        category: LogCategory.analytics,
      );
    } catch (e) {
      AppLogger.error(
        'Failed to initialize analytics service',
        category: LogCategory.analytics,
        error: e,
      );
    }
  }

  /// Define o ID do usuário
  static Future<void> setUserId(String userId) async {
    try {
      await _analytics.setUserId(id: userId);
      AppLogger.info(
        'Analytics user ID set',
        category: LogCategory.analytics,
        data: {'user_id': userId},
      );
    } catch (e) {
      AppLogger.error(
        'Failed to set analytics user ID',
        category: LogCategory.analytics,
        error: e,
      );
    }
  }

  /// Define propriedades do usuário
  static Future<void> setUserProperties({
    String? userType,
    String? userStatus,
    String? registrationDate,
  }) async {
    try {
      if (userType != null) {
        await _analytics.setUserProperty(name: 'user_type', value: userType);
      }
      if (userStatus != null) {
        await _analytics.setUserProperty(
            name: 'user_status', value: userStatus);
      }
      if (registrationDate != null) {
        await _analytics.setUserProperty(
            name: 'registration_date', value: registrationDate);
      }

      AppLogger.info(
        'Analytics user properties set',
        category: LogCategory.analytics,
        data: {
          'user_type': userType,
          'user_status': userStatus,
          'registration_date': registrationDate,
        },
      );
    } catch (e) {
      AppLogger.error(
        'Failed to set analytics user properties',
        category: LogCategory.analytics,
        error: e,
      );
    }
  }

  /// Log de evento personalizado
  static Future<void> logEvent(
    String eventName, {
    Map<String, Object>? parameters,
  }) async {
    try {
      await _analytics.logEvent(
        name: eventName,
        parameters: parameters,
      );

      AppLogger.info(
        'Analytics event logged',
        category: LogCategory.analytics,
        data: {
          'event_name': eventName,
          'parameters': parameters,
        },
      );
    } catch (e) {
      AppLogger.error(
        'Failed to log analytics event',
        category: LogCategory.analytics,
        error: e,
        data: {
          'event_name': eventName,
          'parameters': parameters,
        },
      );
    }
  }

  /// Eventos específicos do app
  static Future<void> logLogin({String? method}) async {
    await logEvent('login', parameters: {
      'method': method ?? 'email',
    });
  }

  static Future<void> logLogout() async {
    await logEvent('logout');
  }

  static Future<void> logSignUp({String? method}) async {
    await logEvent('sign_up', parameters: {
      'method': method ?? 'email',
    });
  }

  static Future<void> logScreenView(String screenName) async {
    await logEvent('screen_view', parameters: {
      'screen_name': screenName,
    });
  }

  static Future<void> logVagaView(String vagaId, String vagaTitle) async {
    await logEvent('vaga_view', parameters: {
      'vaga_id': vagaId,
      'vaga_title': vagaTitle,
    });
  }

  static Future<void> logCandidatura(String vagaId, String vagaTitle) async {
    await logEvent('candidatura', parameters: {
      'vaga_id': vagaId,
      'vaga_title': vagaTitle,
    });
  }

  static Future<void> logEventoView(String eventoId, String eventoTitle) async {
    await logEvent('evento_view', parameters: {
      'evento_id': eventoId,
      'evento_title': eventoTitle,
    });
  }

  static Future<void> logSearch(String query, String category) async {
    await logEvent('search', parameters: {
      'search_term': query,
      'category': category,
    });
  }

  static Future<void> logError(String errorType, String errorMessage) async {
    await logEvent('app_error', parameters: {
      'error_type': errorType,
      'error_message': errorMessage,
    });
  }

  static Future<void> logPerformance(String operation, int durationMs) async {
    await logEvent('performance', parameters: {
      'operation': operation,
      'duration_ms': durationMs,
    });
  }

  /// Métricas de negócio
  static Future<void> logBusinessMetric(String metric, double value) async {
    await logEvent('business_metric', parameters: {
      'metric_name': metric,
      'metric_value': value,
    });
  }

  static Future<void> logUserEngagement(String action, String context) async {
    await logEvent('user_engagement', parameters: {
      'action': action,
      'context': context,
    });
  }
}
