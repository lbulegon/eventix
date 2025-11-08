// Simple hash router
const router = {
  routes: {},
  go(path){ location.hash = '#'+path; },
  back(){ history.back(); },
  on(path, handler){ this.routes[path] = handler; },
  start(){
    const handle = () => {
      const path = location.hash.replace('#','') || '/';
      render(path);
    };
    window.addEventListener('hashchange', handle);
    handle();
  }
};
window.router = router;

const titleEl = document.getElementById('app-title');
const backBtn = document.getElementById('backBtn');

function setTitle(t){ titleEl.textContent = t; }
function setBack(show){ backBtn.hidden = !show; }
function setActiveTab(path){
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.path === path);
  });
}

// Views
function Home(){
  setTitle('Eventix');
  setBack(true); // to mimic the screenshots with back chevron visible sometimes
  return `
  <div class="grid">
    <div class="card">
      <div class="title-lg">Olá, <span class="muted">!</span></div>
      <div class="subtitle">Bem-vindo ao Eventix</div>
    </div>
    <div class="card row" style="justify-content:space-between;">
      <div>
        <div class="title-lg">Oportunidades e recomendações</div>
        <div class="subtitle">Vagas escolhidas especialmente para você</div>
      </div>
      <button class="btn" onclick="router.go('/vagas/recomendadas')">Ver</button>
    </div>
    <div class="card row" style="justify-content:space-between;">
      <div>
        <div class="title-lg">Todas as Vagas</div>
        <div class="subtitle">Buscar oportunidades</div>
      </div>
      <button class="btn" onclick="router.go('/vagas')">Buscar</button>
    </div>
    <div class="card row" style="justify-content:space-between;">
      <div>
        <div class="title-lg">Minhas Candidaturas</div>
        <div class="subtitle">Acompanhe status</div>
      </div>
      <button class="btn" onclick="router.go('/candidaturas')">Abrir</button>
    </div>
    <div class="card row" style="justify-content:space-between;">
      <div>
        <div class="title-lg">Funções</div>
        <div class="subtitle">Configure suas especialidades</div>
      </div>
      <button class="btn" onclick="router.go('/funcoes')">Configurar</button>
    </div>
  </div>`;
}

function VagasList(){
  setTitle('Vagas Disponíveis');
  setBack(true);
  return `
    <div class="search">
      <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zM9.5 14C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
      <input class="input" placeholder="Buscar vagas..." oninput="/* TODO: filter */">
      <button class="icon-btn" aria-label="filtros">
        <svg viewBox="0 0 24 24" width="22" height="22"><path fill="currentColor" d="M10 18h4v-2h-4v2zm-7-8v2h18v-2H3zm3-6v2h12V4H6z"/></svg>
      </button>
      <button class="icon-btn" aria-label="atualizar" onclick="location.reload()">
        <svg viewBox="0 0 24 24" width="22" height="22"><path fill="currentColor" d="M17.65 6.35A7.95 7.95 0 0 0 12 4V1L7 6l5 5V7a5 5 0 1 1-5 5H5a7 7 0 1 0 12.65-5.65z"/></svg>
      </button>
    </div>
    <div class="empty">
      <div class="icon">
        <svg viewBox="0 0 24 24" width="38" height="38"><path fill="currentColor" d="M14 6V4H6v2H2v14h20V6h-8zM6 8h12v10H6V8z"/></svg>
      </div>
      <div class="title-lg">Nenhuma vaga disponível</div>
    </div>
  `;
}

function Candidaturas(){
  setTitle('Minhas Candidaturas');
  setBack(true);
  return `
    <div class="empty">
      <div class="icon">
        <svg viewBox="0 0 24 24" width="38" height="38"><path fill="currentColor" d="M19 3H5a2 2 0 0 0-2 2v14l4-4h12a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z"/></svg>
      </div>
      <div class="title-lg">Nenhuma candidatura encontrada</div>
      <div class="subtitle">Você ainda não se candidatou a nenhuma vaga</div>
    </div>
  `;
}

function Funcoes(){
  setTitle('Minhas Funções');
  setBack(true);
  const tabs = [
    {key:'buscar', label:'Buscar Funções', content:`
      <div class="empty">
        <div class="icon">
          <svg viewBox="0 0 24 24" width="38" height="38"><path fill="currentColor" d="M14 6V4H6v2H2v14h20V6h-8zM6 8h12v10H6V8z"/></svg>
        </div>
        <div class="title-lg">Nenhuma função de segurança disponível</div>
      </div>
    `},
    {key:'minhas', label:'Minhas Funções', content:`
      <div class="empty">
        <div class="icon">
          <svg viewBox="0 0 24 24" width="38" height="38"><path fill="currentColor" d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5zm0 2c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z"/></svg>
        </div>
        <div class="title-lg">Você ainda não adicionou funções</div>
      </div>
    `}
  ];
  const active = (location.hash.includes('minhas')) ? 'minhas' : 'buscar';
  const tabEls = tabs.map(t=>`<div class="tab ${active===t.key?'active':''}" onclick="router.go('/funcoes/${t.key}')">${t.label}</div>`).join('');
  const content = tabs.find(t=>t.key===active).content;
  return `
    <div class="tabs">${tabEls}</div>
    <div>${content}</div>
  `;
}

function Notificacoes(){
  setTitle('Notificações');
  setBack(true);
  return `
    <div class="empty">
      <div class="icon">
        <svg viewBox="0 0 24 24" width="38" height="38"><path fill="currentColor" d="M12 22a2 2 0 0 0 2-2H10a2 2 0 0 0 2 2zm6-6V11a6 6 0 1 0-12 0v5l-2 2v1h16v-1l-2-2z"/></svg>
      </div>
      <div class="title-lg">Nenhuma notificação</div>
      <div class="subtitle">Você receberá notificações sobre suas candidaturas e novas vagas</div>
    </div>
  `;
}

function VagasParaVoce(){
  setTitle('Vagas para Você');
  setBack(true);
  const tabs = [
    {key:'recomendadas', label:'Recomendadas'},
    {key:'em-alta', label:'Em Alta'},
    {key:'urgentes', label:'Urgentes'},
  ];
  const activeKey = (location.hash.split('/')[2]) || 'recomendadas';
  const tabEls = tabs.map(t => `<div class="tab ${t.key===activeKey?'active':''}" onclick="router.go('/vagas/${t.key}')">${t.label}</div>`).join('');
  return `
    <div class="tabs">${tabEls}</div>
    <div class="empty">
      <div class="icon">
        <svg viewBox="0 0 24 24" width="38" height="38"><path fill="currentColor" d="M14 6V4H6v2H2v14h20V6h-8zM6 8h12v10H6V8z"/></svg>
      </div>
      <div class="title-lg">Nenhuma vaga recomendada encontrada</div>
      <div class="subtitle">Complete seu perfil para receber recomendações personalizadas</div>
    </div>
  `;
}

function Perfil(){
  setTitle('Perfil');
  setBack(true);
  return `
    <div class="card">
      <div class="title-lg">Seu Perfil</div>
      <div class="section-title">Dados básicos</div>
      <div class="grid">
        <input class="input" placeholder="Nome completo">
        <input class="input" placeholder="E-mail">
        <input class="input" placeholder="Telefone">
      </div>
      <div style="height:12px"></div>
      <button class="btn">Salvar</button>
    </div>
  `;
}

// Render
function render(path){
  const app = document.getElementById('app');
  setActiveTab(path === '/' ? '/' : path.split('/')[1].startsWith('vagas')? '/vagas':'/'+path.split('/')[1]);
  switch(true){
    case path === '/': app.innerHTML = Home(); break;
    case path.startsWith('/vagas/recomendadas') || path.startsWith('/vagas/em-alta') || path.startsWith('/vagas/urgentes'): app.innerHTML = VagasParaVoce(); break;
    case path.startsWith('/vagas'): app.innerHTML = VagasList(); break;
    case path.startsWith('/candidaturas'): app.innerHTML = Candidaturas(); break;
    case path.startsWith('/funcoes'): app.innerHTML = Funcoes(); break;
    case path.startsWith('/notificacoes'): app.innerHTML = Notificacoes(); break;
    case path.startsWith('/perfil'): app.innerHTML = Perfil(); break;
    default: app.innerHTML = Home();
  }
}

document.querySelectorAll('.nav-item').forEach(el => {
  el.addEventListener('click', () => router.go(el.dataset.path));
});

// PWA install prompt handling
let deferredPrompt;
const banner = document.getElementById('installBanner');
const btnInstall = document.getElementById('installBtn');
const btnDismiss = document.getElementById('dismissInstall');

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  banner.hidden = false;
});

btnInstall?.addEventListener('click', async () => {
  if(!deferredPrompt) return;
  deferredPrompt.prompt();
  await deferredPrompt.userChoice;
  banner.hidden = true;
  deferredPrompt = null;
});

btnDismiss?.addEventListener('click', ()=> banner.hidden = true);

// Service worker registration
if('serviceWorker' in navigator){
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js');
  });
}

// Start router
router.start();
