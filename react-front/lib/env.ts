/**
 * URL base usada pelo browser para chamar a API Django.
 *
 * - Se `NEXT_PUBLIC_API_URL` estiver definida, os pedidos vão direto ao Django
 *   (útil em desenvolvimento local).
 * - Caso contrário, usa o proxy same-origin `/api/eventix/...` (recomendado no
 *   Railway: evita CORS e não exige embutir a URL do backend no build do
 *   cliente — configure `EVENTIX_API_URL` só no servidor Next).
 */
export function getPublicApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim() ?? '';
  if (!raw) {
    return '/api/eventix';
  }
  const withProtocol = /^https?:\/\//i.test(raw) ? raw : `https://${raw}`;
  return withProtocol.replace(/\/$/, '');
}

/** Mantido por compatibilidade; o proxy cobre o caso sem URL pública. */
export function assertApiUrlConfigured(): void {}
