'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const tabs = [
  { href: '/inicio', label: 'Início', icon: '🏠' },
  { href: '/vagas', label: 'Vagas', icon: '💼' },
  { href: '/candidaturas', label: 'Candidaturas', icon: '📋' },
  { href: '/perfil', label: 'Perfil', icon: '👤' },
] as const;

export function BottomNav() {
  const pathname = usePathname();
  if (!tabs.some((t) => t.href === pathname)) return null;

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 border-t border-[#2C2F33] bg-[#161B22]"
      aria-label="Navegação principal"
    >
      <div className="mx-auto flex max-w-lg justify-around safe-area-pb">
        {tabs.map(({ href, label, icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex flex-1 flex-col items-center gap-0.5 py-2 text-xs ${
                active ? 'text-[#6366F1]' : 'text-[#6C757D]'
              }`}
            >
              <span className="text-lg leading-none" aria-hidden>
                {icon}
              </span>
              {label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
