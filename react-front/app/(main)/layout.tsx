'use client';

import { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/lib/context/AuthContext';
import { BottomNav } from '@/components/eventix/BottomNav';

export default function MainAppLayout({ children }: { children: React.ReactNode }) {
  const { ready, isAuthenticated } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (ready && !isAuthenticated) {
      router.replace('/login');
    }
  }, [ready, isAuthenticated, router]);

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0D1117] text-[#B0B3B8]">
        A carregar…
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const tabRoots = ['/inicio', '/vagas', '/candidaturas', '/perfil'];
  const showNav = tabRoots.includes(pathname);

  return (
    <div className="flex min-h-screen flex-col bg-[#0D1117] text-[#EDEDED]">
      <main className={`flex-1 ${showNav ? 'pb-20' : ''}`}>{children}</main>
      <BottomNav />
    </div>
  );
}
