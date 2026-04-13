'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/context/AuthContext';

function ActionCard({
  title,
  subtitle,
  href,
}: {
  title: string;
  subtitle: string;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="block rounded-lg border border-[#2C2F33] bg-[#161B22] p-4 text-center transition hover:border-[#6366F1]/50"
    >
      <p className="font-semibold text-white">{title}</p>
      <p className="mt-1 text-xs text-[#B0B3B8]">{subtitle}</p>
    </Link>
  );
}

export default function InicioPage() {
  const { displayName, logout } = useAuth();

  async function onLogout() {
    if (typeof window !== 'undefined' && window.confirm('Tem certeza que deseja sair?')) {
      await logout();
    }
  }

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between border-b border-[#2C2F33] bg-[#161B22] px-4 py-3">
        <h1 className="text-lg font-medium text-white">Eventix</h1>
        <div className="flex gap-1">
          <Link
            href="/notificacoes"
            className="rounded-lg p-2 text-white hover:bg-[#1E2228]"
            aria-label="Notificações"
          >
            🔔
          </Link>
          <button
            type="button"
            onClick={onLogout}
            className="rounded-lg p-2 text-white hover:bg-[#1E2228]"
            aria-label="Sair"
          >
            ⎋
          </button>
        </div>
      </header>

      <div className="flex-1 space-y-4 p-4">
        <div className="rounded-xl bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] p-5">
          <p className="text-2xl font-bold text-white">Olá, {displayName}!</p>
          <p className="mt-1 text-base text-white/90">Bem-vindo ao Eventix</p>
        </div>

        <ActionCard
          title="Oportunidades e recomendações"
          subtitle="Vagas escolhidas especialmente para você"
          href="/vagas-recomendadas"
        />

        <div className="grid grid-cols-2 gap-3">
          <ActionCard title="Todas as Vagas" subtitle="Buscar oportunidades" href="/vagas" />
          <ActionCard title="Minhas Candidaturas" subtitle="Acompanhe status" href="/candidaturas" />
        </div>

        <ActionCard title="Funções" subtitle="Configure suas especialidades" href="/funcoes" />
      </div>
    </div>
  );
}
