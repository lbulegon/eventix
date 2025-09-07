// lib/utils/app_logger.dart
import 'dart:developer' as developer;
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:logger/logger.dart';
import 'package:firebase_crashlytics/firebase_crashlytics.dart';
import 'package:firebase_analytics/firebase_analytics.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

enum LogLevel {
  debug,
  info,
  warning,
  error,
  fatal,
}

enum LogCategory {
  auth,
  api,
  ui,
  navigation,
  storage,
  network,
  performance,
  crash,
  analytics,
  business,
}

class AppLogger {
  static final Logger _logger = Logger(
    printer: PrettyPrinter(
      methodCount: 2,
      errorMethodCount: 8,
      lineLength: 120,
      colors: true,
      printEmojis: true,
      dateTimeFormat: DateTimeFormat.onlyTimeAndSinceStart,
    ),
  );

  static bool _isInitialized = false;
  static String? _userId;
  static String? _sessionId;
  static Map<String, dynamic> _deviceInfo = {};
  static Map<String, dynamic> _appInfo = {};

  /// Inicializa o sistema de logging
  static Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      // Coleta informações do dispositivo
      await _collectDeviceInfo();

      // Coleta informações do app
      await _collectAppInfo();

      // Gera ID da sessão
      _sessionId = DateTime.now().millisecondsSinceEpoch.toString();

      _isInitialized = true;

      info(
        'AppLogger initialized',
        category: LogCategory.analytics,
        data: {
          'session_id': _sessionId,
          'device_info': _deviceInfo,
          'app_info': _appInfo,
        },
      );
    } catch (e) {
      developer.log('Failed to initialize AppLogger: $e', name: 'AppLogger');
    }
  }

  /// Coleta informações do dispositivo
  static Future<void> _collectDeviceInfo() async {
    try {
      final deviceInfo = DeviceInfoPlugin();

      if (Platform.isAndroid) {
        final androidInfo = await deviceInfo.androidInfo;
        _deviceInfo = {
          'platform': 'android',
          'model': androidInfo.model,
          'brand': androidInfo.brand,
          'version': androidInfo.version.release,
          'sdk_int': androidInfo.version.sdkInt,
          'manufacturer': androidInfo.manufacturer,
        };
      } else if (Platform.isIOS) {
        final iosInfo = await deviceInfo.iosInfo;
        _deviceInfo = {
          'platform': 'ios',
          'model': iosInfo.model,
          'name': iosInfo.name,
          'system_name': iosInfo.systemName,
          'system_version': iosInfo.systemVersion,
          'identifier_for_vendor': iosInfo.identifierForVendor,
        };
      }
    } catch (e) {
      _deviceInfo = {'error': e.toString()};
    }
  }

  /// Coleta informações do app
  static Future<void> _collectAppInfo() async {
    try {
      final packageInfo = await PackageInfo.fromPlatform();
      _appInfo = {
        'app_name': packageInfo.appName,
        'package_name': packageInfo.packageName,
        'version': packageInfo.version,
        'build_number': packageInfo.buildNumber,
      };
    } catch (e) {
      _appInfo = {'error': e.toString()};
    }
  }

  /// Define o ID do usuário para logs
  static void setUserId(String userId) {
    _userId = userId;
    FirebaseCrashlytics.instance.setUserIdentifier(userId);
  }

  /// Log de debug
  static void debug(
    String message, {
    LogCategory category = LogCategory.analytics,
    Map<String, dynamic>? data,
    Object? error,
    StackTrace? stackTrace,
  }) {
    _log(LogLevel.debug, message, category, data, error, stackTrace);
  }

  /// Log de informação
  static void info(
    String message, {
    LogCategory category = LogCategory.analytics,
    Map<String, dynamic>? data,
    Object? error,
    StackTrace? stackTrace,
  }) {
    _log(LogLevel.info, message, category, data, error, stackTrace);
  }

  /// Log de warning
  static void warning(
    String message, {
    LogCategory category = LogCategory.analytics,
    Map<String, dynamic>? data,
    Object? error,
    StackTrace? stackTrace,
  }) {
    _log(LogLevel.warning, message, category, data, error, stackTrace);
  }

  /// Log de erro
  static void error(
    String message, {
    LogCategory category = LogCategory.analytics,
    Map<String, dynamic>? data,
    Object? error,
    StackTrace? stackTrace,
  }) {
    _log(LogLevel.error, message, category, data, error, stackTrace);
  }

  /// Log fatal
  static void fatal(
    String message, {
    LogCategory category = LogCategory.crash,
    Map<String, dynamic>? data,
    Object? error,
    StackTrace? stackTrace,
  }) {
    _log(LogLevel.fatal, message, category, data, error, stackTrace);
  }

  /// Método principal de logging
  static void _log(
    LogLevel level,
    String message,
    LogCategory category,
    Map<String, dynamic>? data,
    Object? error,
    StackTrace? stackTrace,
  ) {
    final timestamp = DateTime.now().toIso8601String();
    final logData = {
      'timestamp': timestamp,
      'level': level.name,
      'category': category.name,
      'message': message,
      'user_id': _userId,
      'session_id': _sessionId,
      'data': data,
      'device_info': _deviceInfo,
      'app_info': _appInfo,
    };

    // Log no console (desenvolvimento)
    if (kDebugMode) {
      _logger.log(_getLogLevel(level), message,
          error: error, stackTrace: stackTrace);
    }

    // Log no developer console
    developer.log(
      message,
      name: 'Eventix.${category.name}',
      error: error,
      stackTrace: stackTrace,
    );

    // Log no Firebase Crashlytics (produção)
    if (level == LogLevel.error || level == LogLevel.fatal) {
      FirebaseCrashlytics.instance.recordError(
        error ?? message,
        stackTrace,
        reason: message,
        information: [logData],
      );
    }

    // Log customizado no Firebase Analytics
    if (level == LogLevel.info && category == LogCategory.analytics) {
      FirebaseAnalytics.instance.logEvent(
        name: 'app_log',
        parameters: {
          'category': category.name,
          'message': message,
          'user_id': _userId ?? 'anonymous',
        },
      );
    }
  }

  /// Converte LogLevel para Level do logger
  static Level _getLogLevel(LogLevel level) {
    switch (level) {
      case LogLevel.debug:
        return Level.debug;
      case LogLevel.info:
        return Level.info;
      case LogLevel.warning:
        return Level.warning;
      case LogLevel.error:
        return Level.error;
      case LogLevel.fatal:
        return Level.fatal;
    }
  }

  /// Log de performance
  static void logPerformance(
    String operation,
    Duration duration, {
    Map<String, dynamic>? additionalData,
  }) {
    _log(
      LogLevel.info,
      'Performance: $operation took ${duration.inMilliseconds}ms',
      LogCategory.performance,
      {
        'operation': operation,
        'duration_ms': duration.inMilliseconds,
        'duration_seconds': duration.inSeconds,
        ...?additionalData,
      },
      null,
      null,
    );
  }

  /// Log de navegação
  static void logNavigation(
    String from,
    String to, {
    Map<String, dynamic>? parameters,
  }) {
    _log(
      LogLevel.info,
      'Navigation: $from -> $to',
      LogCategory.navigation,
      {
        'from': from,
        'to': to,
        'parameters': parameters,
      },
      null,
      null,
    );
  }

  /// Log de API
  static void logApi(
    String method,
    String url,
    int statusCode, {
    Map<String, dynamic>? requestData,
    Map<String, dynamic>? responseData,
    Duration? duration,
  }) {
    final level = statusCode >= 400 ? LogLevel.error : LogLevel.info;

    _log(
      level,
      'API: $method $url - $statusCode',
      LogCategory.api,
      {
        'method': method,
        'url': url,
        'status_code': statusCode,
        'request_data': requestData,
        'response_data': responseData,
        'duration_ms': duration?.inMilliseconds,
      },
      null,
      null,
    );
  }

  /// Log de autenticação
  static void logAuth(
    String action, {
    bool success = true,
    String? error,
    Map<String, dynamic>? data,
  }) {
    final level = success ? LogLevel.info : LogLevel.error;

    _log(
      level,
      'Auth: $action ${success ? 'success' : 'failed'}',
      LogCategory.auth,
      {
        'action': action,
        'success': success,
        'error': error,
        ...?data,
      },
      null,
      null,
    );
  }

  /// Log de negócio
  static void logBusiness(
    String event,
    Map<String, dynamic> data,
  ) {
    info(
      'Business: $event',
      category: LogCategory.business,
      data: data,
    );
  }
}
