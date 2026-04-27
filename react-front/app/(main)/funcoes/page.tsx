'use client';

import { useCallback, useEffect, useState } from 'react';
import { SubpageHeader } from '@/components/eventix/SubpageHeader';
import { adicionarFuncao, fetchFuncoesDisponiveis, fetchMinhasFuncoes } from '@/lib/services/funcoes';

export default function FuncoesPage() {
  const [disponiveis, setDisponiveis] = useState<Record<string, unknown>[]>([]);
  const [minhas, setMinhas] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [d, m] = await Promise.all([fetchFuncoesDisponiveis(), fetchMinhasFuncoes()]);
      setDisponiveis(d);
      setMinhas(m);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const minhasIds = new Set(
    minhas
      .map((x) => {
        const o = x as Record<string, unknown>;
        if (o.funcao_id != null) return Number(o.funcao_id);
        const f = o.funcao as Record<string, unknown> | undefined;
        return f?.id != null ? Number(f.id) : NaN;
      })
      .filter((n) => !Number.isNaN(n)),
  );

  async function add(id: number) {
    const r = await adicionarFuncao(id);
    setToast(r.message);
    setTimeout(() => setToast(null), 3000);
    if (r.ok) load();
  }

  return (
    <div className="min-h-screen">
      <SubpageHeader title="Funções" />
      {toast && (
        <div className="mx-3 mt-2 rounded-lg bg-[#6366F1]/20 px-3 py-2 text-center text-sm text-[#A5B4FC]">{toast}</div>
      )}
      <div className="space-y-6 p-3">
        <section>
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-[#B0B3B8]">Minhas funções</h2>
          {loading ? (
            <p className="text-[#B0B3B8]">A carregar…</p>
          ) : minhas.length === 0 ? (
            <p className="text-sm text-[#B0B3B8]">Nenhuma função registada</p>
          ) : (
            <ul className="space-y-2">
              {minhas.map((f, i) => {
                const o = f as Record<string, unknown>;
                const fn = (o.funcao as Record<string, unknown> | undefined)?.nome;
                const label = fn != null ? String(fn) : `Função ${i + 1}`;
                return (
                  <li key={i} className="rounded-lg border border-[#2C2F33] bg-[#161B22] px-3 py-2 text-sm text-white">
                    {label}
                  </li>
                );
              })}
            </ul>
          )}
        </section>
        <section>
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-[#B0B3B8]">Disponíveis para adicionar</h2>
          <ul className="space-y-2">
            {disponiveis
              .filter((f) => !minhasIds.has(Number(f.id)))
              .map((f) => {
              const id = Number(f.id);
              const nome = String(f.nome ?? id);
              return (
                <li
                  key={id}
                  className="flex items-center justify-between gap-2 rounded-lg border border-[#2C2F33] bg-[#161B22] px-3 py-2"
                >
                  <span className="text-white">{nome}</span>
                  <button
                    type="button"
                    disabled={loading}
                    className="shrink-0 rounded bg-[#6366F1] px-3 py-1 text-xs text-white disabled:opacity-40"
                    onClick={() => add(id)}
                  >
                    Adicionar
                  </button>
                </li>
              );
            })}
          </ul>
        </section>
      </div>
    </div>
  );
}
