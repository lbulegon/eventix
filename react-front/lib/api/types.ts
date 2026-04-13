/** Resposta de POST /api/v1/auth/login/ (CustomTokenObtainPairView). */
export type LoginUser = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  tipo_usuario: string;
  freelance_id?: number;
  nome_completo?: string;
  cadastro_completo?: boolean;
  empresa_id?: number;
  empresa_nome?: string;
};

export type LoginTokens = {
  access: string;
  refresh: string;
};

export type LoginResponse = {
  user: LoginUser;
  tokens: LoginTokens;
};
