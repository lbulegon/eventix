'use client';

import { useEffect } from 'react';

/**
 * Regista o service worker em produção (PWA instalável).
 * Em dev o Next.js pode conflitar com o SW — mantemos só produção.
 */
export function PwaRegister() {
  useEffect(() => {
    if (process.env.NODE_ENV !== 'production') return;
    if (typeof window === 'undefined' || !('serviceWorker' in navigator)) return;

    const register = () => {
      navigator.serviceWorker
        .register('/sw.js', { scope: '/' })
        .catch(() => {
          /* ignorar falhas de registo */
        });
    };

    if (document.readyState === 'complete') register();
    else window.addEventListener('load', register, { once: true });
  }, []);

  return null;
}
