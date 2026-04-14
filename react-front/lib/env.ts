import { sanitizeApiBaseUrl, stripTrailingSlash, withHttpScheme } from '@/lib/sanitizeApiBaseUrl';

/**
 * URL base usada pelo browser para chamar a API Django.
 *
 * - Em **produção no browser** o default é sempre `/api/eventix` (proxy no
 *   próprio Next): no Railway a variável `NEXT_PUBLIC_API_URL` muitas vezes
 *   **não existe no bundle** gerado no `next build`, mas o **processo Node**
 *   vê-a em runtime — o proxy encaminha usando `NEXT_PUBLIC_API_URL` ou
 *   `EVENTIX_API_URL` no servidor.
 * - `NEXT_PUBLIC_API_DIRECT=true` — força chamada direta ao Django no browser
 *   em produção (só use se o build receber a URL correta e CORS/HTTPS estiverem ok).
 * - `NEXT_PUBLIC_API_VIA_PROXY=true` — igual ao default prod (redundante).
 * - Em desenvolvimento (`next dev`), usa `NEXT_PUBLIC_API_URL` se existir.
 */
function normalizeDirectBase(url: string): string {
  let u = url.replace(/\/$/, '');
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    if (u.toLowerCase().startsWith('http://')) {
      u = `https://${u.slice('http://'.length)}`;
    }
  }
  if (typeof window !== 'undefined') {
    try {
      const parsed = new URL(u);
      if (/\.railway\.internal$/i.test(parsed.hostname) || /^10\.\d+\.\d+\.\d+$/i.test(parsed.hostname)) {
        return '/api/eventix';
      }
    } catch {
      /* ignora */
    }
  }
  return u;
}

export function getPublicApiBaseUrl(): string {
  const forceProxy =
    process.env.NEXT_PUBLIC_API_VIA_PROXY === '1' ||
    process.env.NEXT_PUBLIC_API_VIA_PROXY === 'true';
  if (forceProxy) {
    return '/api/eventix';
  }

  const apiDirect =
    process.env.NEXT_PUBLIC_API_DIRECT === '1' ||
    process.env.NEXT_PUBLIC_API_DIRECT === 'true';

  if (
    typeof window !== 'undefined' &&
    process.env.NODE_ENV === 'production' &&
    !apiDirect
  ) {
    return '/api/eventix';
  }

  const raw = sanitizeApiBaseUrl(process.env.NEXT_PUBLIC_API_URL ?? '');
  if (!raw) {
    return '/api/eventix';
  }
  return normalizeDirectBase(stripTrailingSlash(withHttpScheme(raw)));
}

/** Mantido por compatibilidade; o proxy cobre o caso sem URL pública. */
export function assertApiUrlConfigured(): void {}
