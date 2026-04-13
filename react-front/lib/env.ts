/**
 * URL base pública do backend Django (exposta ao browser via NEXT_PUBLIC_*).
 */
export function getPublicApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim() ?? '';
  return raw.replace(/\/$/, '');
}

export function assertApiUrlConfigured(): void {
  if (!getPublicApiBaseUrl()) {
    throw new Error(
      'Defina NEXT_PUBLIC_API_URL no .env.local (copie de .env.example). Ex.: http://127.0.0.1:8000',
    );
  }
}
