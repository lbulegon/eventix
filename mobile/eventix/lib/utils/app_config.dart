class AppConfig {
  static const String baseUrl = 'https://eventix-development.up.railway.app';
  static const String apiPrefix = '/api/v1';
  static const String apiUrl = '$baseUrl$apiPrefix';

  // Autenticação
  static const String login = '$baseUrl/api/auth/login/';
  static const String refreshToken = '$baseUrl/api/auth/refresh/';
  static const String logout = '$baseUrl/api/auth/logout/';
  static const String tokenVerify = '$apiUrl/token/verify/';
  static const String userProfile = '$apiUrl/users/profile/';

  // Endpoints de Freelancers
  static const String preCadastro = '$apiUrl/freelancers/pre_cadastro/';
  static const String freelancerProfile = '$apiUrl/freelancers/';

  // Endpoints de Vagas
  static const String vagasDisponiveis = '$apiUrl/vagas/';
  static const String candidaturas = '$apiUrl/candidaturas/';
  static const String cancelarCandidatura = '$apiUrl/candidaturas/';
  static const String aprovarCandidatura = '$apiUrl/candidaturas/';
  static const String rejeitarCandidatura = '$apiUrl/candidaturas/';

  // Endpoints de Eventos
  static const String eventos = '$apiUrl/eventos/';
  static const String meusEventos = '$apiUrl/eventos/meus_eventos/';
  static const String criarEvento = '$apiUrl/eventos/';

  // Endpoints de Empresas
  static const String empresas = '$apiUrl/empresas/';
  static const String empresasContratantes = '$apiUrl/empresas-contratantes/';

  // Recuperação de Senha
  static const String passwordReset = '$apiUrl/password/password-reset/';
  static const String passwordResetConfirm =
      '$apiUrl/password/password-reset/confirm/';
}
