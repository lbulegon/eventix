/**
 * Caminhos relativos à raiz do Django (espelho de `mobile/eventix/lib/utils/app_config.dart`).
 * Usar com `apiGet` / `apiPost` de `@/lib/api` (juntam `NEXT_PUBLIC_API_URL`).
 */
export const paths = {
  login: () => `/api/v1/auth/login/`,
  refresh: () => `/api/v1/auth/refresh/`,
  logout: () => `/api/v1/auth/logout/`,
  userProfile: () => `/api/v1/users/profile/`,
  vagas: () => `/api/v1/vagas/`,
  vagasRecomendadas: () => `/api/v1/vagas-avancadas/recomendadas/`,
  candidaturas: () => `/api/v1/candidaturas/`,
  candidaturaCancelar: (id: number) => `/api/v1/candidaturas/${id}/cancelar/`,
  notificacoes: () => `/api/v1/notificacoes/`,
  notificacaoMarcarLida: (id: number) => `/api/v1/notificacoes/${id}/marcar_lida/`,
  funcoes: () => `/api/v1/funcoes/`,
  freelancersFuncoesMinhas: () => `/api/v1/freelancers/funcoes/minhas_funcoes/`,
  freelancersFuncoesAdicionar: () => `/api/v1/freelancers/funcoes/adicionar_funcao/`,
  freelancers: () => `/api/v1/freelancers/`,
} as const;
