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

export function formatApiErrorBody(body: unknown): string {
  if (body == null || typeof body !== 'object') {
    return typeof body === 'string' ? body : 'Pedido inválido';
  }
  const o = body as Record<string, unknown>;
  if (typeof o.detail === 'string') return o.detail;
  if (Array.isArray(o.non_field_errors) && o.non_field_errors.length)
    return String(o.non_field_errors[0]);
  if (typeof o.message === 'string') return o.message;
  try {
    return JSON.stringify(body);
  } catch {
    return 'Erro desconhecido';
  }
}
