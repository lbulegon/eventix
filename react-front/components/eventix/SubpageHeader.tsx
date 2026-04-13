import Link from 'next/link';

export function SubpageHeader({ title }: { title: string }) {
  return (
    <header className="sticky top-0 z-40 flex items-center gap-3 border-b border-[#2C2F33] bg-[#161B22] px-3 py-3">
      <Link
        href="/inicio"
        className="rounded-lg px-2 py-1 text-sm text-[#B0B3B8] hover:bg-[#1E2228] hover:text-white"
      >
        ←
      </Link>
      <h1 className="text-lg font-semibold text-white">{title}</h1>
    </header>
  );
}
