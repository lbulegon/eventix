This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Eventix — integração com Django

O front chama o **backend Eventix (Django + DRF + SimpleJWT)** na URL definida por `NEXT_PUBLIC_API_URL`.

1. Copie o exemplo de variáveis: crie `.env.local` com o conteúdo de `.env.example`.
2. Ajuste `NEXT_PUBLIC_API_URL` (ex.: `http://127.0.0.1:8000` com `python manage.py runserver`).
3. No Django (`setup/settings.py`), inclua o origin do Next em `CORS_ALLOWED_ORIGINS` em produção (ex.: `https://teu-front.up.railway.app`).

### Autenticação (igual à app mobile)

| Método | Caminho | Notas |
|--------|---------|--------|
| `POST` | `/api/auth/login/` | Corpo JSON: `{ "username", "password" }`. Resposta: `{ user, tokens: { access, refresh } }`. |
| `POST` | `/api/auth/refresh/` | Corpo: `{ "refresh" }`. Resposta: `{ access }`. |

Módulo de cliente: `@/lib/api` — `loginWithPassword`, `logoutClient`, `apiGet`, `apiPost`, `apiFetch`. Tokens em `localStorage` (apenas browser).

Página de demonstração: [`/login`](http://localhost:3000/login).

### Paridade com o app mobile Flutter (`mobile/eventix`)

| Mobile (`lib/`) | Web (`react-front`) |
|-----------------|---------------------|
| Tema escuro + indigo `#6366F1` | `app/globals.css` + Tailwind nas páginas |
| `SplashScreen` → login ou home | `/` redireciona conforme token |
| `LoginPage` (e-mail → `username` na API) | `/login` + `AuthContext` |
| `HomePage` + bottom nav (Início, Vagas, Candidaturas, Perfil) | `(main)/layout` + `BottomNav.tsx` |
| Cartões início → recomendadas, vagas, candidaturas, funções | `/inicio` com links |
| `VagasPage`, `MinhasCandidaturasPage`, `PerfilPage`, etc. | Rotas `/vagas`, `/candidaturas`, `/perfil`, … |
| `AppConfig` endpoints | `lib/config/apiPaths.ts` + `lib/services/*` |

**Ainda não replicado** (como no mobile): Firebase Messaging/Crashlytics/Analytics, pré-cadastro completo, recuperação de senha, `dashboard_freelancer` dedicado, filtros avançados de vagas.

### PWA (Progressive Web App)

- `app/manifest.ts` — manifesto Web (nome, cores Eventix, `standalone`, ícones).
- `public/icon.svg` — ícone vetorial; `public/icon-192.png` e `public/icon-512.png` — PNG para instalação Android/Chrome (gerados a partir de `../assents/logo_sem_fundo.png`, fundo `#0d1117`).
- `public/sw.js` — service worker (precache mínimo; API noutro domínio não é cacheada).
- `components/PwaRegister.tsx` — regista o SW **apenas em produção** (`npm run build` + `npm run start` ou deploy HTTPS).

Para testar instalação: Chrome → menu **Instalar Eventix** (requer HTTPS no domínio real; em `localhost` também funciona após build de produção).

## Getting Started

```bash
npm install
npm run dev
```

Abra [http://localhost:3000](http://localhost:3000).

## Deploy (Railway / Nixpacks)

Requisito **Node ≥ 20** (ver `nixpacks.toml` e `engines` em `package.json`).

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
