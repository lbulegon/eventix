// lib/services/performance_service.dart
import 'dart:async';
import 'package:eventix/utils/app_logger.dart';

class PerformanceService {
  static final Map<String, Stopwatch> _activeTimers = {};
  static final Map<String, List<Duration>> _performanceHistory = {};

  /// Inicia um timer de performance
  static void startTimer(String operation) {
    _activeTimers[operation] = Stopwatch()..start();

    AppLogger.debug(
      'Performance timer started',
      category: LogCategory.performance,
      data: {'operation': operation},
    );
  }

  /// Para um timer de performance
  static Duration? stopTimer(String operation) {
    final stopwatch = _activeTimers.remove(operation);
    if (stopwatch == null) {
      AppLogger.warning(
        'Performance timer not found',
        category: LogCategory.performance,
        data: {'operation': operation},
      );
      return null;
    }

    stopwatch.stop();
    final duration = Duration(milliseconds: stopwatch.elapsedMilliseconds);

    // Armazena no histórico
    _performanceHistory.putIfAbsent(operation, () => []).add(duration);

    // Log da performance
    AppLogger.logPerformance(
      operation,
      duration,
      additionalData: {
        'operation': operation,
        'duration_ms': duration.inMilliseconds,
        'duration_seconds': duration.inSeconds,
      },
    );

    return duration;
  }

  /// Mede a performance de uma operação
  static Future<T> measureOperation<T>(
    String operation,
    Future<T> Function() operationFunction,
  ) async {
    startTimer(operation);
    try {
      final result = await operationFunction();
      stopTimer(operation);
      return result;
    } catch (e) {
      stopTimer(operation);
      AppLogger.error(
        'Performance operation failed',
        category: LogCategory.performance,
        error: e,
        data: {'operation': operation},
      );
      rethrow;
    }
  }

  /// Mede a performance de uma operação síncrona
  static T measureSyncOperation<T>(
    String operation,
    T Function() operationFunction,
  ) {
    startTimer(operation);
    try {
      final result = operationFunction();
      stopTimer(operation);
      return result;
    } catch (e) {
      stopTimer(operation);
      AppLogger.error(
        'Performance sync operation failed',
        category: LogCategory.performance,
        error: e,
        data: {'operation': operation},
      );
      rethrow;
    }
  }

  /// Obtém estatísticas de performance
  static Map<String, dynamic> getPerformanceStats(String operation) {
    final history = _performanceHistory[operation];
    if (history == null || history.isEmpty) {
      return {
        'operation': operation,
        'count': 0,
        'average_ms': 0,
        'min_ms': 0,
        'max_ms': 0,
        'total_ms': 0,
      };
    }

    final totalMs =
        history.fold<int>(0, (sum, duration) => sum + duration.inMilliseconds);
    final averageMs = totalMs / history.length;
    final minMs =
        history.map((d) => d.inMilliseconds).reduce((a, b) => a < b ? a : b);
    final maxMs =
        history.map((d) => d.inMilliseconds).reduce((a, b) => a > b ? a : b);

    return {
      'operation': operation,
      'count': history.length,
      'average_ms': averageMs.round(),
      'min_ms': minMs,
      'max_ms': maxMs,
      'total_ms': totalMs,
    };
  }

  /// Obtém todas as estatísticas de performance
  static Map<String, Map<String, dynamic>> getAllPerformanceStats() {
    final stats = <String, Map<String, dynamic>>{};
    for (final operation in _performanceHistory.keys) {
      stats[operation] = getPerformanceStats(operation);
    }
    return stats;
  }

  /// Limpa o histórico de performance
  static void clearPerformanceHistory() {
    _performanceHistory.clear();
    AppLogger.info(
      'Performance history cleared',
      category: LogCategory.performance,
    );
  }

  /// Limpa o histórico de uma operação específica
  static void clearOperationHistory(String operation) {
    _performanceHistory.remove(operation);
    AppLogger.info(
      'Performance history cleared for operation',
      category: LogCategory.performance,
      data: {'operation': operation},
    );
  }

  /// Verifica se uma operação está demorando muito
  static bool isOperationSlow(String operation, {int thresholdMs = 1000}) {
    final history = _performanceHistory[operation];
    if (history == null || history.isEmpty) return false;

    final lastDuration = history.last;
    return lastDuration.inMilliseconds > thresholdMs;
  }

  /// Obtém operações lentas
  static List<String> getSlowOperations({int thresholdMs = 1000}) {
    final slowOperations = <String>[];
    for (final operation in _performanceHistory.keys) {
      if (isOperationSlow(operation, thresholdMs: thresholdMs)) {
        slowOperations.add(operation);
      }
    }
    return slowOperations;
  }

  /// Log de performance resumido
  static void logPerformanceSummary() {
    final stats = getAllPerformanceStats();

    AppLogger.info(
      'Performance summary',
      category: LogCategory.performance,
      data: {
        'total_operations': stats.length,
        'operations': stats,
        'slow_operations': getSlowOperations(),
      },
    );
  }
}
