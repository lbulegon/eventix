import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';

class UserProvider extends ChangeNotifier {
  int? _id;
  String? _nome;
  String? _email;
  String? _tipoUsuario; // 'freelancer', 'empresa', 'admin'

  int? get id => _id;
  String? get nome => _nome;
  String? get email => _email;
  String? get tipoUsuario => _tipoUsuario;

  bool get isLoggedIn => _id != null;
  bool get isFreelancer => _tipoUsuario == 'freelancer';
  bool get isEmpresa => _tipoUsuario == 'empresa';
  bool get isAdmin => _tipoUsuario == 'admin';

  /// Define os dados do usuário logado
  void setUserData({
    required int id,
    required String nome,
    required String email,
    required String tipoUsuario,
  }) {
    _id = id;
    _nome = nome;
    _email = email;
    _tipoUsuario = tipoUsuario;
    notifyListeners();
  }

  /// Limpa dados do usuário (logout)
  void clearUserData() {
    _id = null;
    _nome = null;
    _email = null;
    _tipoUsuario = null;
    notifyListeners();
  }
}
