import { getPublicApiBaseUrl, assertApiUrlConfigured } from '@/lib/env';
import { ApiError, formatApiErrorBody } from '@/lib/api/errors';
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setTokens,
  setUserJson,
} from '@/lib/api/storage';
import type { LoginResponse } from '@/lib/api/types';

const JSON_HEADERS = { 'Content-Type': 'application/json' } as const;

/**
 * Login JWT (mesmo contrato da app mobile): username + password Django.
 * Grava access/refresh em localStorage.
 */
export async function loginWithPassword(username: string, password: string): Promise<LoginResponse> {
  assertApiUrlConfigured();
  const base = getPublicApiBaseUrl();
  const res = await fetch(`${base}/api/v1/auth/login/`, {
    method: 'POST',
    headers: { ...JSON_HEADERS },
    body: JSON.stringify({ username, password }),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new ApiError(formatApiErrorBody(body), res.status, body);
  }
  const data = body as LoginResponse;
  if (!data.tokens?.access || !data.tokens?.refresh) {
    throw new ApiError('Resposta de login sem tokens.', res.status, body);
  }
  setTokens(data.tokens.access, data.tokens.refresh);
  setUserJson(data.user);
  return data;
}

/** POST /api/v1/auth/refresh/ — atualiza só o access token. */
export async function refreshAccessToken(): Promise<string | null> {
  assertApiUrlConfigured();
  const refresh = getRefreshToken();
  if (!refresh) return null;

  const base = getPublicApiBaseUrl();
  const res = await fetch(`${base}/api/v1/auth/refresh/`, {
    method: 'POST',
    headers: { ...JSON_HEADERS },
    body: JSON.stringify({ refresh }),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    clearTokens();
    return null;
  }
  const access = (body as { access?: string }).access;
  if (!access) {
    clearTokens();
    return null;
  }
  setAccessToken(access);
  return access;
}

/** Remove sessão local (e tenta POST logout no Django, como no app mobile). */
export async function logoutClient(): Promise<void> {
  const base = getPublicApiBaseUrl();
  const token = getAccessToken();
  if (base && token) {
    try {
      await fetch(`${base}/api/v1/auth/logout/`, {
        method: 'POST',
        headers: { ...JSON_HEADERS, Authorization: `Bearer ${token}` },
      });
    } catch {
      /* ignora rede */
    }
  }
  clearTokens();
}
