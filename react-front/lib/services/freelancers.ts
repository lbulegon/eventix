import { ApiError, apiFetch, apiGet, formatApiErrorBody } from '@/lib/api';
import { paths } from '@/lib/config/apiPaths';

/** GET /freelancers/ — mesmo endpoint do app mobile para perfil. */
export async function fetchFreelancerPerfil(): Promise<Record<string, unknown> | null> {
  try {
    const data = await apiGet<unknown>(paths.freelancers());
    if (Array.isArray(data)) {
      return (data[0] as Record<string, unknown>) ?? null;
    }
    if (data && typeof data === 'object' && 'results' in data) {
      const r = (data as { results: Record<string, unknown>[] }).results;
      return r?.[0] ?? null;
    }
    if (data && typeof data === 'object') {
      return data as Record<string, unknown>;
    }
    return null;
  } catch {
    return null;
  }
}

type PreCadastroPayload = {
  nome_completo: string;
  telefone: string;
  cpf: string;
  email: string;
  password: string;
  data_nascimento?: string;
  sexo?: 'M' | 'F';
  habilidades?: string;
};

export async function preCadastrarFreelancer(payload: PreCadastroPayload): Promise<string> {
  const res = await apiFetch(paths.freelancersPreCadastro(), {
    method: 'POST',
    skipAuth: true,
    body: JSON.stringify(payload),
    headers: { 'Content-Type': 'application/json' },
  });

  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new ApiError(formatApiErrorBody(body), res.status, body);
  }
  const msg = (body as { message?: string }).message;
  return msg || 'Pré-cadastro realizado com sucesso.';
}
