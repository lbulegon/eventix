/**
 * URL base usada pelo browser para chamar a API Django.
 *
 * - `NEXT_PUBLIC_API_VIA_PROXY=true` — força o proxy `/api/eventix/...` mesmo
 *   com `NEXT_PUBLIC_API_URL` (útil se a URL pública estiver errada no build).
 * - Sem `NEXT_PUBLIC_API_URL`, usa o proxy (servidor: `EVENTIX_API_URL`).
 * - Com `NEXT_PUBLIC_API_URL`, chamada direta ao Django; no browser, `http://`
 *   é promovido a `https://` se a página estiver em HTTPS (evita “Failed to
 *   fetch” por conteúdo misto). URLs só acessíveis na rede interna do Railway
 *   fazem fallback para o proxy.
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

  const raw = process.env.NEXT_PUBLIC_API_URL?.trim() ?? '';
  if (!raw) {
    return '/api/eventix';
  }
  const withProtocol = /^https?:\/\//i.test(raw) ? raw : `https://${raw}`;
  return normalizeDirectBase(withProtocol);
}

/** Mantido por compatibilidade; o proxy cobre o caso sem URL pública. */
export function assertApiUrlConfigured(): void {}
