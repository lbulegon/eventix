'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { useRouter } from 'next/navigation';
import { loginWithPassword, logoutClient } from '@/lib/api';
import { getAccessToken, getUserJson } from '@/lib/api/storage';
import { ApiError } from '@/lib/api/errors';
import type { LoginUser } from '@/lib/api/types';

type AuthContextValue = {
  ready: boolean;
  user: LoginUser | null;
  isAuthenticated: boolean;
  displayName: string;
  login: (email: string, password: string) => Promise<{ ok: true } | { ok: false; error: string }>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [user, setUser] = useState<LoginUser | null>(null);

  useEffect(() => {
    setUser(getUserJson<LoginUser>());
    setReady(true);
  }, []);

  const isAuthenticated = Boolean(ready && getAccessToken());

  const displayName = useMemo(() => {
    if (!user) return 'Usuário';
    return (
      (user as { nome_completo?: string }).nome_completo ||
      [user.first_name, user.last_name].filter(Boolean).join(' ').trim() ||
      user.username
    );
  }, [user]);

  const login = useCallback(async (email: string, password: string) => {
    try {
      const data = await loginWithPassword(email.trim(), password);
      setUser(data.user);
      return { ok: true as const };
    } catch (e) {
      if (e instanceof ApiError) {
        let m = e.message.trim();
        if (!m || m === '0') {
          m =
            e.status === 401 || e.status === 403
              ? 'E-mail ou senha incorretos.'
              : 'Não foi possível entrar. Tente novamente.';
        }
        return { ok: false as const, error: m };
      }
      if (e instanceof Error) {
        const m = e.message || '';
        if (/failed to fetch/i.test(m) || e instanceof TypeError) {
          return {
            ok: false as const,
            error:
              'Não foi possível ligar ao servidor. No Railway, use o proxy: defina EVENTIX_API_URL no serviço Next ou NEXT_PUBLIC_API_URL no build.',
          };
        }
        return {
          ok: false as const,
          error: m || 'Erro de rede. Tente novamente.',
        };
      }
      return {
        ok: false as const,
        error: 'Erro de rede. Tente novamente.',
      };
    }
  }, []);

  const logout = useCallback(async () => {
    await logoutClient();
    setUser(null);
    router.replace('/login');
  }, [router]);

  const value = useMemo<AuthContextValue>(
    () => ({
      ready,
      user,
      isAuthenticated,
      displayName,
      login,
      logout,
    }),
    [ready, user, isAuthenticated, displayName, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth deve ser usado dentro de AuthProvider');
  return ctx;
}
