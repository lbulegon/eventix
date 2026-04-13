const KEY_ACCESS = 'eventix_access_token';
const KEY_REFRESH = 'eventix_refresh_token';
const KEY_USER = 'eventix_user';

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(KEY_ACCESS);
}

export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(KEY_REFRESH);
}

export function setTokens(access: string, refresh: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(KEY_ACCESS, access);
  localStorage.setItem(KEY_REFRESH, refresh);
}

export function setAccessToken(access: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(KEY_ACCESS, access);
}

export function clearTokens(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(KEY_ACCESS);
  localStorage.removeItem(KEY_REFRESH);
  localStorage.removeItem(KEY_USER);
}

export function setUserJson(user: unknown): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(KEY_USER, JSON.stringify(user));
}

export function getUserJson<T = Record<string, unknown>>(): T | null {
  if (typeof window === 'undefined') return null;
  const raw = localStorage.getItem(KEY_USER);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}
