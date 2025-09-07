// lib/services/crash_service.dart
import 'package:flutter/foundation.dart';
import 'package:eventix/utils/app_logger.dart';

class CrashService {
  static bool _isInitialized = false;

  /// Inicializa o serviço de crash reporting (versão simplificada sem Firebase)
  static Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      // Captura erros do Flutter
      FlutterError.onError = (FlutterErrorDetails details) {
        AppLogger.fatal(
          'Flutter Error: ${details.exception}',
          category: LogCategory.crash,
          error: details.exception,
          stackTrace: details.stack,
        );
      };

      // Captura erros assíncronos
      PlatformDispatcher.instance.onError = (error, stack) {
        AppLogger.fatal(
          'Async Error: $error',
          category: LogCategory.crash,
          error: error,
          stackTrace: stack,
        );
        return true;
      };

      _isInitialized = true;

      AppLogger.info(
        'Crash service initialized (simplified version)',
        category: LogCategory.crash,
      );
    } catch (e) {
      AppLogger.error(
        'Failed to initialize crash service',
        category: LogCategory.crash,
        error: e,
      );
    }
  }

  /// Define o ID do usuário (versão simplificada)
  static Future<void> setUserId(String userId) async {
    try {
      AppLogger.info(
        'Crash user ID set (simplified)',
        category: LogCategory.crash,
        data: {'user_id': userId},
      );
    } catch (e) {
      AppLogger.error(
        'Failed to set crash user ID',
        category: LogCategory.crash,
        error: e,
      );
    }
  }

  /// Define dados customizados (versão simplificada)
  static Future<void> setCustomKey(String key, Object value) async {
    try {
      AppLogger.debug(
        'Crash custom key set (simplified)',
        category: LogCategory.crash,
        data: {'key': key, 'value': value},
      );
    } catch (e) {
      AppLogger.error(
        'Failed to set crash custom key',
        category: LogCategory.crash,
        error: e,
      );
    }
  }

  /// Define dados customizados em lote (versão simplificada)
  static Future<void> setCustomKeys(Map<String, Object> keys) async {
    try {
      AppLogger.debug(
        'Crash custom keys set (simplified)',
        category: LogCategory.crash,
        data: {'keys': keys},
      );
    } catch (e) {
      AppLogger.error(
        'Failed to set crash custom keys',
        category: LogCategory.crash,
        error: e,
      );
    }
  }

  /// Registra um erro não fatal (versão simplificada)
  static Future<void> recordError(
    dynamic exception,
    StackTrace? stackTrace, {
    String? reason,
    bool fatal = false,
    Map<String, dynamic>? information,
  }) async {
    try {
      AppLogger.error(
        'Crash error recorded (simplified)',
        category: LogCategory.crash,
        error: exception,
        stackTrace: stackTrace,
        data: {
          'reason': reason,
          'fatal': fatal,
          'information': information,
        },
      );
    } catch (e) {
      AppLogger.error(
        'Failed to record crash error',
        category: LogCategory.crash,
        error: e,
      );
    }
  }

  /// Registra um erro fatal (versão simplificada)
  static Future<void> recordFatalError(
    dynamic exception,
    StackTrace? stackTrace, {
    String? reason,
    Map<String, dynamic>? information,
  }) async {
    await recordError(
      exception,
      stackTrace,
      reason: reason,
      fatal: true,
      information: information,
    );
  }

  /// Registra um erro do Flutter (versão simplificada)
  static Future<void> recordFlutterError(
    FlutterErrorDetails details,
  ) async {
    try {
      AppLogger.fatal(
        'Flutter error recorded (simplified)',
        category: LogCategory.crash,
        error: details.exception,
        stackTrace: details.stack,
        data: {
          'library': details.library,
          'context': details.context?.toString(),
        },
      );
    } catch (e) {
      AppLogger.error(
        'Failed to record Flutter error',
        category: LogCategory.crash,
        error: e,
      );
    }
  }

  /// Registra um log (versão simplificada)
  static Future<void> log(String message) async {
    try {
      AppLogger.debug(
        'Crash log recorded (simplified)',
        category: LogCategory.crash,
        data: {'message': message},
      );
    } catch (e) {
      AppLogger.error(
        'Failed to record crash log',
        category: LogCategory.crash,
        error: e,
      );
    }
  }

  /// Verifica se o app foi aberto após um crash (versão simplificada)
  static Future<bool> didCrashOnPreviousExecution() async {
    try {
      AppLogger.info(
        'Crash check completed (simplified)',
        category: LogCategory.crash,
        data: {'did_crash': false},
      );
      return false; // Sempre retorna false na versão simplificada
    } catch (e) {
      AppLogger.error(
        'Failed to check crash status',
        category: LogCategory.crash,
        error: e,
      );
      return false;
    }
  }

  /// Força um crash para teste (apenas em debug)
  static void crash() {
    if (kDebugMode) {
      AppLogger.warning(
        'Crash test called (simplified version)',
        category: LogCategory.crash,
      );
      throw Exception('Test crash - simplified version');
    } else {
      AppLogger.warning(
        'Crash test called in production',
        category: LogCategory.crash,
      );
    }
  }

  /// Configura dados do usuário para crash reporting (versão simplificada)
  static Future<void> setUserData({
    String? userId,
    String? userType,
    String? userStatus,
    String? appVersion,
    String? deviceModel,
  }) async {
    try {
      if (userId != null) {
        await setUserId(userId);
      }

      final customKeys = <String, Object>{};
      if (userType != null) customKeys['user_type'] = userType;
      if (userStatus != null) customKeys['user_status'] = userStatus;
      if (appVersion != null) customKeys['app_version'] = appVersion;
      if (deviceModel != null) customKeys['device_model'] = deviceModel;

      if (customKeys.isNotEmpty) {
        await setCustomKeys(customKeys);
      }

      AppLogger.info(
        'Crash user data set (simplified)',
        category: LogCategory.crash,
        data: {
          'user_id': userId,
          'custom_keys': customKeys,
        },
      );
    } catch (e) {
      AppLogger.error(
        'Failed to set crash user data',
        category: LogCategory.crash,
        error: e,
      );
    }
  }
}
