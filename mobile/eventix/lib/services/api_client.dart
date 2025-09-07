// lib/services/api_client.dart
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:eventix/utils/app_config.dart';
import 'package:eventix/services/logging_interceptor.dart';

class ApiResponse {
  final int statusCode;
  final String body;
  final Map<String, List<String>> headers;
  ApiResponse(
      {required this.statusCode, required this.body, required this.headers});
}

class ApiClient {
  static final Dio dio = Dio()..interceptors.add(LoggingInterceptor());

  static String _normalize(String pathOrUrl) {
    if (pathOrUrl.startsWith('http')) return pathOrUrl;
    // caminhos iniciando com "/" viram {base}/{apiPrefix}/...
    if (pathOrUrl.startsWith('/')) return '${AppConfig.apiUrl}$pathOrUrl';
    return '${AppConfig.apiUrl}/$pathOrUrl';
  }

  static ApiResponse _ok(Response r) {
    final bodyStr = r.data is String ? r.data : jsonEncode(r.data);
    final hdrs = <String, List<String>>{};
    r.headers.forEach((k, v) => hdrs[k] = v.map((e) => e.toString()).toList());
    return ApiResponse(
        statusCode: r.statusCode ?? 0, body: bodyStr, headers: hdrs);
  }

  static ApiResponse _err(DioException e) {
    final status = e.response?.statusCode ?? 0;
    final data = e.response?.data;
    final bodyStr =
        data is String ? data : jsonEncode(data ?? {'error': e.message});
    final hdrs = <String, List<String>>{};
    e.response?.headers
        .forEach((k, v) => hdrs[k] = v.map((e) => e.toString()).toList());
    return ApiResponse(statusCode: status, body: bodyStr, headers: hdrs);
  }

  static Future<ApiResponse> get(String pathOrUrl,
      {Map<String, dynamic>? query}) async {
    try {
      final r = await dio.get(_normalize(pathOrUrl), queryParameters: query);
      return _ok(r);
    } on DioException catch (e) {
      return _err(e);
    }
  }

  static Future<ApiResponse> post(String pathOrUrl, dynamic data,
      {Map<String, dynamic>? query}) async {
    try {
      final r = await dio.post(_normalize(pathOrUrl),
          data: data, queryParameters: query);
      return _ok(r);
    } on DioException catch (e) {
      return _err(e);
    }
  }

  static Future<ApiResponse> put(String pathOrUrl, dynamic data,
      {Map<String, dynamic>? query}) async {
    try {
      final r = await dio.put(_normalize(pathOrUrl),
          data: data, queryParameters: query);
      return _ok(r);
    } on DioException catch (e) {
      return _err(e);
    }
  }

  static Future<ApiResponse> delete(String pathOrUrl,
      {Map<String, dynamic>? query}) async {
    try {
      final r = await dio.delete(_normalize(pathOrUrl), queryParameters: query);
      return _ok(r);
    } on DioException catch (e) {
      return _err(e);
    }
  }
}
