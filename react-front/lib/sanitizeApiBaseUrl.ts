/**
 * Normaliza URL base vinda de variáveis de ambiente.
 * No Railway, valores copiados ou referências mal coladas podem começar por
 * "=" ou "==", o que quebraria o prefixo https:// (ex.: https://=https://host).
 */
export function sanitizeApiBaseUrl(raw: string): string {
  let s = raw.trim();
  if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
    s = s.slice(1, -1).trim();
  }
  while (s.startsWith('=')) {
    s = s.slice(1).trim();
  }
  return s.trim();
}

export function withHttpScheme(url: string): string {
  const s = sanitizeApiBaseUrl(url);
  if (!s) return '';
  return /^https?:\/\//i.test(s) ? s : `https://${s}`;
}

export function stripTrailingSlash(url: string): string {
  return url.replace(/\/$/, '');
}
