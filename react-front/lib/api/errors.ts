export class ApiError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

/** Extrai texto legível de detail (DRF / SimpleJWT: string ou lista). */
function detailToMessage(detail: unknown): string | null {
  if (detail == null) return null;
  if (typeof detail === 'string') return detail;
  if (typeof detail === 'number' || typeof detail === 'boolean') {
    return null; // evita mostrar só "0" ou "false"
  }
  if (Array.isArray(detail)) {
    const first = detail[0];
    if (typeof first === 'string') return first;
    if (first && typeof first === 'object' && 'string' in first) {
      const s = (first as { string?: string }).string;
      if (typeof s === 'string') return s;
    }
  }
  return null;
}

function nonFieldFirstMessage(arr: unknown[]): string | null {
  const first = arr[0];
  if (typeof first === 'string') return first;
  if (typeof first === 'number' || typeof first === 'boolean') {
    return 'Não foi possível validar o pedido. Tente novamente.';
  }
  return null;
}

export function formatApiErrorBody(body: unknown, httpStatus?: number): string {
  if (body == null || typeof body !== 'object') {
    return typeof body === 'string' ? body : 'Pedido inválido';
  }
  const o = body as Record<string, unknown>;
  const hint = typeof o.hint === 'string' && o.hint.trim() ? o.hint.trim() : '';
  const debug = typeof o.debug === 'string' && o.debug.trim() ? o.debug.trim() : '';

  const fromDetail = detailToMessage(o.detail);
  if (fromDetail) {
    return [fromDetail, hint, debug].filter(Boolean).join('\n\n');
  }

  if (Array.isArray(o.non_field_errors) && o.non_field_errors.length) {
    const msg = nonFieldFirstMessage(o.non_field_errors);
    if (msg) return [msg, hint, debug].filter(Boolean).join('\n\n');
  }

  if (typeof o.message === 'string') {
    return [o.message, hint, debug].filter(Boolean).join('\n\n');
  }

  // Erros por campo: { username: ["..."], password: ["..."] }
  for (const key of Object.keys(o)) {
    if (key === 'detail' || key === 'non_field_errors' || key === 'hint' || key === 'debug') continue;
    const val = o[key];
    if (Array.isArray(val) && val.length) {
      const first = val[0];
      if (typeof first === 'string') return [first, hint, debug].filter(Boolean).join('\n\n');
    }
  }

  try {
    const s = JSON.stringify(body);
    if (s && s !== '{}' && s !== '[]') return [s, hint, debug].filter(Boolean).join('\n\n');
  } catch {
    /* ignore */
  }
  const fallback =
    httpStatus != null && httpStatus > 0
      ? `O servidor respondeu com HTTP ${httpStatus}. Se o problema continuar, verifique os logs do Django.`
      : 'Erro desconhecido';
  return [fallback, hint, debug].filter(Boolean).join('\n\n');
}
