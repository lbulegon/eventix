import { getPublicApiBaseUrl, assertApiUrlConfigured } from '@/lib/env';
import { ApiError, formatApiErrorBody } from '@/lib/api/errors';
import { getAccessToken } from '@/lib/api/storage';
import { refreshAccessToken } from '@/lib/api/auth';

export type ApiFetchOptions = RequestInit & {
  /** Não enviar Authorization (rotas públicas). */
  skipAuth?: boolean;
};

function joinUrl(path: string): string {
  assertApiUrlConfigured();
  const base = getPublicApiBaseUrl();
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${base}${p}`;
}

/**
 * fetch para a API Django com Bearer JWT.
 * Em 401, tenta uma vez refresh do access token (se houver refresh guardado).
 */
export async function apiFetch(path: string, init: ApiFetchOptions = {}): Promise<Response> {
  const { skipAuth, headers: initHeaders, ...rest } = init;
  const headers = new Headers(initHeaders);

  if (!skipAuth) {
    let token = getAccessToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  if (!headers.has('Content-Type') && rest.body && typeof rest.body === 'string') {
    headers.set('Content-Type', 'application/json');
  }

  let res = await fetch(joinUrl(path), { ...rest, headers });

  if (res.status === 401 && !skipAuth) {
    const newAccess = await refreshAccessToken();
    if (newAccess) {
      headers.set('Authorization', `Bearer ${newAccess}`);
      res = await fetch(joinUrl(path), { ...rest, headers });
    }
  }

  return res;
}

/** fetch + parse JSON; lança ApiError se !ok. */
export async function apiJson<T>(path: string, init: ApiFetchOptions = {}): Promise<T> {
  const res = await apiFetch(path, init);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new ApiError(formatApiErrorBody(body, res.status), res.status, body);
  }
  return body as T;
}

function withQuery(path: string, query?: Record<string, string | number | boolean | undefined | null>): string {
  if (!query) return path;
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(query)) {
    if (v !== undefined && v !== null) q.set(k, String(v));
  }
  const s = q.toString();
  return s ? `${path}${path.includes('?') ? '&' : '?'}${s}` : path;
}

/** GET JSON autenticado (query opcional). */
export function apiGet<T>(path: string, query?: Record<string, string | number | boolean | undefined | null>): Promise<T> {
  return apiJson<T>(withQuery(path, query), { method: 'GET' });
}

/** POST JSON autenticado. */
export function apiPost<T>(path: string, data: unknown): Promise<T> {
  return apiJson<T>(path, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}
