'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/context/AuthContext';

export default function LoginPage() {
  const router = useRouter();
  const { login, ready, isAuthenticated } = useAuth();

  useEffect(() => {
    if (ready && isAuthenticated) router.replace('/inicio');
  }, [ready, isAuthenticated, router]);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!email.trim() || !password) {
      setError('Preencha e-mail e senha.');
      return;
    }
    if (password.length < 6) {
      setError('Senha deve ter pelo menos 6 caracteres.');
      return;
    }
    setLoading(true);
    const res = await login(email, password);
    setLoading(false);
    if (res.ok) {
      router.replace('/inicio');
    } else {
      const raw = res.error;
      const msg = typeof raw === 'string' ? raw.trim() : '';
      // Evita exibir só "0" (resposta estranha / bug de parsing)
      setError(
        msg && msg !== '0'
          ? msg
          : 'Não foi possível entrar. Verifique e-mail e senha.',
      );
    }
  }

  return (
    <div className="min-h-screen bg-[#0D1117]">
      <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 py-12">
        <h1 className="text-center text-3xl font-bold text-white">Eventix</h1>
        <p className="mt-2 text-center text-base text-[#B0B3B8]">Entre na sua conta</p>

        <form onSubmit={onSubmit} className="mt-8 space-y-4">
          {error != null && error !== '' ? (
            <div
              className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-center text-sm text-red-300"
              role="alert"
            >
              {error}
            </div>
          ) : null}

          <div>
            <label htmlFor="email" className="mb-1 block text-sm text-[#B0B3B8]">
              E-mail
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="username"
              className="w-full rounded-lg border border-[#343A40] bg-[#1E2228] px-3 py-2.5 text-white outline-none ring-[#6366F1] focus:ring-2"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-sm text-[#B0B3B8]">
              Senha
            </label>
            <div className="relative">
              <input
                id="password"
                name="password"
                type={showPass ? 'password' : 'text'}
                autoComplete="current-password"
                className="w-full rounded-lg border border-[#343A40] bg-[#1E2228] px-3 py-2.5 pr-10 text-white outline-none ring-[#6366F1] focus:ring-2"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-[#B0B3B8] hover:text-white"
                onClick={() => setShowPass(!showPass)}
              >
                {showPass ? 'mostrar' : 'ocultar'}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-2 flex h-12 w-full items-center justify-center rounded-lg bg-[#6366F1] font-medium text-white hover:bg-[#4F46E5] disabled:opacity-60"
          >
            {loading ? '…' : 'Entrar'}
          </button>
        </form>

        <div className="mt-4 flex justify-between text-sm">
          <Link href="/recuperar-senha" className="text-[#6366F1] hover:underline">
            Esqueci minha senha
          </Link>
          <Link href="/pre-cadastro" className="text-[#6366F1] hover:underline">
            Criar conta
          </Link>
        </div>
      </div>
    </div>
  );
}
