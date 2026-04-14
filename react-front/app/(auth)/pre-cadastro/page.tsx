'use client';

import Link from 'next/link';
import { useState } from 'react';
import { ApiError } from '@/lib/api';
import { preCadastrarFreelancer } from '@/lib/services/freelancers';

function mensagemErroRede(error: unknown): string {
  if (error instanceof TypeError) {
    return (
      'Não foi possível contactar o servidor. Faça redeploy do serviço Next (versão com proxy /api/eventix). ' +
      'No Railway, no serviço do front, mantenha NEXT_PUBLIC_API_URL=https://… (URL do Django) — o servidor usa em runtime.'
    );
  }
  if (error instanceof Error && /failed to fetch/i.test(error.message)) {
    return mensagemErroRede(new TypeError('fetch'));
  }
  return '';
}

export default function PreCadastroPage() {
  const [nomeCompleto, setNomeCompleto] = useState('');
  const [email, setEmail] = useState('');
  const [telefone, setTelefone] = useState('');
  const [cpf, setCpf] = useState('');
  const [dataNascimento, setDataNascimento] = useState('');
  const [sexo, setSexo] = useState<'M' | 'F' | ''>('');
  const [habilidades, setHabilidades] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmarSenha, setConfirmarSenha] = useState('');
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [sucesso, setSucesso] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setSucesso(null);

    if (!nomeCompleto.trim() || !email.trim() || !telefone.trim() || !cpf.trim()) {
      setErro('Preencha os campos obrigatórios.');
      return;
    }
    if (senha.length < 8) {
      setErro('A senha deve ter pelo menos 8 caracteres.');
      return;
    }
    if (senha !== confirmarSenha) {
      setErro('As senhas não coincidem.');
      return;
    }

    setLoading(true);
    try {
      const message = await preCadastrarFreelancer({
        nome_completo: nomeCompleto.trim(),
        email: email.trim(),
        telefone: telefone.trim(),
        cpf: cpf.trim(),
        password: senha,
        data_nascimento: dataNascimento.trim() || undefined,
        sexo: sexo || undefined,
        habilidades: habilidades.trim() || undefined,
      });
      setSucesso(message);
      setNomeCompleto('');
      setEmail('');
      setTelefone('');
      setCpf('');
      setDataNascimento('');
      setSexo('');
      setHabilidades('');
      setSenha('');
      setConfirmarSenha('');
    } catch (error: unknown) {
      if (error instanceof ApiError) {
        setErro(error.message || 'Não foi possível concluir o pré-cadastro.');
      } else {
        const rede = mensagemErroRede(error);
        if (rede) {
          setErro(rede);
        } else if (error instanceof Error) {
          setErro(error.message || 'Erro de conexão. Tente novamente.');
        } else {
          setErro('Erro de conexão. Tente novamente.');
        }
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 py-10 text-[#EDEDED]">
      <h1 className="text-center text-3xl font-bold text-white">Criar conta</h1>
      <p className="mt-2 text-center text-sm text-[#B0B3B8]">
        Pré-cadastro freelancer
      </p>

      <form onSubmit={onSubmit} className="mt-8 space-y-3">
        {erro ? (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-center text-sm text-red-300">
            {erro}
          </div>
        ) : null}
        {sucesso ? (
          <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-center text-sm text-emerald-300">
            {sucesso}
          </div>
        ) : null}

        <input
          className="w-full rounded-lg border border-[#343A40] bg-[#1E2228] px-3 py-2.5 text-white outline-none ring-[#6366F1] focus:ring-2"
          placeholder="Nome completo *"
          value={nomeCompleto}
          onChange={(e) => setNomeCompleto(e.target.value)}
        />
        <input
          type="email"
          className="w-full rounded-lg border border-[#343A40] bg-[#1E2228] px-3 py-2.5 text-white outline-none ring-[#6366F1] focus:ring-2"
          placeholder="E-mail *"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          className="w-full rounded-lg border border-[#343A40] bg-[#1E2228] px-3 py-2.5 text-white outline-none ring-[#6366F1] focus:ring-2"
          placeholder="Telefone *"
          value={telefone}
          onChange={(e) => setTelefone(e.target.value)}
        />
        <input
          className="w-full rounded-lg border border-[#343A40] bg-[#1E2228] px-3 py-2.5 text-white outline-none ring-[#6366F1] focus:ring-2"
          placeholder="CPF *"
          value={cpf}
          onChange={(e) => setCpf(e.target.value)}
        />
        <input
          type="date"
          className="w-full rounded-lg border border-[#343A40] bg-[#1E2228] px-3 py-2.5 text-white outline-none ring-[#6366F1] focus:ring-2"
          value={dataNascimento}
          onChange={(e) => setDataNascimento(e.target.value)}
        />
        <select
          className="w-full rounded-lg border border-[#343A40] bg-[#1E2228] px-3 py-2.5 text-white outline-none ring-[#6366F1] focus:ring-2"
          value={sexo}
          onChange={(e) => setSexo(e.target.value as 'M' | 'F' | '')}
        >
          <option value="">Sexo (opcional)</option>
          <option value="M">Masculino</option>
          <option value="F">Feminino</option>
        </select>
        <textarea
          className="w-full rounded-lg border border-[#343A40] bg-[#1E2228] px-3 py-2.5 text-white outline-none ring-[#6366F1] focus:ring-2"
          placeholder="Habilidades (opcional)"
          value={habilidades}
          onChange={(e) => setHabilidades(e.target.value)}
        />
        <input
          type="password"
          className="w-full rounded-lg border border-[#343A40] bg-[#1E2228] px-3 py-2.5 text-white outline-none ring-[#6366F1] focus:ring-2"
          placeholder="Senha *"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
        />
        <input
          type="password"
          className="w-full rounded-lg border border-[#343A40] bg-[#1E2228] px-3 py-2.5 text-white outline-none ring-[#6366F1] focus:ring-2"
          placeholder="Confirmar senha *"
          value={confirmarSenha}
          onChange={(e) => setConfirmarSenha(e.target.value)}
        />

        <button
          type="submit"
          disabled={loading}
          className="mt-2 flex h-12 w-full items-center justify-center rounded-lg bg-[#6366F1] font-medium text-white hover:bg-[#4F46E5] disabled:opacity-60"
        >
          {loading ? 'Aguarde…' : 'Criar conta'}
        </button>
      </form>

      <Link href="/login" className="mt-5 text-center text-sm text-[#6366F1] hover:underline">
        Voltar ao login
      </Link>
    </div>
  );
}
