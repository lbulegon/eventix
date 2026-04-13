import { apiGet, apiPost } from '@/lib/api';
import { paths } from '@/lib/config/apiPaths';

type Paginated<T> = { results?: T[] };

export async function fetchFuncoesDisponiveis(): Promise<Record<string, unknown>[]> {
  const data = await apiGet<unknown>(paths.funcoes());
  if (data && typeof data === 'object' && 'results' in data) {
    const r = (data as Paginated<Record<string, unknown>>).results;
    return Array.isArray(r) ? r : [];
  }
  return [];
}

export async function fetchMinhasFuncoes(): Promise<Record<string, unknown>[]> {
  const data = await apiGet<unknown>(paths.freelancersFuncoesMinhas());
  if (Array.isArray(data)) return data as Record<string, unknown>[];
  return [];
}

export async function adicionarFuncao(funcaoId: number): Promise<{ ok: boolean; message: string }> {
  try {
    await apiPost<unknown>(paths.freelancersFuncoesAdicionar(), {
      funcao_id: funcaoId,
      nivel: 'iniciante',
    });
    return { ok: true, message: 'Função adicionada com sucesso!' };
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : 'Erro ao adicionar função';
    return { ok: false, message: msg };
  }
}
