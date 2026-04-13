import { apiGet, apiPost } from '@/lib/api';
import { paths } from '@/lib/config/apiPaths';

type Paginated<T> = { count?: number; results?: T[] };

function asList(data: unknown): Record<string, unknown>[] {
  if (data && typeof data === 'object' && 'results' in data) {
    const r = (data as Paginated<Record<string, unknown>>).results;
    return Array.isArray(r) ? r : [];
  }
  return [];
}

export async function fetchNotificacoes(page = 1, naoLidas?: boolean): Promise<Record<string, unknown>[]> {
  const data = await apiGet<unknown>(paths.notificacoes(), {
    page,
    nao_lidas: naoLidas === undefined ? undefined : naoLidas,
  });
  return asList(data);
}

export async function marcarNotificacaoLida(id: number): Promise<void> {
  await apiPost<unknown>(paths.notificacaoMarcarLida(id), {});
}
