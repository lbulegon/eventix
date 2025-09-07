// lib/services/crash_service.dart
import 'package:firebase_crashlytics/firebase_crashlytics.dart';
import 'package:flutter/foundation.dart';
import 'package:eventix/utils/app_logger.dart';

class CrashService {
  static final FirebaseCrashlytics _crashlytics = FirebaseCrashlytics.instance;
  static bool _isInitialized = false;

  /// Inicializa o serviço de crash reporting
  static Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      // Captura erros do Flutter
      FlutterError.onError = (FlutterErrorDetails details) {
        _crashlytics.recordFlutterFatalError(details);
      };

      // Captura erros assíncronos
      PlatformDispatcher.instance.onError = (error, stack) {
        _crashlytics.recordError(error, stack, fatal: true);
        return true;
      };

      _isInitialized = true;

      AppLogger.info(
        'Crash service initialized',
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

  /// Define o ID do usuário
  static Future<void> setUserId(String userId) async {
    try {
      await _crashlytics.setUserIdentifier(userId);
      AppLogger.info(
        'Crash user ID set',
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

  /// Define dados customizados
  static Future<void> setCustomKey(String key, Object value) async {
    try {
      await _crashlytics.setCustomKey(key, value);
      AppLogger.debug(
        'Crash custom key set',
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

  /// Define dados customizados em lote
  static Future<void> setCustomKeys(Map<String, Object> keys) async {
    try {
      for (final entry in keys.entries) {
        await _crashlytics.setCustomKey(entry.key, entry.value);
      }

      AppLogger.debug(
        'Crash custom keys set',
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

  /// Registra um erro não fatal
  static Future<void> recordError(
    dynamic exception,
    StackTrace? stackTrace, {
    String? reason,
    bool fatal = false,
    Map<String, dynamic>? information,
  }) async {
    try {
      await _crashlytics.recordError(
        exception,
        stackTrace,
        reason: reason,
        fatal: fatal,
        information:
            information?.entries.map((e) => '${e.key}: ${e.value}').toList() ??
                [],
      );

      AppLogger.error(
        'Crash error recorded',
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

  /// Registra um erro fatal
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

  /// Registra um erro do Flutter
  static Future<void> recordFlutterError(
    FlutterErrorDetails details,
  ) async {
    try {
      await _crashlytics.recordFlutterFatalError(details);

      AppLogger.fatal(
        'Flutter error recorded',
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

  /// Registra um log
  static Future<void> log(String message) async {
    try {
      await _crashlytics.log(message);

      AppLogger.debug(
        'Crash log recorded',
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

  /// Verifica se o app foi aberto após um crash
  static Future<bool> didCrashOnPreviousExecution() async {
    try {
      final didCrash = await _crashlytics.didCrashOnPreviousExecution();

      AppLogger.info(
        'Crash check completed',
        category: LogCategory.crash,
        data: {'did_crash': didCrash},
      );

      return didCrash;
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
      _crashlytics.crash();
    } else {
      AppLogger.warning(
        'Crash test called in production',
        category: LogCategory.crash,
      );
    }
  }

  /// Configura dados do usuário para crash reporting
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
        'Crash user data set',
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
