// lib/services/logging_interceptor.dart
import 'package:dio/dio.dart';
import 'package:eventix/utils/app_logger.dart';

class LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final stopwatch = Stopwatch()..start();
    options.extra['start_time'] = stopwatch;

    AppLogger.debug(
      'API Request: ${options.method} ${options.uri}',
      category: LogCategory.api,
      data: {
        'method': options.method,
        'url': options.uri.toString(),
        'headers': options.headers,
        'query_parameters': options.queryParameters,
        'data': options.data,
      },
    );

    super.onRequest(options, handler);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    final stopwatch = response.requestOptions.extra['start_time'] as Stopwatch?;
    stopwatch?.stop();

    AppLogger.logApi(
      response.requestOptions.method,
      response.requestOptions.uri.toString(),
      response.statusCode ?? 0,
      requestData: response.requestOptions.data,
      responseData: response.data,
      duration: stopwatch != null
          ? Duration(milliseconds: stopwatch.elapsedMilliseconds)
          : null,
    );

    super.onResponse(response, handler);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final stopwatch = err.requestOptions.extra['start_time'] as Stopwatch?;
    stopwatch?.stop();

    AppLogger.error(
      'API Error: ${err.requestOptions.method} ${err.requestOptions.uri}',
      category: LogCategory.api,
      error: err,
      data: {
        'method': err.requestOptions.method,
        'url': err.requestOptions.uri.toString(),
        'status_code': err.response?.statusCode,
        'error_type': err.type.toString(),
        'error_message': err.message,
        'response_data': err.response?.data,
        'duration_ms': stopwatch?.elapsedMilliseconds,
      },
    );

    super.onError(err, handler);
  }
}
