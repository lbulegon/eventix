import { apiGet } from '@/lib/api';
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
