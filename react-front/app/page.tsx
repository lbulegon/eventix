'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getAccessToken } from '@/lib/api/storage';

/** Espelho do splash: envia para home ou login conforme token. */
export default function SplashPage() {
  const router = useRouter();

  useEffect(() => {
    const t = setTimeout(() => {
      if (getAccessToken()) {
        router.replace('/inicio');
      } else {
        router.replace('/login');
      }
    }, 600);
    return () => clearTimeout(t);
  }, [router]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#0D1117]">
      <p className="text-3xl font-bold tracking-tight text-white">Eventix</p>
      <p className="mt-2 text-sm text-[#B0B3B8]">A carregar…</p>
    </div>
  );
}
