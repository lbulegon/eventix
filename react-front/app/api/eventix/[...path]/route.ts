import dns from 'node:dns';
import { NextRequest, NextResponse } from 'next/server';
import { stripTrailingSlash, withHttpScheme } from '@/lib/sanitizeApiBaseUrl';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

try {
  dns.setDefaultResultOrder('ipv4first');
} catch {
  /* Node antigo */
}

const UPSTREAM_TIMEOUT_MS = 25_000;

const RAILWAY_HINT =
  'No Railway, se o pedido falhar entre serviços, defina EVENTIX_API_URL no serviço Next com o URL ' +
  'privado do Django (Painel do serviço Django → Networking → endpoint da rede privada, ex.: http://…railway.internal:PORT) ' +
  'ou confirme que o serviço Django está online. Não coloque "=" no início do valor (ex.: use https://… e não =https://…). ' +
  'Opcional: EVENTIX_PROXY_DEBUG=1 para ver o erro técnico nos logs e na resposta.';

function targetBase(): string {
  const raw =
    process.env.EVENTIX_API_URL?.trim() ||
    process.env.NEXT_PUBLIC_API_URL?.trim() ||
    '';
  if (!raw) return '';
  return stripTrailingSlash(withHttpScheme(raw));
}

function forwardHeaders(req: NextRequest): Headers {
  const h = new Headers();
  const auth = req.headers.get('authorization');
  if (auth) h.set('authorization', auth);
  const ct = req.headers.get('content-type');
  if (ct) h.set('content-type', ct);
  const ctx = req.headers.get('x-empresa-context-id');
  if (ctx) h.set('x-empresa-context-id', ctx);
  return h;
}

function upstreamErrorPayload(err: unknown): { detail: string; hint: string; debug?: string } {
  const detail = 'Não foi possível contactar o backend Eventix.';
  const hint = RAILWAY_HINT;
  const showDebug = process.env.EVENTIX_PROXY_DEBUG === '1' || process.env.EVENTIX_PROXY_DEBUG === 'true';
  if (!showDebug) {
    return { detail, hint };
  }
  const msg = err instanceof Error ? `${err.name}: ${err.message}` : String(err);
  return { detail, hint, debug: msg };
}

async function proxy(req: NextRequest, segments: string[]): Promise<NextResponse> {
  const suffix = segments.join('/');
  if (!suffix.startsWith('api/')) {
    return NextResponse.json({ detail: 'Caminho não permitido.' }, { status: 403 });
  }
  const base = targetBase();
  if (!base) {
    return NextResponse.json(
      {
        detail:
          'Proxy Eventix: defina EVENTIX_API_URL (recomendado) ou NEXT_PUBLIC_API_URL no serviço Next.js.',
        hint: RAILWAY_HINT,
      },
      { status: 503 },
    );
  }
  const url = `${base}/${suffix}${req.nextUrl.search}`;

  const method = req.method.toUpperCase();
  const headers = forwardHeaders(req);
  let body: ArrayBuffer | undefined;
  if (!['GET', 'HEAD'].includes(method)) {
    body = await req.arrayBuffer();
  }

  let upstream: Response;
  try {
    const signal = AbortSignal.timeout(UPSTREAM_TIMEOUT_MS);
    upstream = await fetch(url, {
      method,
      headers,
      body: body && body.byteLength > 0 ? body : undefined,
      cache: 'no-store',
      signal,
    });
  } catch (err) {
    console.error('[eventix proxy] fetch falhou', { url, err });
    return NextResponse.json(upstreamErrorPayload(err), { status: 502 });
  }

  const out = new Headers();
  const pass = ['content-type', 'www-authenticate'];
  upstream.headers.forEach((v, k) => {
    if (pass.includes(k.toLowerCase())) out.set(k, v);
  });

  return new NextResponse(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: out,
  });
}

type RouteCtx = { params: Promise<{ path?: string[] }> };

async function segmentsOf(ctx: RouteCtx): Promise<string[]> {
  const p = await ctx.params;
  return p.path ?? [];
}

export async function GET(req: NextRequest, ctx: RouteCtx) {
  return proxy(req, await segmentsOf(ctx));
}

export async function POST(req: NextRequest, ctx: RouteCtx) {
  return proxy(req, await segmentsOf(ctx));
}

export async function PUT(req: NextRequest, ctx: RouteCtx) {
  return proxy(req, await segmentsOf(ctx));
}

export async function PATCH(req: NextRequest, ctx: RouteCtx) {
  return proxy(req, await segmentsOf(ctx));
}

export async function DELETE(req: NextRequest, ctx: RouteCtx) {
  return proxy(req, await segmentsOf(ctx));
}
