import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

function targetBase(): string {
  const raw =
    process.env.EVENTIX_API_URL?.trim() ||
    process.env.NEXT_PUBLIC_API_URL?.trim() ||
    '';
  if (!raw) return '';
  const withProtocol = /^https?:\/\//i.test(raw) ? raw : `https://${raw}`;
  return withProtocol.replace(/\/$/, '');
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
    upstream = await fetch(url, {
      method,
      headers,
      body: body && body.byteLength > 0 ? body : undefined,
      cache: 'no-store',
    });
  } catch {
    return NextResponse.json(
      { detail: 'Não foi possível contactar o backend Eventix.' },
      { status: 502 },
    );
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
