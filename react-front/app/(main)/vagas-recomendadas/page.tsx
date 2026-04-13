'use client';

import { useCallback, useEffect, useState } from 'react';
import { SubpageHeader } from '@/components/eventix/SubpageHeader';
import { candidatarNaVaga, fetchVagasRecomendadas } from '@/lib/services/vagas';

export default function VagasRecomendadasPage() {
  const [list, setList] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setList(await fetchVagasRecomendadas(1));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function candidatar(id: number) {
    const r = await candidatarNaVaga(id);
    setToast(r.message);
    setTimeout(() => setToast(null), 3000);
    if (r.ok) load();
  }

  return (
    <div className="min-h-screen">
      <SubpageHeader title="Oportunidades e recomendações" />
      {toast && (
        <div className="mx-3 mt-2 rounded-lg bg-[#10B981]/20 px-3 py-2 text-center text-sm text-[#10B981]">{toast}</div>
      )}
      <div className="p-3">
        {loading && <p className="text-center text-[#B0B3B8]">A carregar…</p>}
        {!loading && !list.length && <p className="text-center text-[#B0B3B8]">Sem recomendações por agora</p>}
        <ul className="space-y-2">
          {list.map((v) => {
            const id = Number(v.id);
            return (
              <li key={id} className="rounded-lg border border-[#2C2F33] bg-[#161B22] p-4">
                <p className="font-semibold text-white">{String(v.titulo ?? 'Vaga')}</p>
                <button
                  type="button"
                  className="mt-3 w-full rounded-lg bg-[#6366F1] py-2 text-sm text-white"
                  onClick={() => candidatar(id)}
                >
                  Candidatar-se
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
