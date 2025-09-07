// lib/utils/app_logger.dart
import 'dart:developer' as developer;
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:logger/logger.dart';
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
      // Gera um ID de sessão único
      _sessionId = DateTime.now().millisecondsSinceEpoch.toString();

      // Coleta informações do dispositivo
      await _collectDeviceInfo();

      // Coleta informações do app
      await _collectAppInfo();

      _isInitialized = true;

      // Log inicial
      _logger.i('🚀 AppLogger initialized successfully');
    } catch (e) {
      _logger.e('❌ Failed to initialize AppLogger: $e');
    }
  }

  /// Coleta informações do dispositivo
  static Future<void> _collectDeviceInfo() async {
    try {
      final deviceInfo = DeviceInfoPlugin();

      if (Platform.isAndroid) {
        final androidInfo = await deviceInfo.androidInfo;
        _deviceInfo = {
          'platform': 'Android',
          'model': androidInfo.model,
          'brand': androidInfo.brand,
          'version': androidInfo.version.release,
          'sdk': androidInfo.version.sdkInt,
        };
      } else if (Platform.isIOS) {
        final iosInfo = await deviceInfo.iosInfo;
        _deviceInfo = {
          'platform': 'iOS',
          'model': iosInfo.model,
          'name': iosInfo.name,
          'version': iosInfo.systemVersion,
        };
      }
    } catch (e) {
      _logger.w('⚠️ Failed to collect device info: $e');
    }
  }

  /// Coleta informações do app
  static Future<void> _collectAppInfo() async {
    try {
      final packageInfo = await PackageInfo.fromPlatform();
      _appInfo = {
        'name': packageInfo.appName,
        'version': packageInfo.version,
        'build': packageInfo.buildNumber,
        'package': packageInfo.packageName,
      };
    } catch (e) {
      _logger.w('⚠️ Failed to collect app info: $e');
    }
  }

  /// Define o ID do usuário
  static void setUserId(String userId) {
    _userId = userId;
  }

  /// Log de debug
  static void debug(
    String message, {
    LogCategory category = LogCategory.business,
    Map<String, dynamic>? data,
    dynamic error,
    StackTrace? stackTrace,
  }) {
    _log(LogLevel.debug, message, category, data, error, stackTrace);
  }

  /// Log de informação
  static void info(
    String message, {
    LogCategory category = LogCategory.business,
    Map<String, dynamic>? data,
    dynamic error,
    StackTrace? stackTrace,
  }) {
    _log(LogLevel.info, message, category, data, error, stackTrace);
  }

  /// Log de aviso
  static void warning(
    String message, {
    LogCategory category = LogCategory.business,
    Map<String, dynamic>? data,
    dynamic error,
    StackTrace? stackTrace,
  }) {
    _log(LogLevel.warning, message, category, data, error, stackTrace);
  }

  /// Log de erro
  static void error(
    String message, {
    LogCategory category = LogCategory.business,
    Map<String, dynamic>? data,
    dynamic error,
    StackTrace? stackTrace,
  }) {
    _log(LogLevel.error, message, category, data, error, stackTrace);
  }

  /// Log fatal
  static void fatal(
    String message, {
    LogCategory category = LogCategory.business,
    Map<String, dynamic>? data,
    dynamic error,
    StackTrace? stackTrace,
  }) {
    _log(LogLevel.fatal, message, category, data, error, stackTrace);
  }

  /// Método interno de logging
  static void _log(
    LogLevel level,
    String message,
    LogCategory category,
    Map<String, dynamic>? data,
    dynamic error,
    StackTrace? stackTrace,
  ) {
    if (!_isInitialized) {
      print('⚠️ AppLogger not initialized. Message: $message');
      return;
    }

    // Prepara dados do log
    final logData = <String, dynamic>{
      'message': message,
      'category': category.name,
      'level': level.name,
      'timestamp': DateTime.now().toIso8601String(),
      'session_id': _sessionId,
      'user_id': _userId,
      'device_info': _deviceInfo,
      'app_info': _appInfo,
      if (data != null) ...data,
    };

    // Log no console usando o logger
    final logLevel = _getLogLevel(level);
    _logger.log(
      logLevel,
      message,
      error: error,
      stackTrace: stackTrace,
    );

    // Log no developer console
    developer.log(
      message,
      name: 'Eventix.${category.name}',
      error: error,
      stackTrace: stackTrace,
    );

    // Firebase removido - usando apenas logs locais
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
    info(
      'Performance: $operation took ${duration.inMilliseconds}ms',
      category: LogCategory.performance,
      data: {
        'operation': operation,
        'duration_ms': duration.inMilliseconds,
        ...?additionalData,
      },
    );
  }

  /// Log de API
  static void logApiCall(
    String method,
    String url,
    int? statusCode,
    Duration? duration, {
    Map<String, dynamic>? requestData,
    Map<String, dynamic>? responseData,
    String? error,
  }) {
    final level = statusCode != null && statusCode >= 400
        ? LogLevel.error
        : LogLevel.info;

    _log(
      level,
      'API Call: $method $url',
      LogCategory.api,
      {
        'method': method,
        'url': url,
        'status_code': statusCode,
        'duration_ms': duration?.inMilliseconds,
        'request_data': requestData,
        'response_data': responseData,
        'error': error,
      },
      null,
      null,
    );
  }

  /// Log de navegação
  static void logNavigation(
    String from,
    String to, {
    Map<String, dynamic>? data,
  }) {
    info(
      'Navigation: $from -> $to',
      category: LogCategory.navigation,
      data: data,
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
      'Auth: $action',
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

  /// Log de erro de rede
  static void logNetworkError(
    String operation,
    String error, {
    Map<String, dynamic>? data,
  }) {
    _log(
      LogLevel.error,
      'Network Error: $operation',
      LogCategory.network,
      {
        'operation': operation,
        'error': error,
        ...?data,
      },
      null,
      null,
    );
  }

  /// Log de erro de UI
  static void logUIError(
    String screen,
    String error, {
    Map<String, dynamic>? data,
  }) {
    _log(
      LogLevel.error,
      'UI Error: $screen',
      LogCategory.ui,
      {
        'screen': screen,
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
      'Business Event: $event',
      category: LogCategory.business,
      data: data,
    );
  }

  /// Log de analytics (versão simplificada)
  static void logAnalytics(
    String event,
    Map<String, dynamic>? parameters,
  ) {
    info(
      'Analytics: $event',
      category: LogCategory.analytics,
      data: {
        'event': event,
        'parameters': parameters,
      },
    );
  }

  /// Log de crash (versão simplificada)
  static void logCrash(
    String error,
    StackTrace? stackTrace, {
    Map<String, dynamic>? data,
  }) {
    _log(
      LogLevel.fatal,
      'Crash: $error',
      LogCategory.crash,
      data,
      error,
      stackTrace,
    );
  }

  /// Limpa logs antigos (implementação simplificada)
  static void clearOldLogs() {
    // Implementação simplificada - apenas log
    info('Clearing old logs', category: LogCategory.storage);
  }

  /// Exporta logs (implementação simplificada)
  static Future<String> exportLogs() async {
    // Implementação simplificada - retorna mensagem
    info('Exporting logs', category: LogCategory.storage);
    return 'Logs exported successfully (simplified version)';
  }

  /// Verifica se está inicializado
  static bool get isInitialized => _isInitialized;

  /// Obtém informações do dispositivo
  static Map<String, dynamic> get deviceInfo => Map.from(_deviceInfo);

  /// Obtém informações do app
  static Map<String, dynamic> get appInfo => Map.from(_appInfo);

  /// Obtém ID da sessão
  static String? get sessionId => _sessionId;

  /// Obtém ID do usuário
  static String? get userId => _userId;
}
