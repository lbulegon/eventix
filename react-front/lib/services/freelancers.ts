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

function parseResponseBody(raw: string, contentType: string, status: number): unknown {
  const trimmed = raw.trim();
  if (!trimmed) return {};
  if (contentType.includes('application/json') || trimmed.startsWith('{') || trimmed.startsWith('[')) {
    try {
      return JSON.parse(trimmed) as unknown;
    } catch {
      return { detail: trimmed.slice(0, 400) };
    }
  }
  return {
    detail:
      trimmed.slice(0, 300).trim() ||
      `Resposta não JSON do servidor (HTTP ${status}).`,
  };
}

export async function preCadastrarFreelancer(payload: PreCadastroPayload): Promise<string> {
  const res = await apiFetch(paths.freelancersPreCadastro(), {
    method: 'POST',
    skipAuth: true,
    body: JSON.stringify(payload),
    headers: { 'Content-Type': 'application/json' },
  });

  const raw = await res.text();
  const ct = res.headers.get('content-type') ?? '';
  const body = parseResponseBody(raw, ct, res.status);

  if (!res.ok) {
    throw new ApiError(formatApiErrorBody(body, res.status), res.status, body);
  }
  const msg = (body as { message?: string }).message;
  return msg || 'Pré-cadastro realizado com sucesso.';
}
