const CONFIG = window.EVENTIX_PWA_CONFIG || {};

const API_BASE = '/api/v1';
const ENDPOINTS = {
  login: '/auth/login/',
  refresh: '/auth/refresh/',
  logout: '/auth/logout/',
  profile: '/users/profile/',
  freelancer: '/freelancers/',
  vagas: '/vagas/',
  candidaturas: '/candidaturas/',
  funcoes: '/freelancers/funcoes/',
};

const STORAGE_KEYS = {
  auth: 'eventix:frel:pwa:auth',
};

const state = {
  tokens: null,
  user: null,
  profile: null,
  freelancer: null,
  candidaturas: null,
  vagas: null,
  vagasFilters: {
    search: '',
  },
  funcoes: null,
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

const ROUTES_REQUIRING_AUTH = ['/vagas', '/candidaturas', '/funcoes', '/perfil', '/notificacoes'];
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
    console.warn('[Eventix PWA] Falha ao carregar auth localStorage', error);
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
  state.freelancer = null;
  state.candidaturas = null;
  state.vagas = null;
  state.funcoes = null;
  saveAuthToStorage();
  updateAuthUI();
}

function isAuthenticated() {
  return Boolean(state.tokens?.access);
}

function setTitle(text) {
  if (titleEl) titleEl.textContent = text;
}

function setBack(show) {
  if (backBtn) backBtn.hidden = !show;
}

function setActiveTab(path) {
  document.querySelectorAll('.nav-item').forEach((el) => {
    el.classList.toggle('active', el.dataset.path === path);
  });
}

function showToast(message, type = 'info') {
  if (!toastContainer) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
      <path fill="currentColor" d="M12 2a10 10 0 1 0 10 10A10.01 10.01 0 0 0 12 2Zm.75 15h-1.5v-1.5h1.5Zm0-3h-1.5v-6h1.5Z" />
    </svg>
    <span>${message}</span>
  `;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('hidden');
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

function openLoginModal() {
  if (!loginModal) return;
  loginModal.classList.remove('hidden');
  requestAnimationFrame(() => loginEmail?.focus());
}

function closeLoginModal() {
  loginModal?.classList.add('hidden');
  loginForm?.reset();
}

function updateAuthUI() {
  if (!authBtn) return;
  if (isAuthenticated()) {
    authBtn.setAttribute('aria-label', 'Sair da conta');
    authBtn.innerHTML = `
      <svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">
        <path fill="currentColor" d="M16 13v-2H7V8L2 12l5 4v-3zm3-10H9a2 2 0 0 0-2 2v3h2V5h10v14H9v-3H7v3a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z" />
      </svg>
    `;
  } else {
    authBtn.setAttribute('aria-label', 'Entrar ou criar conta');
    authBtn.innerHTML = `
      <svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">
        <path fill="currentColor" d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5zm0 2c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z" />
      </svg>
    `;
  }
}

async function refreshAccessToken() {
  if (!state.tokens?.refresh) return false;
  try {
    const response = await fetch(`${API_BASE}${ENDPOINTS.refresh}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: state.tokens.refresh }),
    });
    if (!response.ok) throw new Error('Falha no refresh');
    const data = await response.json();
    state.tokens.access = data.access;
    saveAuthToStorage();
    return true;
  } catch (error) {
    console.warn('[Eventix PWA] Falha ao renovar token', error);
    clearAuth();
    return false;
  }
}

async function apiFetch(path, options = {}, { skipAuth = false } = {}) {
  const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
  const headers = new Headers(options.headers || {});
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (!skipAuth && state.tokens?.access) {
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
    showToast(`Bem-vindo(a), ${payload.user?.nome_completo || payload.user?.username || 'freelancer'}!`, 'success');
    await hydrateAuthenticatedData(true);
    renderRoute(currentPath, { force: true });
  } catch (error) {
    console.error('[Eventix PWA] Falha no login', error);
    showToast('Login inválido. Verifique suas credenciais.', 'error');
  }
}

async function handleLogout() {
  try {
    if (state.tokens?.access) {
      await apiFetch(ENDPOINTS.logout, { method: 'POST' });
    }
  } catch (error) {
    console.warn('[Eventix PWA] Erro ao fazer logout', error);
  } finally {
    clearAuth();
    renderRoute('/', { force: true });
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
      ensureFreelancerProfile(force),
    ]);
  } catch (error) {
    console.error('[Eventix PWA] Erro ao carregar dados iniciais', error);
  }
}

async function ensureUserProfile(force = false) {
  if (!isAuthenticated()) return null;
  if (state.profile && !force) return state.profile;
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
}

async function ensureFreelancerProfile(force = false) {
  if (!isAuthenticated()) return null;
  if (state.freelancer && !force) return state.freelancer;
  const data = await apiFetch(ENDPOINTS.freelancer);
  const items = Array.isArray(data) ? data : data?.results || [];
  state.freelancer = items[0] || null;
  return state.freelancer;
}

async function ensureCandidaturas(force = false) {
  if (!isAuthenticated()) return null;
  if (state.candidaturas && !force) return state.candidaturas;
  const data = await apiFetch(ENDPOINTS.candidaturas);
  const items = Array.isArray(data) ? data : data?.results || [];
  state.candidaturas = {
    items,
    count: data?.count ?? items.length,
  };
  return state.candidaturas;
}

async function ensureVagas({ search = state.vagasFilters.search, force = false } = {}) {
  if (!isAuthenticated()) return null;
  if (state.vagas && !force && state.vagasFilters.search === search) return state.vagas;
  const params = new URLSearchParams({ page: '1' });
  if (search) params.set('search', search);
  const data = await apiFetch(`${ENDPOINTS.vagas}?${params.toString()}`);
  const items = Array.isArray(data) ? data : data?.results || [];
  state.vagas = {
    items,
    count: data?.count ?? items.length,
  };
  state.vagasFilters.search = search;
  return state.vagas;
}

async function ensureFuncoes(force = false) {
  if (!isAuthenticated()) return null;
  if (state.funcoes && !force) return state.funcoes;
  const data = await apiFetch(ENDPOINTS.funcoes);
  const items = Array.isArray(data) ? data : data?.results || [];
  state.funcoes = items;
  return state.funcoes;
}

function formatCurrencyBRL(value) {
  const number = Number(value ?? 0);
  return number.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
  });
}

function safeGet(object, path, fallback = '') {
  return path.split('.').reduce((acc, key) => (acc && acc[key] !== undefined ? acc[key] : undefined), object) ?? fallback;
}

function renderGuestHome() {
  return `
    <div class="card" style="background:linear-gradient(135deg,#6366F1,#8B5CF6);color:#fff;">
      <div class="title-lg">Olá!</div>
      <p class="subtitle" style="color:rgba(255,255,255,.85)">Entre na sua conta para acessar vagas e candidaturas.</p>
      <div class="row" style="justify-content:flex-start;margin-top:16px;gap:12px;">
        <button class="btn" onclick="router.go('/vagas')">Ver Vagas</button>
        <button class="btn btn-text" style="color:#fff" onclick="window.openLoginModal?.()">Entrar</button>
      </div>
    </div>
    <div class="card" style="margin-top:16px;">
      <div class="title-lg">Nova experiência PWA</div>
      <p class="subtitle">Instale o Eventix para acessar oportunidades com rapidez.</p>
    </div>
  `;
}

function buildHomeHTML() {
  const profile = state.profile || {};
  const freelancer = state.freelancer || {};
  const nome = freelancer.nome_completo || profile.first_name || profile.username || 'Freelancer';
  const primeiroNome = nome.split(' ')[0];
  const candidaturas = state.candidaturas?.items || [];
  const totalCandidaturas = candidaturas.length;
  const pendentes = candidaturas.filter((c) => c.status === 'pendente' || c.status === 'Pendente').length;
  const aprovadas = candidaturas.filter((c) => ['aprovado', 'aprovada', 'contratado'].includes((c.status || '').toLowerCase())).length;
  const vagasAtivas = state.vagas?.count || 0;

  return `
    <section class="hero-card">
      <div>
        <p class="hero-eyebrow">Bem-vindo de volta</p>
        <h2 class="hero-title">Olá, ${primeiroNome} 👋</h2>
        <p class="hero-subtitle">Gerencie suas oportunidades e candidaturas em tempo real.</p>
      </div>
      <button class="btn btn-light" data-action="ver-vagas">Ver vagas</button>
    </section>

    <section class="stats-grid">
      <article class="stat-card">
        <span class="stat-label">Total de candidaturas</span>
        <span class="stat-number">${totalCandidaturas}</span>
      </article>
      <article class="stat-card">
        <span class="stat-label">Pendentes</span>
        <span class="stat-number">${pendentes}</span>
      </article>
      <article class="stat-card">
        <span class="stat-label">Aprovadas</span>
        <span class="stat-number">${aprovadas}</span>
      </article>
      <article class="stat-card">
        <span class="stat-label">Vagas ativas</span>
        <span class="stat-number">${vagasAtivas}</span>
      </article>
    </section>

    <section class="action-grid">
      <article class="action-card" data-path="/vagas/recomendadas">
        <div>
          <h3>Oportunidades</h3>
          <p>Vagas recomendadas para você</p>
        </div>
        <span class="action-icon">➜</span>
      </article>
      <article class="action-card" data-path="/vagas">
        <div>
          <h3>Todas as vagas</h3>
          <p>Descubra novas experiências</p>
        </div>
        <span class="action-icon">➜</span>
      </article>
      <article class="action-card" data-path="/candidaturas">
        <div>
          <h3>Minhas candidaturas</h3>
          <p>Consulte o status em minutos</p>
        </div>
        <span class="action-icon">➜</span>
      </article>
      <article class="action-card" data-path="/perfil">
        <div>
          <h3>Meu perfil</h3>
          <p>Atualize suas informações</p>
        </div>
        <span class="action-icon">➜</span>
      </article>
    </section>
  `;
}

function buildGuestAuthHTML(path) {
  return `
    <div class="empty-state">
      <svg viewBox="0 0 24 24" width="48" height="48" aria-hidden="true"><path fill="currentColor" d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5zm-9 9v-1a7 7 0 0 1 7-7h4a7 7 0 0 1 7 7v1z" /></svg>
      <p>Entre para acessar ${path.startsWith('/vagas') ? 'as vagas disponíveis' : 'este conteúdo'}.</p>
      <button class="btn" onclick="window.openLoginModal?.()">Fazer login</button>
    </div>
  `;
}

function buildVagasHTML() {
  const vagas = state.vagas?.items || [];
  if (!vagas.length) {
    return `
      <div class="search-block">
        <div class="search">
          <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5z"/></svg>
          <input id="vagasSearch" class="input" placeholder="Buscar vagas..." value="${state.vagasFilters.search || ''}">
          <button class="icon-btn" id="vagasClearSearch" aria-label="Limpar busca" ${state.vagasFilters.search ? '' : 'hidden'}>
            <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M18.3 5.71 12 12l6.3 6.29-1.41 1.42L10.59 13.4 4.29 19.7 2.88 18.3 9.17 12 2.88 5.71 4.29 4.3l6.3 6.29L16.89 4.3z"/></svg>
          </button>
        </div>
      </div>
      <div class="empty-state">
        <svg viewBox="0 0 24 24" width="48" height="48" aria-hidden="true"><path fill="currentColor" d="M14 6V4H6v2H2v14h20V6z"/></svg>
        <p>Nenhuma vaga encontrada com o filtro atual.</p>
        <button class="btn" data-action="reset-vagas">Limpar filtros</button>
      </div>
    `;
  }

  const cards = vagas
    .map((vaga) => {
      const evento = safeGet(vaga, 'setor.evento.nome', vaga.evento_nome || 'Evento não informado');
      const funcao = safeGet(vaga, 'funcao.nome', 'Função não informada');
      const remuneracao = formatCurrencyBRL(vaga.remuneracao);
      const quantidade = vaga.quantidade || 1;
      const descricao = vaga.descricao ? vaga.descricao.slice(0, 160) : 'Sem descrição complementar.';
      return `
        <article class="list-item" data-id="${vaga.id}">
          <header>
            <div>
              <h3>${vaga.titulo || 'Vaga sem título'}</h3>
              <p>${evento}</p>
            </div>
            <span class="chip">${quantidade} vaga(s)</span>
          </header>
          <p>${descricao}</p>
          <p class="vaga-info">${funcao} • ${remuneracao}</p>
          <div class="list-actions">
            <button class="btn" data-action="candidatar" data-vaga="${vaga.id}">Candidatar-se</button>
            <a class="inline-link" href="/freelancer/vaga/${vaga.id}/" target="_blank" rel="noopener">Ver detalhes</a>
          </div>
        </article>
      `;
    })
    .join('');

  return `
    <div class="search-block">
      <div class="search">
        <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5z"/></svg>
        <input id="vagasSearch" class="input" placeholder="Buscar por título, função ou evento" value="${state.vagasFilters.search || ''}">
        <button class="icon-btn" id="vagasClearSearch" aria-label="Limpar busca" ${state.vagasFilters.search ? '' : 'hidden'}>
          <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M18.3 5.71 12 12l6.3 6.29-1.41 1.42L10.59 13.4 4.29 19.7 2.88 18.3 9.17 12 2.88 5.71 4.29 4.3l6.3 6.29L16.89 4.3z"/></svg>
        </button>
      </div>
    </div>
    <section class="list">${cards}</section>
  `;
}

function buildPerfilHTML() {
  const user = state.profile || {};
  const freelancer = state.freelancer || {};
  const funcoes = state.funcoes || [];
  const inicial = (freelancer.nome_completo || user.first_name || 'F').charAt(0).toUpperCase();

  const infoRows = [
    { label: 'CPF', value: freelancer.cpf },
    { label: 'Telefone', value: freelancer.telefone },
    { label: 'Data de nascimento', value: freelancer.data_nascimento },
    { label: 'Sexo', value: freelancer.sexo },
    { label: 'Cidade', value: freelancer.cidade },
    { label: 'Estado', value: freelancer.uf },
  ]
    .filter((row) => row.value)
    .map((row) => `
      <div class="info-row">
        <span>${row.label}</span>
        <strong>${row.value}</strong>
      </div>
    `)
    .join('');

  const funcoesHtml = funcoes.length
    ? `
        <div class="section-title">Funções</div>
        <div class="chip-row">
          ${funcoes.map((funcao) => `<span class="chip">${funcao.funcao?.nome || funcao.funcao_nome || 'Função'}</span>`).join('')}
        </div>
      `
    : '<p class="subtitle">Nenhuma função cadastrada ainda.</p>';

  return `
    <section class="perfil-header">
      <div class="avatar">${inicial}</div>
      <h2>${freelancer.nome_completo || user.first_name || 'Seu nome'}</h2>
      <p>${user.email || freelancer.usuario_email || ''}</p>
      <span class="status-pill contratada">Freelancer</span>
    </section>

    <section class="card">
      <div class="section-title">Informações principais</div>
      ${infoRows || '<p class="subtitle">Complete suas informações para aumentar as chances de contratação.</p>'}
    </section>

    <section class="card">
      ${funcoesHtml}
      <a class="inline-link" href="/freelancer/funcoes/" target="_blank" rel="noopener">Gerenciar funções</a>
    </section>
  `;
}

async function handleCandidatarClick(vagaId, button) {
  if (!vagaId) return;
  if (button) {
    button.disabled = true;
    button.textContent = 'Enviando...';
  }
  try {
    await apiFetch(ENDPOINTS.candidaturas, {
      method: 'POST',
      body: JSON.stringify({ vaga_id: vagaId }),
    });
    showToast('Candidatura enviada com sucesso!', 'success');
    await Promise.all([
      ensureCandidaturas(true),
      ensureVagas({ force: true }),
    ]);
    renderRoute(currentPath, { force: true });
  } catch (error) {
    console.error('[Eventix PWA] Erro ao candidatar-se', error);
    showToast(error.payload?.error || 'Não foi possível enviar a candidatura.', 'error');
  } finally {
    if (button) {
      button.disabled = false;
      button.textContent = 'Candidatar-se';
    }
  }
}

function bindHomeEvents(container) {
  container.querySelectorAll('.action-card').forEach((card) => {
    card.addEventListener('click', () => router.go(card.dataset.path));
  });
  container.querySelector('[data-action="ver-vagas"]')?.addEventListener('click', () => router.go('/vagas'));
}

function debounce(fn, delay = 400) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}

function bindVagasEvents(container) {
  const searchInput = container.querySelector('#vagasSearch');
  const clearBtn = container.querySelector('#vagasClearSearch');
  if (searchInput) {
    searchInput.addEventListener(
      'input',
      debounce(async (event) => {
        state.vagasFilters.search = event.target.value.trim();
        await ensureVagas({ search: state.vagasFilters.search, force: true });
        renderRoute('/vagas');
      }),
    );
  }
  if (clearBtn) {
    clearBtn.addEventListener('click', async () => {
      state.vagasFilters.search = '';
      await ensureVagas({ search: '', force: true });
      renderRoute('/vagas');
    });
  }
  container.querySelectorAll('[data-action="candidatar"]').forEach((button) => {
    button.addEventListener('click', () => handleCandidatarClick(button.dataset.vaga, button));
  });
  container.querySelector('[data-action="reset-vagas"]')?.addEventListener('click', async () => {
    state.vagasFilters.search = '';
    await ensureVagas({ search: '', force: true });
    renderRoute('/vagas');
  });
}

function bindPerfilEvents() {
  // Espaço reservado para ações futuras (editar perfil, etc.)
}

async function renderHome(force = false) {
  setTitle('Eventix');
  setBack(false);
  const app = document.getElementById('app');
  if (!isAuthenticated()) {
    app.innerHTML = renderGuestHome();
    return;
  }
  app.innerHTML = LOADER_HTML;
  await Promise.all([
    ensureUserProfile(force),
    ensureFreelancerProfile(force),
    ensureCandidaturas(force),
    ensureVagas({ force }),
  ]);
  app.innerHTML = buildHomeHTML();
  bindHomeEvents(app);
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
  await ensureVagas({ force });
  app.innerHTML = buildVagasHTML();
  bindVagasEvents(app);
}

async function renderPerfil(force = false) {
  setTitle('Perfil');
  setBack(false);
  const app = document.getElementById('app');
  if (!isAuthenticated()) {
    app.innerHTML = buildGuestAuthHTML('/perfil');
    return;
  }
  app.innerHTML = LOADER_HTML;
  await Promise.all([
    ensureUserProfile(force),
    ensureFreelancerProfile(force),
    ensureFuncoes(force),
  ]);
  app.innerHTML = buildPerfilHTML();
  bindPerfilEvents(app);
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
        <svg viewBox="0 0 24 24" width="48" height="48" aria-hidden="true"><path fill="currentColor" d="M19 3H5a2 2 0 0 0-2 2v14l4-4h12a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z"/></svg>
        <p>Você ainda não se candidatou a nenhuma vaga.</p>
        <button class="btn" onclick="router.go('/vagas')">Encontrar vagas</button>
      </div>
    `;
    return;
  }
  const items = candidaturas
    .map((candidatura) => {
      const vaga = candidatura.vaga || {};
      const status = candidatura.status?.toLowerCase?.() || 'pendente';
      return `
        <article class="list-item">
          <header>
            <div>
              <h3>${vaga.titulo || 'Vaga'}</h3>
              <p>${safeGet(vaga, 'evento_nome', safeGet(vaga, 'setor.evento.nome', 'Evento não informado'))}</p>
            </div>
            <span class="status-pill ${status}">${STATUS_LABELS[status] || status}</span>
          </header>
          <p>${vaga.descricao ? vaga.descricao.slice(0, 160) : 'Sem descrição adicional.'}</p>
          <div class="list-actions">
            <a class="inline-link" href="/freelancer/vaga/${vaga.id}/" target="_blank" rel="noopener">Ver detalhes</a>
          </div>
        </article>
      `;
    })
    .join('');
  app.innerHTML = `<section class="list">${items}</section>`;
}

async function renderNotificacoes() {
  setTitle('Notificações');
  setBack(false);
  const app = document.getElementById('app');
  app.innerHTML = '<div class="empty-state"><p>Notificações em breve.</p></div>';
}

async function renderFuncoes(force = false) {
  setTitle('Minhas funções');
  setBack(false);
  const app = document.getElementById('app');
  if (!isAuthenticated()) {
    app.innerHTML = buildGuestAuthHTML('/funcoes');
    return;
  }
  app.innerHTML = LOADER_HTML;
  await ensureFuncoes(force);
  const funcoes = state.funcoes || [];
  if (!funcoes.length) {
    app.innerHTML = '<div class="empty-state"><p>Você ainda não adicionou funções. Atualize seu perfil para receber vagas alinhadas.</p></div>';
    return;
  }
  const items = funcoes
    .map((funcao) => `
      <article class="list-item">
        <header>
          <div>
            <h3>${funcao.funcao?.nome || funcao.funcao_nome || 'Função'}</h3>
            <p>${funcao.nivel || 'Sem nível'}</p>
          </div>
        </header>
      </article>
    `)
    .join('');
  app.innerHTML = `<section class="list">${items}</section>`;
}

async function renderRoute(path, { force = false } = {}) {
  currentPath = path || '/';
  const mainPath = currentPath === '/' ? '/' : `/${currentPath.split('/')[1]}`;
  setBack(currentPath !== '/');
  setActiveTab(mainPath.startsWith('/vagas') ? '/vagas' : mainPath);

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
    case currentPath.startsWith('/vagas') && currentPath !== '/vagas/recomendadas':
      await renderVagas(force);
      break;
    case currentPath.startsWith('/vagas'):
      await renderVagas(force);
      break;
    case currentPath.startsWith('/candidaturas'):
      await renderCandidaturas(force);
      break;
    case currentPath.startsWith('/perfil'):
      await renderPerfil(force);
      break;
    case currentPath.startsWith('/funcoes'):
      await renderFuncoes(force);
      break;
    case currentPath.startsWith('/notificacoes'):
      await renderNotificacoes(force);
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
    location.hash = '#' + path;
  },
  back() {
    history.back();
  },
  start() {
    const handle = () => {
      const path = location.hash.replace('#', '') || '/';
      renderRoute(path).catch((error) => console.error('[Eventix PWA] Erro ao renderizar rota', error));
    };
    window.addEventListener('hashchange', handle);
    handle();
  },
};

window.router = router;
window.openLoginModal = openLoginModal;

function attachGlobalListeners() {
  if (loginCancel) loginCancel.addEventListener('click', closeLoginModal);
  if (closeLoginModalBtn) closeLoginModalBtn.addEventListener('click', closeLoginModal);
  if (loginForm) loginForm.addEventListener('submit', handleLoginSubmit);
  if (authBtn) authBtn.addEventListener('click', () => (isAuthenticated() ? handleLogout() : openLoginModal()));
  if (refreshBtn) refreshBtn.addEventListener('click', () => renderRoute(currentPath, { force: true }));
}

function registerNavItems() {
  document.querySelectorAll('.nav-item').forEach((el) => {
    el.addEventListener('click', () => router.go(el.dataset.path));
  });
}

let deferredPrompt;
window.addEventListener('beforeinstallprompt', (event) => {
  event.preventDefault();
  deferredPrompt = event;
  if (banner) banner.hidden = false;
});

btnInstall?.addEventListener('click', async () => {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  await deferredPrompt.userChoice;
  if (banner) banner.hidden = true;
  deferredPrompt = null;
});

btnDismiss?.addEventListener('click', () => {
  if (banner) banner.hidden = true;
});

if ('serviceWorker' in navigator && CONFIG.swUrl) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register(CONFIG.swUrl, { scope: CONFIG.swScope || '/freelancer/app/' })
      .catch((error) => console.warn('[Eventix PWA] Falha ao registrar Service Worker', error));
  });
}

async function init() {
  loadAuthFromStorage();
  updateAuthUI();
  attachGlobalListeners();
  registerNavItems();
  if (isAuthenticated()) await hydrateAuthenticatedData();
  router.start();
}

init();

