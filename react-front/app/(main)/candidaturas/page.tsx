'use client';

import { useCallback, useEffect, useState } from 'react';
import { cancelarCandidatura, fetchMinhasCandidaturas } from '@/lib/services/vagas';

function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message.trim()) return error.message;
  return fallback;
}

function statusLabel(s: string) {
  switch (s) {
    case 'pendente':
      return 'Pendente';
    case 'aprovada':
      return 'Aprovada';
    case 'rejeitada':
      return 'Rejeitada';
    case 'cancelada':
      return 'Cancelada';
    default:
      return s || '—';
  }
}

function statusClass(s: string) {
  switch (s) {
    case 'pendente':
      return 'bg-amber-500/20 text-amber-300';
    case 'aprovada':
      return 'bg-emerald-500/20 text-emerald-300';
    case 'rejeitada':
      return 'bg-red-500/20 text-red-300';
    case 'cancelada':
      return 'bg-zinc-500/20 text-zinc-400';
    default:
      return 'bg-zinc-500/20 text-zinc-400';
  }
}

export default function CandidaturasPage() {
  const [list, setList] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setList(await fetchMinhasCandidaturas());
    } catch (error: unknown) {
      setError(getErrorMessage(error, 'Erro ao carregar candidaturas'));
      setList([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function cancelar(id: number) {
    const r = await cancelarCandidatura(id);
    setToast(r.message);
    setTimeout(() => setToast(null), 3000);
    if (r.ok) load();
  }

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between bg-[#6366F1] px-4 py-3 text-white">
        <h1 className="text-lg font-semibold">Minhas Candidaturas</h1>
        <button type="button" className="rounded p-2 hover:bg-white/10" onClick={() => load()}>
          ↻
        </button>
      </header>

      {toast && (
        <div className="mx-3 mt-2 rounded-lg bg-[#10B981]/20 px-3 py-2 text-center text-sm text-[#10B981]">{toast}</div>
      )}

      <div className="flex-1 p-3">
        {loading && <p className="p-8 text-center text-[#B0B3B8]">A carregar…</p>}
        {error && (
          <div className="p-8 text-center">
            <p className="text-red-400">{error}</p>
            <button type="button" className="mt-3 text-[#6366F1]" onClick={() => load()}>
              Tentar novamente
            </button>
          </div>
        )}
        {!loading && !error && !list.length && (
          <p className="p-8 text-center text-[#B0B3B8]">Nenhuma candidatura</p>
        )}
        <ul className="space-y-3">
          {list.map((c) => {
            const id = Number(c.id);
            const status = String(c.status ?? '');
            const vaga = c.vaga as Record<string, unknown> | undefined;
            const titulo = vaga?.titulo != null ? String(vaga.titulo) : `Candidatura #${id}`;
            return (
              <li key={id} className="rounded-lg border border-[#2C2F33] bg-[#161B22] p-4">
                <div className="flex items-start justify-between gap-2">
                  <p className="font-medium text-white">{titulo}</p>
                  <span className={`shrink-0 rounded px-2 py-0.5 text-xs ${statusClass(status)}`}>
                    {statusLabel(status)}
                  </span>
                </div>
                {status === 'pendente' && (
                  <button
                    type="button"
                    className="mt-3 w-full rounded-lg border border-red-500/40 py-2 text-sm text-red-300 hover:bg-red-500/10"
                    onClick={() => cancelar(id)}
                  >
                    Cancelar candidatura
                  </button>
                )}
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
