// lib/services/local_storage.dart
import 'package:shared_preferences/shared_preferences.dart';

class LocalStorage {
  static const String _keyAccessToken = 'access_token';
  static const String _keyRefreshToken = 'refresh_token';
  static const String _keyUserId = 'user_id';
  static const String _keyNome = 'nome';
  static const String _keyTelefone = 'telefone';
  static const String _keyEmail = 'email';
  static const String _keyTipoUsuario = 'tipo_usuario';

  // TOKENS
  static Future<void> saveTokens(String access, String refresh) async {
    final p = await SharedPreferences.getInstance();
    await p.setString(_keyAccessToken, access);
    await p.setString(_keyRefreshToken, refresh);
  }

  static Future<void> setAccessToken(String access) async {
    final p = await SharedPreferences.getInstance();
    await p.setString(_keyAccessToken, access);
  }

  static Future<void> setRefreshToken(String refresh) async {
    final p = await SharedPreferences.getInstance();
    await p.setString(_keyRefreshToken, refresh);
  }

  static Future<void> setTokensIfPresent(
      {String? access, String? refresh}) async {
    final p = await SharedPreferences.getInstance();
    if (access != null && access.isNotEmpty) {
      await p.setString(_keyAccessToken, access);
    }
    if (refresh != null && refresh.isNotEmpty) {
      await p.setString(_keyRefreshToken, refresh);
    }
  }

  static Future<String?> getAccessToken() async {
    final p = await SharedPreferences.getInstance();
    return p.getString(_keyAccessToken);
  }

  static Future<String?> getRefreshToken() async {
    final p = await SharedPreferences.getInstance();
    return p.getString(_keyRefreshToken);
  }

  static Future<void> clearTokens() async {
    final p = await SharedPreferences.getInstance();
    await p.remove(_keyAccessToken);
    await p.remove(_keyRefreshToken);
  }

  // DADOS
  static Future<void> saveUserData(int id, String nome, String telefone,
      String email, String tipoUsuario) async {
    final p = await SharedPreferences.getInstance();
    await p.setInt(_keyUserId, id);
    await p.setString(_keyNome, nome);
    await p.setString(_keyTelefone, telefone);
    await p.setString(_keyEmail, email);
    await p.setString(_keyTipoUsuario, tipoUsuario);
  }

  static Future<int> getUserId() async {
    final p = await SharedPreferences.getInstance();
    return p.getInt(_keyUserId) ?? 0;
  }

  static Future<String> getNome() async {
    final p = await SharedPreferences.getInstance();
    return p.getString(_keyNome) ?? '';
  }

  static Future<String> getTelefone() async {
    final p = await SharedPreferences.getInstance();
    return p.getString(_keyTelefone) ?? '';
  }

  static Future<String> getEmail() async {
    final p = await SharedPreferences.getInstance();
    return p.getString(_keyEmail) ?? '';
  }

  static Future<String> getTipoUsuario() async {
    final p = await SharedPreferences.getInstance();
    return p.getString(_keyTipoUsuario) ?? '';
  }

  // LIMPAR
  static Future<void> clearAll() => clear();
  static Future<void> clear() async {
    final p = await SharedPreferences.getInstance();
    await p.clear();
  }
}
