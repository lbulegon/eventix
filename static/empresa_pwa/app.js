const CONFIG = window.EVENTIX_PWA_CONFIG || {};

const API_BASE = '/api/v1';
const ENDPOINTS = {
  login: '/auth/login/',
  refresh: '/auth/refresh/',
  logout: '/auth/logout/',
  profile: '/users/profile/',
  empresa: '/empresas/',
  eventos: '/eventos/',
  vagas: '/vagas/',
  candidaturas: '/candidaturas/',
  financeiro: '/financeiro/',
};

const STORAGE_KEYS = {
  auth: 'eventix:emp:pwa:auth',
  installDismissed: 'eventix:emp:pwa:install-dismissed',
};

const state = {
  tokens: null,
  user: null,
  profile: null,
  empresa: null,
  eventos: null,
  vagas: null,
  candidaturas: null,
  financeiro: null,
  loading: false,
};

let currentPath = '/';

const titleEl = document.getElementById('app-title');
const backBtn = document.getElementById('backBtn');
const refreshBtn = document.getElementById('refreshBtn');
const authBtn = document.getElementById('authBtn');
const loginModal = document.getElementById('loginModal');
const loginForm = document.getElementById('loginForm');
const loginEmail = document.getElementById('loginEmail');
const loginPassword = document.getElementById('loginPassword');
const loginCancel = document.getElementById('loginCancel');
const closeLoginModalBtn = document.getElementById('closeLoginModal');
const banner = document.getElementById('installBanner');
const btnInstall = document.getElementById('installBtn');
const btnDismiss = document.getElementById('dismissInstall');
const toastContainer = document.getElementById('toastContainer');

const ROUTES_REQUIRING_AUTH = ['/eventos', '/vagas', '/candidaturas', '/financeiro'];
const LOADER_HTML = '<div class="loader" role="status" aria-label="Carregando"></div>';
const STATUS_LABELS = {
  pendente: 'Pendente',
  em_analise: 'Em análise',
  aprovada: 'Aprovada',
  aprovado: 'Aprovada',
  rejeitada: 'Rejeitada',
  rejeitado: 'Rejeitada',
  cancelado: 'Cancelada',
  contratado: 'Contratada',
};

function loadAuthFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEYS.auth);
    if (!raw) return;
    const parsed = JSON.parse(raw);
    if (parsed?.tokens?.access) {
      state.tokens = parsed.tokens;
      state.user = parsed.user || null;
    }
  } catch (error) {
    console.warn('[Eventix Empresa PWA] Falha ao carregar auth localStorage', error);
  }
}

function saveAuthToStorage() {
  if (!state.tokens) {
    localStorage.removeItem(STORAGE_KEYS.auth);
    return;
  }
  const payload = {
    tokens: state.tokens,
    user: state.user,
  };
  localStorage.setItem(STORAGE_KEYS.auth, JSON.stringify(payload));
}

function clearAuth() {
  state.tokens = null;
  state.user = null;
  state.profile = null;
  state.empresa = null;
  updateAuthUI();
  saveAuthToStorage();
}

function isAuthenticated() {
  return Boolean(state.tokens?.access);
}

function setTitle(t) {
  if (titleEl) titleEl.textContent = t;
}

function setBack(show) {
  if (backBtn) backBtn.hidden = !show;
}

function setActiveTab(path) {
  document.querySelectorAll('.nav-item').forEach((item) => {
    item.classList.toggle('active', item.dataset.path === path);
  });
}

function showToast(message, type = 'info') {
  if (!toastContainer) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
    <span>${message}</span>
  `;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 4000);
}

function openLoginModal() {
  if (loginModal) loginModal.classList.remove('hidden');
}

function closeLoginModal() {
  if (loginModal) loginModal.classList.add('hidden');
}

function updateAuthUI() {
  if (authBtn) {
    authBtn.setAttribute('aria-label', isAuthenticated() ? 'Sair' : 'Entrar');
    authBtn.onclick = isAuthenticated() ? handleLogout : openLoginModal;
  }
}

async function refreshAccessToken() {
  if (!state.tokens?.refresh) return false;
  try {
    const payload = await apiFetch(ENDPOINTS.refresh, {
      method: 'POST',
      body: JSON.stringify({ refresh: state.tokens.refresh }),
    }, { skipAuth: true });
    state.tokens.access = payload.access;
    saveAuthToStorage();
    return true;
  } catch (error) {
    clearAuth();
    return false;
  }
}

async function apiFetch(endpoint, options = {}, { skipAuth = false } = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = new Headers({
    'Content-Type': 'application/json',
    ...options.headers,
  });
  if (state.tokens?.access && !skipAuth) {
    headers.set('Authorization', `Bearer ${state.tokens.access}`);
  }
  const fetchOptions = {
    ...options,
    headers,
  };
  let response = await fetch(url, fetchOptions);
  if (response.status === 401 && !skipAuth) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      headers.set('Authorization', `Bearer ${state.tokens.access}`);
      response = await fetch(url, fetchOptions);
    }
  }
  if (response.status === 204) return null;
  const text = await response.text();
  let payload;
  try {
    payload = text ? JSON.parse(text) : null;
  } catch (error) {
    payload = text;
  }
  if (!response.ok) {
    const error = new Error(payload?.error || payload?.detail || 'Erro na requisição');
    error.payload = payload;
    error.status = response.status;
    throw error;
  }
  return payload;
}

async function handleLoginSubmit(event) {
  event.preventDefault();
  if (!loginEmail || !loginPassword) return;
  const email = loginEmail.value.trim();
  const password = loginPassword.value;
  if (!email || !password) {
    showToast('Informe email e senha.', 'error');
    return;
  }
  try {
    const payload = await apiFetch(ENDPOINTS.login, {
      method: 'POST',
      body: JSON.stringify({ username: email, password }),
    }, { skipAuth: true });

    state.tokens = {
      access: payload.tokens?.access,
      refresh: payload.tokens?.refresh,
    };
    state.user = payload.user;
    saveAuthToStorage();
    updateAuthUI();
    closeLoginModal();
    showToast(`Bem-vindo(a), ${payload.user?.nome_completo || payload.user?.username || 'empresa'}!`, 'success');
    await hydrateAuthenticatedData(true);
    renderRoute(currentPath, { force: true });
  } catch (error) {
    console.error('[Eventix Empresa PWA] Falha no login', error);
    showToast('Login inválido. Verifique suas credenciais.', 'error');
  }
}

async function handleLogout() {
  try {
    if (state.tokens?.access) {
      await apiFetch(ENDPOINTS.logout, { method: 'POST' });
    }
  } catch (error) {
    console.warn('[Eventix Empresa PWA] Erro ao fazer logout', error);
  } finally {
    clearAuth();
    renderRoute('/', { force: true });
    openLoginModal();
    showToast('Você saiu da sua conta.', 'success');
  }
}

function requiresAuth(path) {
  return ROUTES_REQUIRING_AUTH.some((prefix) => path.startsWith(prefix));
}

async function hydrateAuthenticatedData(force = false) {
  if (!isAuthenticated()) return;
  try {
    await Promise.all([
      ensureUserProfile(force),
      ensureEmpresaProfile(force),
    ]);
  } catch (error) {
    console.error('[Eventix Empresa PWA] Erro ao carregar dados iniciais', error);
  }
}

async function ensureUserProfile(force = false) {
  if (!isAuthenticated()) return null;
  if (state.profile && !force) return state.profile;
  try {
    const data = await apiFetch(ENDPOINTS.profile);
    state.profile = data?.usuario || data || null;
    if (data?.usuario) {
      state.user = {
        ...(state.user || {}),
        ...data.usuario,
      };
      saveAuthToStorage();
    }
    return state.profile;
  } catch (error) {
    console.warn('[Eventix Empresa PWA] Erro ao carregar perfil', error);
    return null;
  }
}

async function ensureEmpresaProfile(force = false) {
  if (!isAuthenticated()) return null;
  if (state.empresa && !force) return state.empresa;
  try {
    const data = await apiFetch(ENDPOINTS.empresa);
    const items = Array.isArray(data) ? data : data?.results || [];
    state.empresa = items[0] || null;
    return state.empresa;
  } catch (error) {
    console.warn('[Eventix Empresa PWA] Erro ao carregar empresa', error);
    return null;
  }
}

async function ensureEventos(force = false) {
  if (!isAuthenticated()) return null;
  if (state.eventos && !force) return state.eventos;
  try {
    const data = await apiFetch(`${ENDPOINTS.eventos}?page=1`);
    const items = Array.isArray(data) ? data : data?.results || [];
    state.eventos = {
      items,
      count: data?.count ?? items.length,
    };
    return state.eventos;
  } catch (error) {
    console.warn('[Eventix Empresa PWA] Erro ao carregar eventos', error);
    return null;
  }
}

async function ensureVagas(force = false) {
  if (!isAuthenticated()) return null;
  if (state.vagas && !force) return state.vagas;
  try {
    const data = await apiFetch(`${ENDPOINTS.vagas}?page=1`);
    const items = Array.isArray(data) ? data : data?.results || [];
    state.vagas = {
      items,
      count: data?.count ?? items.length,
    };
    return state.vagas;
  } catch (error) {
    console.warn('[Eventix Empresa PWA] Erro ao carregar vagas', error);
    return null;
  }
}

async function ensureCandidaturas(force = false) {
  if (!isAuthenticated()) return null;
  if (state.candidaturas && !force) return state.candidaturas;
  try {
    const data = await apiFetch(`${ENDPOINTS.candidaturas}?page=1`);
    const items = Array.isArray(data) ? data : data?.results || [];
    state.candidaturas = {
      items,
      count: data?.count ?? items.length,
    };
    return state.candidaturas;
  } catch (error) {
    console.warn('[Eventix Empresa PWA] Erro ao carregar candidaturas', error);
    return null;
  }
}

function safeGet(object, path, fallback = '') {
  return path.split('.').reduce((acc, key) => (acc && acc[key] !== undefined ? acc[key] : undefined), object) ?? fallback;
}

function formatCurrencyBRL(value) {
  const number = Number(value ?? 0);
  return number.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
  });
}

function renderGuestHome() {
  return `
    <div class="card" style="background:linear-gradient(135deg,#0EA5E9,#38BDF8);color:#fff;">
      <div class="title-lg">Olá!</div>
      <p class="subtitle" style="color:rgba(255,255,255,.85)">Entre na sua conta para acessar a gestão da empresa.</p>
      <div class="row" style="justify-content:flex-start;margin-top:16px;gap:12px;">
        <button class="btn btn-light" onclick="window.openLoginModal?.()">Entrar</button>
      </div>
    </div>
    <div class="card" style="margin-top:16px;">
      <div class="title-lg">Nova experiência PWA</div>
      <p class="subtitle">Instale o Eventix Empresa para acessar sua gestão com rapidez.</p>
    </div>
  `;
}

function buildHomeHTML() {
  const empresa = state.empresa || {};
  const nomeEmpresa = empresa.nome_fantasia || 'Empresa';
  const eventos = state.eventos?.items || [];
  const vagas = state.vagas?.items || [];
  const candidaturas = state.candidaturas?.items || [];
  
  const totalEventos = eventos.length;
  const eventosAtivos = eventos.filter((e) => e.ativo).length;
  const totalVagas = vagas.length;
  const vagasAtivas = vagas.filter((v) => v.ativa).length;
  const totalCandidaturas = candidaturas.length;
  const candidaturasPendentes = candidaturas.filter((c) => c.status === 'pendente').length;
  
  const quickActions = [
    { title: 'Eventos', subtitle: 'Gerenciar eventos', path: '/eventos', icon: '<svg viewBox="0 0 24 24" width="22" height="22"><path fill="currentColor" d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20a2 2 0 0 0 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zm0-12H5V6h14v2z"/></svg>' },
    { title: 'Vagas', subtitle: 'Gerenciar vagas', path: '/vagas', icon: '<svg viewBox="0 0 24 24" width="22" height="22"><path fill="currentColor" d="M14 6V4H6v2H2v14h20V6h-8zM6 8h12v10H6V8z"/></svg>' },
    { title: 'Candidaturas', subtitle: 'Revisar candidaturas', path: '/candidaturas', icon: '<svg viewBox="0 0 24 24" width="22" height="22"><path fill="currentColor" d="M19 3H5a2 2 0 0 0-2 2v16l4-4h12a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z"/></svg>' },
    { title: 'Financeiro', subtitle: 'Gestão financeira', path: '/financeiro', icon: '<svg viewBox="0 0 24 24" width="22" height="22"><path fill="currentColor" d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>' },
  ];
  
  const quickGrid = quickActions
    .map(
      (action) => `
        <article class="quick-card" data-path="${action.path}">
          <div class="quick-icon">${action.icon}</div>
          <div>
            <h3>${action.title}</h3>
            <p>${action.subtitle}</p>
          </div>
          <span class="quick-arrow">➜</span>
        </article>
      `,
    )
    .join('');
  
  const statsGrid = `
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Eventos</div>
        <div class="stat-number">${totalEventos}</div>
        <div class="stat-label" style="font-size:11px;">${eventosAtivos} ativos</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Vagas</div>
        <div class="stat-number">${totalVagas}</div>
        <div class="stat-label" style="font-size:11px;">${vagasAtivas} ativas</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Candidaturas</div>
        <div class="stat-number">${totalCandidaturas}</div>
        <div class="stat-label" style="font-size:11px;">${candidaturasPendentes} pendentes</div>
      </div>
    </div>
  `;
  
  return `
    <div class="hero-card">
      <div class="hero-title">Bem-vindo, ${nomeEmpresa}</div>
      <p class="hero-subtitle">Gerencie seus eventos, vagas e candidaturas.</p>
    </div>
    ${statsGrid}
    <section class="quick-grid">${quickGrid}</section>
  `;
}

function buildGuestAuthHTML(path) {
  return `
    <div class="empty-state">
      <svg viewBox="0 0 24 24" width="48" height="48" aria-hidden="true"><path fill="currentColor" d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5zm-9 9v-1a7 7 0 0 1 7-7h4a7 7 0 0 1 7 7v1z" /></svg>
      <p>Entre para acessar ${path.startsWith('/eventos') ? 'os eventos' : path.startsWith('/vagas') ? 'as vagas' : path.startsWith('/candidaturas') ? 'as candidaturas' : 'este conteúdo'}.</p>
      <button class="btn" onclick="window.openLoginModal?.()">Fazer login</button>
    </div>
  `;
}

async function renderHome(force = false) {
  setTitle('Eventix Empresa');
  setBack(false);
  const app = document.getElementById('app');
  if (!isAuthenticated()) {
    app.innerHTML = renderGuestHome();
    if (loginModal?.classList.contains('hidden')) {
      openLoginModal();
    }
    return;
  }
  app.innerHTML = LOADER_HTML;
  await Promise.all([
    ensureUserProfile(force),
    ensureEmpresaProfile(force),
    ensureEventos(force),
    ensureVagas(force),
    ensureCandidaturas(force),
  ]);
  app.innerHTML = buildHomeHTML();
  bindHomeEvents(app);
}

async function renderEventos(force = false) {
  setTitle('Eventos');
  setBack(false);
  const app = document.getElementById('app');
  if (!isAuthenticated()) {
    app.innerHTML = buildGuestAuthHTML('/eventos');
    return;
  }
  app.innerHTML = LOADER_HTML;
  await ensureEventos(force);
  const eventos = state.eventos?.items || [];
  if (!eventos.length) {
    app.innerHTML = `
      <div class="empty-state">
        <svg viewBox="0 0 24 24" width="48" height="48" aria-hidden="true"><path fill="currentColor" d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20a2 2 0 0 0 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zm0-12H5V6h14v2z"/></svg>
        <p>Nenhum evento encontrado.</p>
      </div>
    `;
    return;
  }
  const items = eventos
    .map((evento) => `
      <article class="list-item" data-id="${evento.id}">
        <header>
          <div>
            <h3>${evento.nome || 'Evento sem nome'}</h3>
            <p>${safeGet(evento, 'local', 'Local não informado')}</p>
          </div>
          <span class="chip">${evento.ativo ? 'Ativo' : 'Inativo'}</span>
        </header>
        <p>${evento.descricao ? evento.descricao.slice(0, 160) : 'Sem descrição adicional.'}</p>
      </article>
    `)
    .join('');
  app.innerHTML = `<section class="list">${items}</section>`;
}

async function renderVagas(force = false) {
  setTitle('Vagas');
  setBack(false);
  const app = document.getElementById('app');
  if (!isAuthenticated()) {
    app.innerHTML = buildGuestAuthHTML('/vagas');
    return;
  }
  app.innerHTML = LOADER_HTML;
  await ensureVagas(force);
  const vagas = state.vagas?.items || [];
  if (!vagas.length) {
    app.innerHTML = `
      <div class="empty-state">
        <svg viewBox="0 0 24 24" width="48" height="48" aria-hidden="true"><path fill="currentColor" d="M14 6V4H6v2H2v14h20V6h-8zM6 8h12v10H6V8z"/></svg>
        <p>Nenhuma vaga encontrada.</p>
      </div>
    `;
    return;
  }
  const items = vagas
    .map((vaga) => `
      <article class="list-item" data-id="${vaga.id}">
        <header>
          <div>
            <h3>${vaga.titulo || 'Vaga sem título'}</h3>
            <p>${safeGet(vaga, 'setor.evento.nome', vaga.evento_nome || 'Evento não informado')}</p>
          </div>
          <span class="chip">${vaga.ativa ? 'Ativa' : 'Inativa'}</span>
        </header>
        <p>${vaga.descricao ? vaga.descricao.slice(0, 160) : 'Sem descrição adicional.'}</p>
      </article>
    `)
    .join('');
  app.innerHTML = `<section class="list">${items}</section>`;
}

async function renderCandidaturas(force = false) {
  setTitle('Candidaturas');
  setBack(false);
  const app = document.getElementById('app');
  if (!isAuthenticated()) {
    app.innerHTML = buildGuestAuthHTML('/candidaturas');
    return;
  }
  app.innerHTML = LOADER_HTML;
  await ensureCandidaturas(force);
  const candidaturas = state.candidaturas?.items || [];
  if (!candidaturas.length) {
    app.innerHTML = `
      <div class="empty-state">
        <svg viewBox="0 0 24 24" width="48" height="48" aria-hidden="true"><path fill="currentColor" d="M19 3H5a2 2 0 0 0-2 2v16l4-4h12a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z"/></svg>
        <p>Nenhuma candidatura encontrada.</p>
      </div>
    `;
    return;
  }
  const items = candidaturas
    .map((candidatura) => {
      const vaga = candidatura.vaga || {};
      const status = candidatura.status?.toLowerCase?.() || 'pendente';
      return `
        <article class="list-item" data-id="${candidatura.id}">
          <header>
            <div>
              <h3>${vaga.titulo || 'Vaga'}</h3>
              <p>${safeGet(vaga, 'setor.evento.nome', vaga.evento_nome || 'Evento não informado')}</p>
            </div>
            <span class="status-pill ${status}">${STATUS_LABELS[status] || status}</span>
          </header>
          <p>${vaga.descricao ? vaga.descricao.slice(0, 160) : 'Sem descrição adicional.'}</p>
        </article>
      `;
    })
    .join('');
  app.innerHTML = `<section class="list">${items}</section>`;
}

async function renderFinanceiro(force = false) {
  setTitle('Financeiro');
  setBack(false);
  const app = document.getElementById('app');
  if (!isAuthenticated()) {
    app.innerHTML = buildGuestAuthHTML('/financeiro');
    return;
  }
  app.innerHTML = `
    <div class="empty-state">
      <svg viewBox="0 0 24 24" width="48" height="48" aria-hidden="true"><path fill="currentColor" d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>
      <p>Funcionalidade financeiro em breve.</p>
    </div>
  `;
}

function bindHomeEvents(container) {
  container.querySelectorAll('.quick-card').forEach((card) => {
    card.addEventListener('click', () => router.go(card.dataset.path));
  });
}

async function renderRoute(path, { force = false } = {}) {
  currentPath = path || '/';
  const mainPath = currentPath === '/' ? '/' : `/${currentPath.split('/')[1]}`;
  setBack(currentPath !== '/');
  setActiveTab(mainPath);

  if (requiresAuth(currentPath) && !isAuthenticated()) {
    const app = document.getElementById('app');
    app.innerHTML = buildGuestAuthHTML(currentPath);
    openLoginModal();
    return;
  }

  switch (true) {
    case currentPath === '/':
      await renderHome(force);
      break;
    case currentPath.startsWith('/eventos'):
      await renderEventos(force);
      break;
    case currentPath.startsWith('/vagas'):
      await renderVagas(force);
      break;
    case currentPath.startsWith('/candidaturas'):
      await renderCandidaturas(force);
      break;
    case currentPath.startsWith('/financeiro'):
      await renderFinanceiro(force);
      break;
    default:
      await renderHome(force);
  }
}

const router = {
  go(path) {
    if (path === currentPath) {
      renderRoute(path, { force: true });
      return;
    }
    window.location.hash = `#${path}`;
  },
  back() {
    window.history.back();
  },
};

window.router = router;

function initPWAInstall() {
  let deferredPrompt;
  
  function isAppInstalled() {
    if (localStorage.getItem('pwa-installed') === 'true') return true;
    try {
      if (window.matchMedia('(display-mode: standalone)').matches) {
        localStorage.setItem('pwa-installed', 'true');
        return true;
      }
    } catch (e) {
      console.error('Erro ao verificar display-mode:', e);
    }
    if (window.navigator.standalone === true) {
      localStorage.setItem('pwa-installed', 'true');
      return true;
    }
    return false;
  }
  
  if (isAppInstalled()) {
    if (banner) banner.hidden = true;
    return;
  }
  
  if (localStorage.getItem(STORAGE_KEYS.installDismissed) === 'true') {
    if (banner) banner.hidden = true;
    return;
  }
  
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (banner) {
      banner.hidden = false;
      banner.classList.add('visible');
    }
  });
  
  window.addEventListener('appinstalled', () => {
    localStorage.setItem('pwa-installed', 'true');
    if (banner) banner.hidden = true;
    showToast('App instalado com sucesso!', 'success');
    deferredPrompt = null;
  });
  
  if (btnInstall) {
    btnInstall.addEventListener('click', async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === 'accepted') {
        localStorage.setItem('pwa-installed', 'true');
      }
      deferredPrompt = null;
      if (banner) banner.hidden = true;
    });
  }
  
  if (btnDismiss) {
    btnDismiss.addEventListener('click', () => {
      localStorage.setItem(STORAGE_KEYS.installDismissed, 'true');
      if (banner) banner.hidden = true;
    });
  }
}

function initServiceWorker() {
  if ('serviceWorker' in navigator && CONFIG.swUrl) {
    navigator.serviceWorker.register(CONFIG.swUrl, { scope: CONFIG.swScope || '/' })
      .then(() => console.log('[Eventix Empresa PWA] Service Worker registrado'))
      .catch((error) => console.error('[Eventix Empresa PWA] Erro ao registrar Service Worker', error));
  }
}

function initNavigation() {
  document.querySelectorAll('.nav-item').forEach((item) => {
    item.addEventListener('click', () => {
      const path = item.dataset.path;
      router.go(path);
    });
  });
}

function initLoginModal() {
  if (loginForm) {
    loginForm.addEventListener('submit', handleLoginSubmit);
  }
  if (loginCancel) {
    loginCancel.addEventListener('click', closeLoginModal);
  }
  if (closeLoginModalBtn) {
    closeLoginModalBtn.addEventListener('click', closeLoginModal);
  }
  window.openLoginModal = openLoginModal;
  window.closeLoginModal = closeLoginModal;
}

function initRefresh() {
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      renderRoute(currentPath, { force: true });
    });
  }
}

function attachGlobalListeners() {
  if (authBtn) {
    authBtn.addEventListener('click', () => (isAuthenticated() ? handleLogout() : openLoginModal()));
  }
}

function initHashRouter() {
  const handle = () => {
    const hash = window.location.hash.slice(1) || '/';
    renderRoute(hash).catch((error) => {
      console.error('[Eventix Empresa PWA] Erro ao renderizar rota', error);
      const app = document.getElementById('app');
      if (app) {
        app.innerHTML = '<div class="empty-state"><p>Erro ao carregar conteúdo.</p></div>';
      }
    });
  };
  window.addEventListener('hashchange', handle);
  handle();
}

router.start = initHashRouter;

// Inicialização
loadAuthFromStorage();
updateAuthUI();
attachGlobalListeners();
initServiceWorker();
initPWAInstall();
initNavigation();
initLoginModal();
initRefresh();

// Inicializar router após tudo estar pronto
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initHashRouter();
  });
} else {
  initHashRouter();
}

if (isAuthenticated()) {
  hydrateAuthenticatedData();
}

