# 📱 Arquitetura PWA - Eventix (Futuro)

## 🎯 Visão Geral

O Eventix terá **dois PWAs separados** para diferentes tipos de usuários:

1. **PWA Freelancer** - Para profissionais independentes (✅ JÁ IMPLEMENTADO)
2. **PWA Empresa** - Para empresas contratantes (🔜 FUTURO)

---

## ✅ PWA Freelancer (Implementado)

### **Estrutura Atual**

- **URL de Acesso:** `/freelancer/app/`
- **Localização dos Arquivos:** `static/freelancer_pwa/`
- **Template Django:** `app_eventos/templates/freelancer_publico/pwa.html`
- **View:** `freelancer_pwa()` em `app_eventos/views_dashboard_freelancer_publico.py`
- **Manifest:** `static/freelancer_pwa/manifest.webmanifest`
- **Service Worker:** `static/freelancer_pwa/sw.js`

### **Configuração do Manifest**

```json
{
  "name": "Eventix Freelancer",
  "short_name": "Eventix Pro",
  "start_url": "/freelancer/app/",
  "scope": "/freelancer/app/",
  "display": "standalone",
  "theme_color": "#6B63FF"
}
```

### **Rotas**

- `/freelancer/app/` - PWA principal
- `/freelancer/login/` - Login
- `/freelancer/dashboard/` - Dashboard (web)
- `/freelancer/vagas/` - Vagas disponíveis
- `/freelancer/candidaturas/` - Minhas candidaturas

---

## 🔜 PWA Empresa (Futuro)

### **Estrutura Planejada**

- **URL de Acesso:** `/empresa/app/`
- **Localização dos Arquivos:** `static/empresa_pwa/`
- **Template Django:** `app_eventos/templates/empresa/pwa.html`
- **View:** `empresa_pwa()` em `app_eventos/views_dashboard_empresa.py`
- **Manifest:** `static/empresa_pwa/manifest.webmanifest`
- **Service Worker:** `static/empresa_pwa/sw.js`

### **Configuração do Manifest (Planejada)**

```json
{
  "name": "Eventix Empresa",
  "short_name": "Eventix Emp",
  "start_url": "/empresa/app/",
  "scope": "/empresa/app/",
  "display": "standalone",
  "theme_color": "#0EA5E9"
}
```

### **Rotas (Planejadas)**

- `/empresa/app/` - PWA principal
- `/empresa/login/` - Login
- `/empresa/dashboard/` - Dashboard (web)
- `/empresa/eventos/` - Gestão de eventos
- `/empresa/vagas/` - Gestão de vagas
- `/empresa/candidaturas/` - Candidaturas recebidas
- `/empresa/financeiro/` - Gestão financeira

---

## 🏗️ Estrutura de Diretórios (Futura)

```
static/
├── freelancer_pwa/          # ✅ PWA Freelancer (implementado)
│   ├── manifest.webmanifest
│   ├── sw.js
│   ├── app.js
│   ├── styles.css
│   └── index.html
│
├── empresa_pwa/             # 🔜 PWA Empresa (futuro)
│   ├── manifest.webmanifest
│   ├── sw.js
│   ├── app.js
│   ├── styles.css
│   └── index.html
│
└── icons/                   # Ícones compartilhados
    ├── icon-192x192.png
    ├── icon-512x512.png
    ├── icon-maskable-192x192.png
    └── icon-maskable-512x512.png
```

---

## 🔧 Implementação Futura do PWA Empresa

### **Passo 1: Criar Estrutura de Diretórios**

```bash
mkdir -p static/empresa_pwa
```

### **Passo 2: Criar Manifest**

Criar `static/empresa_pwa/manifest.webmanifest`:

```json
{
  "name": "Eventix Empresa",
  "short_name": "Eventix Emp",
  "description": "Experiência PWA da empresa Eventix com gestão de eventos, vagas e candidaturas.",
  "start_url": "/empresa/app/",
  "scope": "/empresa/app/",
  "display": "standalone",
  "background_color": "#FFFFFF",
  "theme_color": "#0EA5E9",
  "orientation": "portrait-primary",
  "lang": "pt-BR",
  "icons": [
    {
      "src": "/static/icons/icon-empresa-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/static/icons/icon-empresa-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    }
  ],
  "shortcuts": [
    {
      "name": "Criar evento",
      "url": "/empresa/app/?action=create-event",
      "icons": [{"src": "/static/icons/icon-event-96x96.png", "sizes": "96x96"}]
    },
    {
      "name": "Candidaturas",
      "url": "/empresa/app/?action=candidaturas",
      "icons": [{"src": "/static/icons/icon-candidaturas-96x96.png", "sizes": "96x96"}]
    }
  ]
}
```

### **Passo 3: Criar Service Worker**

Criar `static/empresa_pwa/sw.js`:

```javascript
const CACHE_NAME = 'eventix-empresa-pwa-v1';
const STATIC_ASSETS = [
  '/empresa/app/',
  '/static/empresa_pwa/styles.css',
  '/static/empresa_pwa/app.js',
  '/static/empresa_pwa/manifest.webmanifest',
  '/static/icons/icon-empresa-192x192.png',
  '/static/icons/icon-empresa-512x512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

### **Passo 4: Criar View**

Adicionar em `app_eventos/views_dashboard_empresa.py`:

```python
def empresa_pwa(request):
    """PWA da empresa (interface baseada no app Flutter)"""
    empresa = None
    if request.user.is_authenticated:
        if hasattr(request.user, 'empresa_contratante'):
            empresa = request.user.empresa_contratante
    return render(request, 'empresa/pwa.html', {'empresa': empresa})
```

### **Passo 5: Adicionar Rota**

Adicionar em `app_eventos/urls_dashboard_empresa.py`:

```python
urlpatterns = [
    # ... rotas existentes
    path('app/', views_dashboard_empresa.empresa_pwa, name='pwa'),
    # ... outras rotas
]
```

### **Passo 6: Criar Template**

Criar `app_eventos/templates/empresa/pwa.html`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eventix Empresa</title>
    <link rel="manifest" href="/static/empresa_pwa/manifest.webmanifest">
    <meta name="theme-color" content="#0EA5E9">
    <link rel="stylesheet" href="/static/empresa_pwa/styles.css">
</head>
<body>
    <div id="app"></div>
    <script src="/static/empresa_pwa/app.js"></script>
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/empresa_pwa/sw.js');
        }
    </script>
</body>
</html>
```

---

## 🎨 Diferenças Visuais entre PWAs

### **PWA Freelancer**
- **Tema:** Roxo (#6B63FF)
- **Foco:** Vagas, Candidaturas, Perfil
- **Orientação:** Portrait (mobile-first)
- **Ícone:** Ícone com símbolo de freelancer

### **PWA Empresa**
- **Tema:** Azul (#0EA5E9)
- **Foco:** Eventos, Vagas, Candidaturas, Financeiro
- **Orientação:** Portrait (mobile-first)
- **Ícone:** Ícone com símbolo de empresa

---

## 🔄 Fluxo de Redirecionamento

### **Na Home (`/`)**

```javascript
// Botão "Área do Freelancer"
if (isMobile()) {
    window.location.href = "/freelancer/app/";  // PWA Freelancer
} else {
    window.location.href = "/freelancer/login/";  // Web Login
}

// Botão "Área da Empresa" (futuro)
if (isMobile()) {
    window.location.href = "/empresa/app/";  // PWA Empresa
} else {
    window.location.href = "/empresa/login/";  // Web Login
}
```

---

## 📋 Checklist de Implementação (PWA Empresa)

### **Fase 1: Preparação**
- [ ] Criar diretório `static/empresa_pwa/`
- [ ] Criar ícones específicos para empresa
- [ ] Documentar funcionalidades necessárias

### **Fase 2: Estrutura Base**
- [ ] Criar `manifest.webmanifest`
- [ ] Criar `sw.js` (Service Worker)
- [ ] Criar `pwa.html` (Template Django)
- [ ] Criar view `empresa_pwa()`

### **Fase 3: Interface**
- [ ] Criar `app.js` (JavaScript principal)
- [ ] Criar `styles.css` (Estilos)
- [ ] Implementar navegação
- [ ] Implementar autenticação

### **Fase 4: Funcionalidades**
- [ ] Lista de eventos
- [ ] Criação de eventos
- [ ] Gestão de vagas
- [ ] Visualização de candidaturas
- [ ] Aprovação/rejeição de candidaturas
- [ ] Dashboard financeiro

### **Fase 5: Testes**
- [ ] Testar instalação PWA
- [ ] Testar offline
- [ ] Testar em diferentes dispositivos
- [ ] Testar autenticação
- [ ] Testar notificações push (se aplicável)

---

## 🔐 Autenticação

### **PWA Freelancer**
- Login em `/freelancer/login/`
- Redireciona para `/freelancer/app/` após login
- Verifica perfil de freelancer

### **PWA Empresa**
- Login em `/empresa/login/`
- Redireciona para `/empresa/app/` após login
- Verifica perfil de empresa (admin_empresa ou operador_empresa)

---

## 📱 Instalação

### **PWA Freelancer**
1. Acessar `/freelancer/app/`
2. Banner "Adicionar à tela inicial" aparece
3. Instalar no dispositivo
4. Ícone aparece na tela inicial

### **PWA Empresa (Futuro)**
1. Acessar `/empresa/app/`
2. Banner "Adicionar à tela inicial" aparece
3. Instalar no dispositivo
4. Ícone aparece na tela inicial

---

## 🎯 Vantagens da Arquitetura Separada

1. **Isolamento:** Cada PWA é independente
2. **Manutenção:** Mais fácil de manter e atualizar
3. **Performance:** Menor bundle size por PWA
4. **Customização:** Cada PWA pode ter seu próprio tema e funcionalidades
5. **Segurança:** Escopo separado por tipo de usuário
6. **UX:** Experiência otimizada para cada tipo de usuário

---

## 📝 Notas Importantes

1. **Service Workers Separados:** Cada PWA tem seu próprio service worker com escopo específico
2. **Manifests Separados:** Cada PWA tem seu próprio manifest com configurações específicas
3. **Templates Separados:** Cada PWA tem seu próprio template HTML
4. **Rotas Separadas:** Cada PWA tem suas próprias rotas (`/freelancer/app/` e `/empresa/app/`)
5. **Ícones Separados:** Cada PWA pode ter seus próprios ícones (opcional)

---

**Última atualização:** Janeiro 2025
**Status:** PWA Freelancer ✅ Implementado | PWA Empresa 🔜 Futuro


