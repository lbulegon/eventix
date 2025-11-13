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
function setBack(show){ 
  if(backBtn) backBtn.hidden = !show; 
}
function setActiveTab(path){
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.path === path);
  });
}

// Views
function Home(){
  setTitle('Eventix');
  setBack(false);
  const userName = getUserName() || 'Usuário';
  return `
    <div class="welcome-card">
      <h2>Olá, ${userName}!</h2>
      <p>Bem-vindo ao Eventix</p>
    </div>
    
    <div class="action-card" onclick="router.go('/vagas/recomendadas')" style="margin-bottom:12px;">
      <svg class="action-card-icon" viewBox="0 0 24 24" width="32" height="32">
        <path fill="currentColor" d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
      </svg>
      <div class="action-card-title">Oportunidades e recomendações</div>
      <div class="action-card-subtitle">Vagas escolhidas especialmente para você</div>
    </div>
    
    <div class="cards-row" style="margin-bottom:12px;">
      <div class="action-card" onclick="router.go('/vagas')">
        <svg class="action-card-icon" viewBox="0 0 24 24" width="32" height="32">
          <path fill="currentColor" d="M14 6V4H6v2H2v14h20V6h-8zM6 8h12v10H6V8z"/>
        </svg>
        <div class="action-card-title">Todas as Vagas</div>
        <div class="action-card-subtitle">Buscar oportunidades</div>
      </div>
      <div class="action-card" onclick="router.go('/candidaturas')">
        <svg class="action-card-icon" viewBox="0 0 24 24" width="32" height="32">
          <path fill="currentColor" d="M19 3H5a2 2 0 0 0-2 2v14l4-4h12a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z"/>
        </svg>
        <div class="action-card-title">Minhas Candidaturas</div>
        <div class="action-card-subtitle">Acompanhe status</div>
      </div>
    </div>
    
    <div class="action-card" onclick="router.go('/funcoes')">
      <svg class="action-card-icon" viewBox="0 0 24 24" width="32" height="32">
        <path fill="currentColor" d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
      </svg>
      <div class="action-card-title">Funções</div>
      <div class="action-card-subtitle">Configure suas especialidades</div>
    </div>
  `;
}

function getUserName(){
  // Tenta obter o nome do usuário do localStorage ou de uma API
  try {
    const user = localStorage.getItem('user');
    if(user){
      const userData = JSON.parse(user);
      return userData.nome || userData.name || null;
    }
  } catch(e){
    console.error('Erro ao obter nome do usuário:', e);
  }
  return null;
}

function handleLogout(){
  if(confirm('Tem certeza que deseja sair?')){
    // Limpar dados do usuário
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    // Redirecionar para login
    window.location.href = '/';
  }
}

function VagasList(){
  setTitle('Vagas Disponíveis');
  setBack(false);
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
  setBack(false);
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
  setBack(false);
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
  setBack(false);
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
  setBack(false);
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
  setBack(false);
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
  const pathParts = path.split('/').filter(p => p);
  let activePath = '/';
  
  if(path === '/') {
    activePath = '/';
  } else if(pathParts[0] === 'vagas') {
    activePath = '/vagas';
  } else if(pathParts[0] === 'candidaturas') {
    activePath = '/candidaturas';
  } else if(pathParts[0] === 'perfil') {
    activePath = '/perfil';
  }
  
  setActiveTab(activePath);
  
  switch(true){
    case path === '/': 
      setBack(false);
      app.innerHTML = Home(); 
      break;
    case path.startsWith('/vagas/recomendadas') || path.startsWith('/vagas/em-alta') || path.startsWith('/vagas/urgentes'): 
      setBack(true);
      app.innerHTML = VagasParaVoce(); 
      break;
    case path.startsWith('/vagas'): 
      setBack(false);
      app.innerHTML = VagasList(); 
      break;
    case path.startsWith('/candidaturas'): 
      setBack(false);
      app.innerHTML = Candidaturas(); 
      break;
    case path.startsWith('/funcoes'): 
      setBack(false);
      app.innerHTML = Funcoes(); 
      break;
    case path.startsWith('/notificacoes'): 
      setBack(true);
      app.innerHTML = Notificacoes(); 
      break;
    case path.startsWith('/perfil'): 
      setBack(false);
      app.innerHTML = Perfil(); 
      break;
    default: 
      setBack(false);
      app.innerHTML = Home();
  }
}

document.querySelectorAll('.nav-item').forEach(el => {
  el.addEventListener('click', () => router.go(el.dataset.path));
});

// PWA install prompt handling
let deferredPrompt = null;

// Verifica se o app já está instalado
function isAppInstalled() {
  // Verifica se foi instalado anteriormente (salvo no localStorage) - PRIORIDADE MÁXIMA
  // Esta é a verificação mais importante para evitar mostrar o banner novamente
  if (localStorage.getItem('pwa-installed') === 'true') {
    console.log('PWA já está instalado (verificado via localStorage)');
    return true;
  }
  
  // Verifica se está rodando em modo standalone (instalado)
  // Este é o modo mais confiável para detectar PWA instalado
  try {
    if (window.matchMedia('(display-mode: standalone)').matches) {
      console.log('PWA está rodando em modo standalone');
      localStorage.setItem('pwa-installed', 'true');
      return true;
    }
  } catch (e) {
    console.error('Erro ao verificar display-mode:', e);
  }
  
  // Verifica no iOS Safari (modo standalone)
  if (window.navigator.standalone === true) {
    console.log('PWA está rodando no iOS em modo standalone');
    localStorage.setItem('pwa-installed', 'true');
    return true;
  }
  
  // Verifica se está em modo fullscreen (outra forma de PWA instalado)
  try {
    if (window.matchMedia('(display-mode: fullscreen)').matches) {
      console.log('PWA está rodando em modo fullscreen');
      localStorage.setItem('pwa-installed', 'true');
      return true;
    }
  } catch (e) {
    console.error('Erro ao verificar fullscreen:', e);
  }
  
  // Verifica se está em modo minimal-ui (outro indicador)
  try {
    if (window.matchMedia('(display-mode: minimal-ui)').matches) {
      console.log('PWA está rodando em modo minimal-ui');
      localStorage.setItem('pwa-installed', 'true');
      return true;
    }
  } catch (e) {
    // Ignora erro
  }
  
  return false;
}

// Verifica se o usuário já rejeitou a instalação
function hasUserDismissed() {
  return localStorage.getItem('pwa-install-dismissed') === 'true';
}

// Esconde o banner se já estiver instalado ou se o usuário rejeitou
function checkInstallStatus() {
  const installed = isAppInstalled();
  const dismissed = hasUserDismissed();
  return installed || dismissed;
}

// Força o banner a ficar oculto
function hideBanner() {
  const banner = document.getElementById('installBanner');
  if (banner) {
    banner.hidden = true;
    banner.style.display = 'none';
    console.log('Banner de instalação ocultado');
  }
}

// Atualiza o estado do banner
function updateBannerState() {
  if (checkInstallStatus()) {
    hideBanner();
    return true; // Banner oculto
  }
  return false; // Banner pode ser mostrado
}

// Variável global para o intervalo de verificação
let installCheckInterval = null;

// Para o intervalo de verificação
function stopInstallCheck() {
  if (installCheckInterval) {
    clearInterval(installCheckInterval);
    installCheckInterval = null;
  }
}

// Inicializa o sistema de instalação PWA
function initPWAInstall() {
  const banner = document.getElementById('installBanner');
  const btnInstall = document.getElementById('installBtn');
  const btnDismiss = document.getElementById('dismissInstall');
  
  if (!banner) {
    console.log('Banner de instalação não encontrado');
    return;
  }
  
  // SEMPRE esconde o banner primeiro
  hideBanner();
  
  // Verifica imediatamente se já está instalado ou rejeitado
  const isInstalled = checkInstallStatus();
  console.log('Status de instalação:', {
    installed: isInstalled,
    dismissed: hasUserDismissed(),
    localStorage: localStorage.getItem('pwa-installed')
  });
  
  // Se já estiver instalado, não faz mais nada
  if (isInstalled) {
    console.log('PWA já está instalado ou foi rejeitado. Banner não será mostrado.');
    return;
  }
  
  // Detecta quando o app é instalado (evento padrão do PWA)
  window.addEventListener('appinstalled', (evt) => {
    console.log('Evento appinstalled disparado - PWA instalado com sucesso', evt);
    localStorage.setItem('pwa-installed', 'true');
    hideBanner();
    deferredPrompt = null;
    stopInstallCheck();
  });
  
  // Listener para o prompt de instalação (ANTES de prevenir o padrão)
  window.addEventListener('beforeinstallprompt', (e) => {
    console.log('Evento beforeinstallprompt recebido');
    
    // Verifica novamente se já está instalado
    if (checkInstallStatus()) {
      console.log('PWA já instalado, ignorando beforeinstallprompt');
      return;
    }
    
    // Previne o prompt padrão do navegador
    e.preventDefault();
    deferredPrompt = e;
    
    // Mostra o banner apenas se ainda não foi rejeitado e não está instalado
    if (!hasUserDismissed() && !isAppInstalled()) {
      console.log('Mostrando banner de instalação em 3 segundos');
      // Aguarda um pouco antes de mostrar o banner (deixa usuário ver a página primeiro)
      setTimeout(() => {
        // Verifica novamente antes de mostrar
        if (!checkInstallStatus() && banner) {
          banner.hidden = false;
          banner.style.display = 'flex';
          console.log('Banner de instalação exibido');
        } else {
          console.log('Banner não será mostrado (já instalado ou rejeitado)');
        }
      }, 3000); // Mostra após 3 segundos
    } else {
      console.log('Banner não será mostrado:', {
        dismissed: hasUserDismissed(),
        installed: isAppInstalled()
      });
    }
  });
  
  // Verifica periodicamente se o app foi instalado (útil se usuário instalou pelo menu do navegador)
  installCheckInterval = setInterval(() => {
    if (isAppInstalled()) {
      console.log('PWA instalado detectado durante verificação periódica');
      hideBanner();
      stopInstallCheck();
    }
  }, 1000); // Verifica a cada 1 segundo
  
  // Para de verificar após 30 segundos para não consumir recursos desnecessariamente
  setTimeout(() => {
    stopInstallCheck();
  }, 30000);
  
  // Botão de instalação
  if (btnInstall) {
    btnInstall.addEventListener('click', async () => {
      if (!deferredPrompt) {
        // Se não tiver o prompt, mostra instruções
        if (window.navigator.userAgent.includes('Android')) {
          alert('Para instalar o app no Android:\n\n1. Toque no menu (três pontos)\n2. Selecione "Adicionar à tela inicial" ou "Instalar app"');
        } else {
          alert('Para instalar o app, use o menu do navegador e selecione "Adicionar à tela inicial"');
        }
        return;
      }
      
      try {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        
        if (outcome === 'accepted') {
          console.log('Usuário aceitou a instalação');
          localStorage.setItem('pwa-installed', 'true');
          hideBanner();
        } else {
          console.log('Usuário rejeitou a instalação');
        }
      } catch (error) {
        console.error('Erro ao instalar PWA:', error);
      }
      
      deferredPrompt = null;
    });
  }
  
  // Botão de rejeitar
  if (btnDismiss) {
    btnDismiss.addEventListener('click', () => {
      console.log('Usuário rejeitou a instalação');
      localStorage.setItem('pwa-install-dismissed', 'true');
      hideBanner();
      deferredPrompt = null;
    });
  }
  
  // Monitora mudanças na visualização para detectar instalação
  let resizeTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      if (isAppInstalled()) {
        console.log('PWA instalado detectado durante resize');
        hideBanner();
        stopInstallCheck();
      }
    }, 500);
  });
  
  // Verifica quando a página ganha foco (pode indicar que foi instalado)
  window.addEventListener('focus', () => {
    if (isAppInstalled()) {
      console.log('PWA instalado detectado quando página ganhou foco');
      hideBanner();
      stopInstallCheck();
    }
  });
  
  // Verifica quando a página é carregada (pode ter sido instalada enquanto estava fechada)
  window.addEventListener('load', () => {
    if (isAppInstalled()) {
      console.log('PWA instalado detectado no carregamento da página');
      hideBanner();
      stopInstallCheck();
    }
  });
}

// Função para esconder banner imediatamente se já estiver instalado
function hideBannerIfInstalled() {
  const banner = document.getElementById('installBanner');
  if (banner && (isAppInstalled() || hasUserDismissed())) {
    hideBanner();
    return true;
  }
  return false;
}

// Esconde o banner imediatamente se necessário (ANTES de tudo)
if (document.readyState === 'loading') {
  // Se o DOM ainda está carregando, esconde o banner assim que possível
  document.addEventListener('DOMContentLoaded', () => {
    hideBannerIfInstalled();
    initPWAInstall();
  });
} else {
  // DOM já está carregado, esconde imediatamente
  hideBannerIfInstalled();
  initPWAInstall();
}

// Também esconde quando a página é totalmente carregada
window.addEventListener('load', () => {
  hideBannerIfInstalled();
});

// Service worker registration
if('serviceWorker' in navigator){
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js');
  });
}

// Start router
router.start();
