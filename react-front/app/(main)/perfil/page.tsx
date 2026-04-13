'use client';

import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '@/lib/context/AuthContext';
import { fetchFreelancerPerfil } from '@/lib/services/freelancers';

export default function PerfilPage() {
  const { user, displayName } = useAuth();
  const [perfil, setPerfil] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    const p = await fetchFreelancerPerfil();
    if (!p) setError('Erro ao carregar perfil');
    setPerfil(p);
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between bg-[#6366F1] px-4 py-3 text-white">
        <h1 className="text-lg font-semibold">Perfil</h1>
        <span className="text-sm opacity-80">✎</span>
      </header>

      <div className="flex-1 p-4">
        {loading && <p className="text-center text-[#B0B3B8]">A carregar…</p>}
        {error && (
          <div className="text-center">
            <p className="text-red-400">{error}</p>
            <button type="button" className="mt-3 text-[#6366F1]" onClick={() => load()}>
              Tentar novamente
            </button>
          </div>
        )}
        {!loading && !error && (
          <div className="space-y-3 rounded-lg border border-[#2C2F33] bg-[#161B22] p-4">
            <p>
              <span className="text-[#B0B3B8]">Nome: </span>
              <span className="text-white">{displayName}</span>
            </p>
            <p>
              <span className="text-[#B0B3B8]">E-mail: </span>
              <span className="text-white">{user?.email ?? '—'}</span>
            </p>
            <p>
              <span className="text-[#B0B3B8]">Tipo: </span>
              <span className="text-white">{user?.tipo_usuario ?? '—'}</span>
            </p>
            {perfil &&
              Object.entries(perfil)
                .filter(([k]) => !['id'].includes(k))
                .slice(0, 8)
                .map(([k, v]) => (
                  <p key={k} className="text-sm">
                    <span className="text-[#B0B3B8]">{k}: </span>
                    <span className="text-white">{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
                  </p>
                ))}
          </div>
        )}
      </div>
    </div>
  );
}
