import Link from 'next/link';

export default function RecuperarSenhaPage() {
  return (
    <div className="mx-auto max-w-md px-6 py-16 text-center text-[#EDEDED]">
      <h1 className="text-xl font-semibold">Recuperar senha</h1>
      <p className="mt-3 text-sm text-[#B0B3B8]">
        Fluxo completo em breve. No mobile usa a API de password reset do Eventix.
      </p>
      <Link href="/login" className="mt-6 inline-block text-[#6366F1] hover:underline">
        Voltar ao login
      </Link>
    </div>
  );
}
