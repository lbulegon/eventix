import { apiGet, apiPost } from '@/lib/api';
import { paths } from '@/lib/config/apiPaths';

type Paginated<T> = { count?: number; results?: T[] };

function asList<T extends Record<string, unknown>>(data: unknown): T[] {
  if (data && typeof data === 'object' && 'results' in data) {
    const r = (data as Paginated<T>).results;
    return Array.isArray(r) ? (r as T[]) : [];
  }
  return [];
}

export async function fetchVagas(params?: {
  page?: number;
  search?: string;
  eventoId?: number;
  funcaoId?: number;
  cidade?: string;
}): Promise<{ results: Record<string, unknown>[]; count: number }> {
  const data = await apiGet<Paginated<Record<string, unknown>>>(paths.vagas(), {
    page: params?.page ?? 1,
    search: params?.search,
    evento_id: params?.eventoId,
    funcao_id: params?.funcaoId,
    cidade: params?.cidade,
  });
  const results = asList(data);
  return { results, count: typeof data.count === 'number' ? data.count : results.length };
}

export async function fetchVagasRecomendadas(page = 1): Promise<Record<string, unknown>[]> {
  const data = await apiGet<unknown>(paths.vagasRecomendadas(), { page });
  return asList(data);
}

export async function fetchMinhasCandidaturas(): Promise<Record<string, unknown>[]> {
  const data = await apiGet<unknown>(paths.candidaturas());
  return asList(data);
}

export async function candidatarNaVaga(vagaId: number): Promise<{ ok: boolean; message: string }> {
  try {
    await apiPost<unknown>(paths.candidaturas(), { vaga_id: vagaId });
    return { ok: true, message: 'Candidatura realizada com sucesso!' };
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : 'Erro na candidatura';
    return { ok: false, message: msg };
  }
}

export async function cancelarCandidatura(id: number): Promise<{ ok: boolean; message: string }> {
  try {
    await apiPost<unknown>(paths.candidaturaCancelar(id), {});
    return { ok: true, message: 'Candidatura cancelada com sucesso!' };
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : 'Erro ao cancelar';
    return { ok: false, message: msg };
  }
}
