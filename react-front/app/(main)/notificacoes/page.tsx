'use client';

import { useCallback, useEffect, useState } from 'react';
import { SubpageHeader } from '@/components/eventix/SubpageHeader';
import { fetchNotificacoes, marcarNotificacaoLida } from '@/lib/services/notificacoes';

export default function NotificacoesPage() {
  const [list, setList] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setList(await fetchNotificacoes(1));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function marcar(id: number) {
    try {
      await marcarNotificacaoLida(id);
      load();
    } catch {
      /* ignore */
    }
  }

  return (
    <div className="min-h-screen">
      <SubpageHeader title="Notificações" />
      <div className="p-3">
        {loading && <p className="text-center text-[#B0B3B8]">A carregar…</p>}
        {!loading && !list.length && <p className="text-center text-[#B0B3B8]">Sem notificações</p>}
        <ul className="space-y-2">
          {list.map((n) => {
            const id = Number(n.id);
            return (
              <li key={id} className="rounded-lg border border-[#2C2F33] bg-[#161B22] p-3 text-sm text-white">
                <p>{String(n.mensagem ?? n.titulo ?? JSON.stringify(n))}</p>
                <button type="button" className="mt-2 text-xs text-[#6366F1]" onClick={() => marcar(id)}>
                  Marcar como lida
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
