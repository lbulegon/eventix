import Link from 'next/link';

export default function PreCadastroPage() {
  return (
    <div className="mx-auto max-w-md px-6 py-16 text-center text-[#EDEDED]">
      <h1 className="text-xl font-semibold">Criar conta</h1>
      <p className="mt-3 text-sm text-[#B0B3B8]">
        Pré-cadastro freelancer via API — interface web em breve (ver app mobile).
      </p>
      <Link href="/login" className="mt-6 inline-block text-[#6366F1] hover:underline">
        Voltar ao login
      </Link>
    </div>
  );
}
