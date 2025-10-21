# 🎨 Arquitetura Híbrida - Inspiração Canva

## 📖 Visão Geral

Este documento explica como funciona a arquitetura híbrida do Canva, que mistura aplicativo instalado no computador com aplicativo na web, e como podemos aplicar os mesmos conceitos no Eventix.

---

## 🏗️ Como o Canva Funciona

### **1. Aplicativo Web (Principal)**

O Canva é **primariamente uma aplicação web** (SaaS - Software as a Service):

- ✅ Interface roda no navegador
- ✅ Dados armazenados na nuvem
- ✅ Acesso de qualquer dispositivo
- ✅ Sem necessidade de instalação
- ✅ Atualizações automáticas e instantâneas
- ✅ Multiplataforma por natureza

**Acesso:** [https://www.canva.com](https://www.canva.com)

---

### **2. Aplicativo Desktop (Wrapper Electron)**

O app de desktop é basicamente um **wrapper** que empacota a aplicação web dentro de um navegador:

**Tecnologia Utilizada: Electron.js**

- Empacota a aplicação web dentro de um navegador Chromium
- Adiciona funcionalidades nativas do sistema operacional
- Permite ícone na área de trabalho e integração com o SO
- Acesso a recursos do computador (arquivos, notificações, etc.)

---

## 🔄 Diagrama da Arquitetura

```
┌─────────────────────────────────────┐
│   Aplicativo Desktop do Canva       │
├─────────────────────────────────────┤
│  Electron (Chromium + Node.js)      │
│  ├─ Interface Web (mesma do browser)│
│  ├─ Acesso a APIs nativas do SO     │
│  ├─ Cache local para offline        │
│  └─ Sincronização automática        │
└─────────────────────────────────────┘
              ↕ Internet (HTTPS)
┌─────────────────────────────────────┐
│   Servidores Canva (Cloud)          │
│  ├─ Backend (API REST/GraphQL)      │
│  ├─ Banco de Dados (PostgreSQL)     │
│  ├─ Storage (imagens, assets)       │
│  ├─ CDN para distribuição global    │
│  └─ Processamento de renderização   │
└─────────────────────────────────────┘
```

---

## 🎯 Vantagens da Arquitetura Híbrida

### **Aplicativo Web:**

| Vantagem | Descrição |
|----------|-----------|
| ✅ Acesso Universal | Funciona em qualquer navegador moderno |
| ✅ Atualizações Instantâneas | Deploy imediato para todos os usuários |
| ✅ Multiplataforma | Windows, Mac, Linux, tablets, etc. |
| ✅ Zero Instalação | Basta acessar a URL |
| ✅ Sem Compatibilidade | Não precisa se preocupar com versões do SO |
| ✅ Manutenção Única | Um código para todas as plataformas |

### **Aplicativo Desktop (Electron):**

| Vantagem | Descrição |
|----------|-----------|
| ✅ Acesso Offline | Funciona sem internet (modo limitado) |
| ✅ Integração com SO | Acesso a sistema de arquivos local |
| ✅ Notificações Nativas | Notificações do sistema operacional |
| ✅ Performance | Cache local melhora a velocidade |
| ✅ Atalhos Nativos | Integração com atalhos de teclado do SO |
| ✅ Arrastar e Soltar | Drag & drop de arquivos do computador |
| ✅ Impressão Nativa | Acesso direto a impressoras |
| ✅ Presença Visual | Ícone no desktop, barra de tarefas |

---

## 💻 Tecnologias Utilizadas

### **Backend (Servidor na Nuvem)**

```yaml
Linguagens:
  - Node.js / Python / Java / Go
  
Banco de Dados:
  - PostgreSQL (dados estruturados)
  - MongoDB (dados não estruturados)
  - Redis (cache e sessões)
  
Storage:
  - AWS S3 / Google Cloud Storage
  - CDN (CloudFlare, Akamai)
  
Infraestrutura:
  - AWS / Google Cloud / Azure
  - Kubernetes para orquestração
  - Load Balancers
  - Auto-scaling
```

### **Frontend Web**

```yaml
Framework:
  - React.js / Vue.js / Angular
  
Renderização Gráfica:
  - WebGL (gráficos 3D/2D acelerados)
  - Canvas API (desenho 2D)
  - SVG (vetores)
  
Tempo Real:
  - WebSockets (colaboração simultânea)
  - WebRTC (comunicação peer-to-peer)
  
State Management:
  - Redux / Vuex / MobX
  
Build Tools:
  - Webpack / Vite
  - TypeScript
```

### **Desktop App (Electron)**

```javascript
// Estrutura básica do Electron

const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    icon: path.join(__dirname, 'assets/icon.png')
  });

  // Opção 1: Carregar aplicação web remota
  mainWindow.loadURL('https://www.canva.com');
  
  // Opção 2: Carregar versão local otimizada
  // mainWindow.loadFile('dist/index.html');
  
  // Adicionar funcionalidades nativas
  setupNativeFeatures(mainWindow);
}

app.whenReady().then(createWindow);

function setupNativeFeatures(window) {
  // Acesso ao sistema de arquivos
  // Notificações nativas
  // Atalhos de teclado
  // Menu customizado
  // etc.
}
```

---

## 🔐 Como Sincronizam (Web + Desktop)

### **1. Mesma Base de Código**

```
┌────────────────────────────────┐
│     Frontend Compartilhado      │
│      (React Components)         │
├────────────────────────────────┤
│  • Mesmos componentes           │
│  • Mesma lógica de negócio      │
│  • Mesmo design system          │
└────────────────────────────────┘
         ↓                ↓
┌─────────────┐    ┌─────────────┐
│  Web Build  │    │Desktop Build│
│  (Browser)  │    │  (Electron) │
└─────────────┘    └─────────────┘
```

### **2. API Centralizada**

Ambos (web e desktop) fazem requisições para a **mesma API**:

```javascript
// Configuração da API (compartilhada)
const API_BASE_URL = 'https://api.canva.com/v1';

// Autenticação
const authToken = localStorage.getItem('auth_token');

// Requisição (mesma em web e desktop)
fetch(`${API_BASE_URL}/designs`, {
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  }
});
```

### **3. Autenticação Unificada**

```
Usuário faz login → Token JWT gerado → Salvo localmente
                                       ↓
                    Token usado em TODAS as requisições
                    (web, desktop, mobile)
```

### **4. Cache e Sincronização**

**Desktop App:**
```javascript
// Cache local com IndexedDB
const cache = await openDB('canva-cache');

// Salvar offline
await cache.put('designs', userDesigns);

// Sincronizar quando online
if (navigator.onLine) {
  await syncWithServer();
}
```

**Service Workers (PWA):**
```javascript
// Funciona também no navegador
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
```

---

## 📱 Arquitetura Completa (Multi-plataforma)

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Web Browser │  │Desktop App  │  │  Mobile iOS │  │Mobile Android│
│  (React)    │  │  (Electron) │  │  (Native)   │  │  (Native)   │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │                │
       └────────────────┴────────────────┴────────────────┘
                            ↓
              ┌─────────────────────────────┐
              │    API Gateway (Cloud)       │
              ├─────────────────────────────┤
              │  • Autenticação (OAuth/JWT) │
              │  • Rate Limiting            │
              │  • Load Balancing           │
              └─────────────────────────────┘
                            ↓
       ┌────────────────────┼────────────────────┐
       ↓                    ↓                    ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Designs API │  │  Users API   │  │ Assets API   │
│ (Microservice)│  │(Microservice)│  │(Microservice)│
└──────────────┘  └──────────────┘  └──────────────┘
       ↓                    ↓                    ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │  PostgreSQL  │  │  S3/CDN      │
│  (Designs)   │  │  (Users)     │  │  (Images)    │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🚀 Aplicando no Eventix

Você **já tem** a infraestrutura pronta!

### **Estrutura Atual do Eventix:**

```
eventix/
├── Backend (Django)          ✅ Pronto
│   ├── API REST (DRF)
│   ├── PostgreSQL
│   └── Deploy: Railway
│
├── Web (Dashboard)           ✅ Funcional
│   ├── Templates Django
│   └── Bootstrap + jQuery
│
├── Mobile (Flutter)          ✅ Em desenvolvimento
│   ├── iOS
│   └── Android
│
└── Desktop (Electron)        ✅ Estrutura existe
    └── desktop/electron-config.js
```

### **Para Implementar Arquitetura Híbrida:**

#### **1. Separar Frontend Web do Django**

```bash
# Criar aplicação React/Vue separada
npx create-react-app eventix-web
# ou
npm create vue@latest eventix-web
```

#### **2. Usar a Mesma API para Tudo**

```javascript
// Arquivo de configuração compartilhado
// src/config/api.js

export const API_CONFIG = {
  // Desenvolvimento local
  development: 'http://localhost:8000/api',
  
  // Produção (Railway)
  production: 'https://eventix-development.up.railway.app/api',
  
  // Electron desktop
  desktop: 'https://eventix-development.up.railway.app/api'
};

export const getApiUrl = () => {
  if (window.electron) return API_CONFIG.desktop;
  return process.env.NODE_ENV === 'production' 
    ? API_CONFIG.production 
    : API_CONFIG.development;
};
```

#### **3. Electron Wrapper**

```javascript
// desktop/main.js (Electron)

const { app, BrowserWindow } = require('electron');

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Em desenvolvimento: carrega localhost
  if (process.env.NODE_ENV === 'development') {
    win.loadURL('http://localhost:3000');
  } else {
    // Em produção: carrega build local
    win.loadFile('dist/index.html');
  }
  
  // Funcionalidades nativas
  setupFileSystem(win);
  setupNotifications(win);
  setupPrinting(win);
}

app.whenReady().then(createWindow);
```

---

## 🔑 Conceitos Principais

### **1. Progressive Web App (PWA)**

```javascript
// service-worker.js
// Permite funcionar offline mesmo no navegador

const CACHE_NAME = 'eventix-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/api/eventos/',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Cache first, network fallback
        return response || fetch(event.request);
      })
  );
});
```

### **2. Sincronização de Dados**

```javascript
// Sincronização entre dispositivos

class SyncManager {
  constructor() {
    this.apiUrl = getApiUrl();
    this.syncInterval = null;
  }

  async syncData() {
    try {
      // Buscar dados do servidor
      const serverData = await fetch(`${this.apiUrl}/sync/`, {
        headers: {
          'Authorization': `Bearer ${this.getToken()}`
        }
      }).then(r => r.json());

      // Atualizar cache local
      await this.updateLocalCache(serverData);

      // Enviar alterações locais para o servidor
      const localChanges = await this.getLocalChanges();
      if (localChanges.length > 0) {
        await this.pushChanges(localChanges);
      }

      console.log('✅ Sincronização concluída');
    } catch (error) {
      console.error('❌ Erro na sincronização:', error);
    }
  }

  startAutoSync(interval = 30000) {
    // Sincronizar a cada 30 segundos
    this.syncInterval = setInterval(() => {
      if (navigator.onLine) {
        this.syncData();
      }
    }, interval);
  }

  stopAutoSync() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }
  }
}
```

### **3. Detecção de Plataforma**

```javascript
// utils/platform.js
// Detectar onde a aplicação está rodando

export const Platform = {
  isElectron: () => {
    return window.electron !== undefined;
  },

  isWeb: () => {
    return !Platform.isElectron() && !Platform.isMobile();
  },

  isMobile: () => {
    return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
  },

  isOnline: () => {
    return navigator.onLine;
  },

  getPlatformName: () => {
    if (Platform.isElectron()) return 'desktop';
    if (Platform.isMobile()) return 'mobile';
    return 'web';
  }
};

// Uso:
if (Platform.isElectron()) {
  // Funcionalidades específicas do desktop
  enableFileSystemAccess();
} else if (Platform.isWeb()) {
  // Funcionalidades específicas da web
  enableSocialSharing();
}
```

---

## 🛠️ Implementação no Electron

### **Arquivo Principal (main.js)**

```javascript
const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'assets/icon.png'),
    backgroundColor: '#1a1a1a',
    show: false // Mostrar apenas quando carregar
  });

  // Produção: carrega build local
  mainWindow.loadFile('dist/index.html');
  
  // Desenvolvimento: carrega dev server
  // mainWindow.loadURL('http://localhost:3000');

  // Mostrar janela quando pronta
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Menu customizado
  createMenu();
}

// Funcionalidades nativas do SO
ipcMain.handle('select-file', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters: [
      { name: 'Images', extensions: ['jpg', 'png', 'gif'] },
      { name: 'Documents', extensions: ['pdf', 'doc', 'docx'] }
    ]
  });
  
  if (!result.canceled) {
    const filePath = result.filePaths[0];
    const fileContent = fs.readFileSync(filePath);
    return {
      path: filePath,
      content: fileContent.toString('base64')
    };
  }
});

// Salvar arquivo localmente
ipcMain.handle('save-file', async (event, data) => {
  const result = await dialog.showSaveDialog({
    defaultPath: data.filename,
    filters: data.filters
  });
  
  if (!result.canceled) {
    fs.writeFileSync(result.filePath, data.content);
    return { success: true, path: result.filePath };
  }
  return { success: false };
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
```

### **Arquivo Preload (preload.js)**

```javascript
// Ponte segura entre Electron e código web
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  // Identificar que está no Electron
  isElectron: true,
  
  // Abrir diálogo de arquivo
  selectFile: () => ipcRenderer.invoke('select-file'),
  
  // Salvar arquivo
  saveFile: (data) => ipcRenderer.invoke('save-file', data),
  
  // Notificações
  showNotification: (title, body) => {
    new Notification(title, { body });
  },
  
  // Informações do sistema
  platform: process.platform,
  version: process.versions.electron
});
```

### **Uso no Frontend**

```javascript
// No código React/Vue (funciona em web E desktop)

async function uploadImage() {
  // Verificar se está no Electron
  if (window.electron) {
    // Desktop: usar seletor nativo
    const file = await window.electron.selectFile();
    await uploadToServer(file.content);
  } else {
    // Web: usar input file HTML
    const input = document.createElement('input');
    input.type = 'file';
    input.onchange = (e) => {
      const file = e.target.files[0];
      uploadToServer(file);
    };
    input.click();
  }
}
```

---

## 📊 Fluxo de Dados Completo

### **Criando um Design (Exemplo)**

```
1. USUÁRIO CRIA DESIGN
   ↓
2. FRONTEND (Web/Desktop)
   - Valida dados localmente
   - Salva no cache local (offline-first)
   ↓
3. ENVIA PARA API
   POST /api/v1/designs
   Headers: { Authorization: Bearer token }
   Body: { name, elements, ... }
   ↓
4. BACKEND (Cloud)
   - Valida dados
   - Salva no banco PostgreSQL
   - Upload de imagens para S3/CDN
   - Retorna design_id
   ↓
5. SINCRONIZAÇÃO
   - WebSocket notifica outros dispositivos
   - Todos os apps do usuário recebem update
   - Cache atualizado automaticamente
   ↓
6. RESULTADO
   - Design disponível em TODOS os dispositivos
   - Web, Desktop, Mobile sincronizados
```

---

## 🎯 Benefícios para o Eventix

### **Cenário Ideal:**

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Web Browser    │  │  Mobile Flutter  │  │  Desktop Electron│
│   (Dashboard)    │  │  (Freelancers)   │  │  (Empresa)       │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ • Admin Empresa  │  │ • Buscar vagas   │  │ • Gestão offline │
│ • Criar eventos  │  │ • Candidaturas   │  │ • Impressão      │
│ • Relatórios     │  │ • Notificações   │  │ • Arquivos local │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                       │
         └─────────────────────┼───────────────────────┘
                               ↓
                    ┌─────────────────────┐
                    │  Backend Django      │
                    │  (API REST + Admin)  │
                    │  Railway Cloud       │
                    └──────────┬───────────┘
                               ↓
                    ┌─────────────────────┐
                    │  PostgreSQL + S3    │
                    │  (Dados + Arquivos) │
                    └─────────────────────┘
```

### **Vantagens:**

1. **Usuário da Empresa:**
   - Acessa via **Web** no escritório
   - Acessa via **Desktop** no evento (pode ter offline)
   - Dados sempre sincronizados

2. **Freelancer:**
   - Usa **Mobile** para buscar vagas
   - Recebe **notificações push**
   - Pode acessar via **Web** para tarefas complexas

3. **Admin do Sistema:**
   - Gerencia via **Web** (Django Admin)
   - Monitora em tempo real

---

## 🔧 Tecnologias Recomendadas

### **Para o Eventix:**

| Componente | Tecnologia Atual | Sugestão de Melhoria |
|------------|------------------|----------------------|
| Backend | ✅ Django + DRF | Manter (está ótimo) |
| Banco de Dados | ✅ PostgreSQL | Manter |
| Web Frontend | Templates Django | React/Vue (SPA) |
| Mobile | ✅ Flutter | Manter |
| Desktop | Electron básico | Melhorar wrapper |
| Deploy | ✅ Railway | Manter ou AWS |

### **Stack Moderna Sugerida:**

```yaml
Backend:
  - Django + Django REST Framework (atual)
  - PostgreSQL (atual)
  - Redis para cache
  - Celery para tarefas assíncronas

Frontend Web:
  - React.js ou Vue.js
  - TypeScript
  - Tailwind CSS ou Material-UI
  - Redux/Zustand para state

Desktop:
  - Electron (wrapper do frontend React/Vue)
  - Mesma base de código do web
  - Funcionalidades nativas adicionais

Mobile:
  - Flutter (atual)
  - Dart
  - Firebase (notificações)

Infraestrutura:
  - Railway (backend Django)
  - Vercel/Netlify (frontend estático)
  - AWS S3 (arquivos/uploads)
  - CloudFlare (CDN)
```

---

## 📚 Recursos e Referências

### **Electron:**
- [Documentação Oficial](https://www.electronjs.org/)
- [Electron Forge](https://www.electronforge.io/) - Template e ferramentas
- [Electron Builder](https://www.electron.build/) - Build e distribuição

### **PWA (Progressive Web Apps):**
- [Google PWA](https://web.dev/progressive-web-apps/)
- [Workbox](https://developers.google.com/web/tools/workbox) - Service Workers

### **Arquitetura:**
- [Microservices Pattern](https://microservices.io/)
- [API Gateway Pattern](https://microservices.io/patterns/apigateway.html)

---

## 💡 Próximos Passos para o Eventix

### **Fase 1: Melhorar o Existente**
1. ✅ Corrigir bugs atuais (já feito!)
2. ✅ Implementar CRUD completo (já feito!)
3. ✅ Sistema de funções nas vagas (já feito!)
4. ⏳ Testar no Railway

### **Fase 2: Modernizar Frontend**
1. Separar frontend em SPA (React/Vue)
2. Implementar PWA
3. Melhorar UX/UI

### **Fase 3: Desktop App**
1. Melhorar wrapper Electron existente
2. Adicionar funcionalidades offline
3. Integração com impressoras
4. Upload de arquivos drag-and-drop

### **Fase 4: Integração Total**
1. WebSockets para real-time
2. Notificações sincronizadas
3. Cache inteligente
4. Modo offline completo

---

## 🎓 Conclusão

A arquitetura híbrida do Canva é **simples mas poderosa**:

1. **Uma aplicação web bem feita** como base
2. **Electron empacota** essa web app para desktop
3. **Mesma API** serve todos os clientes
4. **Cache local** melhora performance
5. **Sincronização** mantém tudo atualizado

**O Eventix já tem 80% dessa arquitetura pronta!** Com algumas melhorias, você terá um sistema tão robusto quanto o Canva. 🚀

---

*Documento criado em: Outubro 2025*  
*Projeto: Eventix - Sistema de Gestão de Eventos*

