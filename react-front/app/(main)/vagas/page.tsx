'use client';

import { useCallback, useEffect, useState } from 'react';
import { fetchVagas, candidatarNaVaga } from '@/lib/services/vagas';

function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message.trim()) return error.message;
  return fallback;
}

export default function VagasPage() {
  const [list, setList] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState<string | undefined>(undefined);
  const [page, setPage] = useState(1);
  const [toast, setToast] = useState<string | null>(null);

  const load = useCallback(async (p: number, q?: string, append = false) => {
    setLoading(true);
    setError(null);
    try {
      const { results } = await fetchVagas({ page: p, search: q });
      setList((prev) => (append ? [...prev, ...results] : results));
      setPage(p);
    } catch (error: unknown) {
      setError(getErrorMessage(error, 'Erro ao carregar vagas'));
      if (!append) setList([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(1, search, false);
  }, [load, search]);

  async function candidatar(id: number) {
    const r = await candidatarNaVaga(id);
    setToast(r.message);
    setTimeout(() => setToast(null), 3000);
    if (r.ok) load(1, search, false);
  }

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between bg-[#6366F1] px-4 py-3 text-white">
        <h1 className="text-lg font-semibold">Vagas Disponíveis</h1>
        <button type="button" className="rounded p-2 hover:bg-white/10" onClick={() => load(1, search, false)}>
          ↻
        </button>
      </header>

      <form
        className="border-b border-[#2C2F33] p-3"
        onSubmit={(e) => {
          e.preventDefault();
          const q = searchInput.trim() || undefined;
          setSearch(q);
        }}
      >
        <input
          placeholder="Buscar vagas..."
          className="w-full rounded-lg border border-[#343A40] bg-[#1E2228] px-3 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-[#6366F1]"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
      </form>

      {toast && (
        <div className="mx-3 mt-2 rounded-lg bg-[#10B981]/20 px-3 py-2 text-center text-sm text-[#10B981]">{toast}</div>
      )}

      <div className="flex-1 p-2">
        {loading && list.length === 0 && <p className="p-8 text-center text-[#B0B3B8]">A carregar…</p>}
        {error && !list.length && (
          <div className="p-8 text-center">
            <p className="text-red-400">{error}</p>
            <button type="button" className="mt-3 text-[#6366F1]" onClick={() => load(1, search, false)}>
              Tentar novamente
            </button>
          </div>
        )}
        {!loading && !error && !list.length && (
          <p className="p-8 text-center text-[#B0B3B8]">Nenhuma vaga disponível</p>
        )}
        <ul className="space-y-2">
          {list.map((v) => {
            const id = Number(v.id);
            const titulo = String(v.titulo ?? 'Vaga');
            const eventoNome = v.evento_nome != null ? String(v.evento_nome) : null;
            const rem = v.remuneracao != null ? String(v.remuneracao) : null;
            return (
              <li key={`${id}-${titulo}`} className="rounded-lg border border-[#2C2F33] bg-[#161B22] p-4">
                <p className="font-semibold text-white">{titulo}</p>
                {eventoNome && <p className="mt-1 text-sm text-[#B0B3B8]">{eventoNome}</p>}
                {rem && <p className="text-sm text-[#6366F1]">R$ {rem}</p>}
                <button
                  type="button"
                  className="mt-3 w-full rounded-lg bg-[#6366F1] py-2 text-sm font-medium text-white hover:bg-[#4F46E5]"
                  onClick={() => candidatar(id)}
                >
                  Candidatar-se
                </button>
              </li>
            );
          })}
        </ul>
        {list.length > 0 && (
          <button
            type="button"
            className="mt-4 w-full py-2 text-sm text-[#6366F1]"
            onClick={() => load(page + 1, search, true)}
          >
            Carregar mais
          </button>
        )}
      </div>
    </div>
  );
}
