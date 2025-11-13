# 📱 Entendimento do Fluxo PWA - Eventix

## 🎯 Arquitetura Atual e Futura

O Eventix utilizará **dois PWAs separados** para diferentes tipos de usuários:

1. **PWA Freelancer** - ✅ **IMPLEMENTADO** (em uso)
2. **PWA Empresa** - 🔜 **FUTURO** (planejado)

> 📖 **Documentação Completa:** Veja [PWA_ARQUITETURA_FUTURA.md](./PWA_ARQUITETURA_FUTURA.md) para detalhes da arquitetura futura.

---

## 🔍 Situação Atual

### **1. PWA do Freelancer** ✅ (Implementado e em uso)
- **Localização:** `static/freelancer_pwa/`
- **URL de acesso:** `/freelancer/app/`
- **Template Django:** `app_eventos/templates/freelancer_publico/pwa.html`
- **View:** `freelancer_pwa()` em `views_dashboard_freelancer_publico.py`
- **Manifest:** `static/freelancer_pwa/manifest.webmanifest`
  - `start_url`: `/freelancer/app/`
  - `scope`: `/freelancer/app/`
  - `theme_color`: `#6B63FF` (roxo)
- **Service Worker:** `static/freelancer_pwa/sw.js`

### **2. Dashboard Empresa** (Web tradicional)
- **URL:** `/empresa/dashboard/`
- **Status:** ✅ Funcional (apenas web)
- **PWA:** ❌ Não implementado (planejado para o futuro)

### **3. View `home()` na raiz**
- **URL:** `/`
- **Função:** Redireciona baseado no tipo de usuário
  - Não autenticado → Mostra `home.html`
  - Freelancer → Redireciona para `/freelancer/dashboard/`
  - Empresa → Redireciona para `/empresa/dashboard/`
  - Admin Sistema → Redireciona para `/admin/`

### **4. Redirecionamento Inteligente na Home**
- **Botão "Área do Freelancer":**
  - **Mobile/Android** → Redireciona para `/freelancer/app/` (PWA)
  - **Desktop** → Redireciona para `/freelancer/login/` (Web)
- **Botão "Área da Empresa":**
  - **Mobile/Android** → Redireciona para `/empresa/login/` (Web - PWA futuro)
  - **Desktop** → Redireciona para `/empresa/login/` (Web)

---

## ✅ Arquitetura Implementada

### **PWA Freelancer (Atual)**

**Estrutura:**
```
static/freelancer_pwa/
├── manifest.webmanifest
├── sw.js
├── app.js
├── styles.css
└── index.html (referência)
```

**Funcionalidades:**
- ✅ Instalação PWA
- ✅ Funciona offline (Service Worker)
- ✅ Interface mobile-first
- ✅ Autenticação integrada
- ✅ Gestão de vagas e candidaturas
- ✅ Perfil do freelancer

**Rotas:**
- `/freelancer/app/` - PWA principal
- `/freelancer/login/` - Login
- `/freelancer/dashboard/` - Dashboard (web)
- `/freelancer/vagas/` - Vagas disponíveis
- `/freelancer/candidaturas/` - Minhas candidaturas

---

## 🔜 Arquitetura Futura (PWA Empresa)

### **Planejamento**

**Estrutura Planejada:**
```
static/empresa_pwa/
├── manifest.webmanifest
├── sw.js
├── app.js
├── styles.css
└── index.html (referência)
```

**Funcionalidades Planejadas:**
- 🔜 Instalação PWA
- 🔜 Funciona offline (Service Worker)
- 🔜 Interface mobile-first
- 🔜 Autenticação integrada
- 🔜 Gestão de eventos
- 🔜 Gestão de vagas
- 🔜 Gestão de candidaturas
- 🔜 Dashboard financeiro

**Rotas Planejadas:**
- `/empresa/app/` - PWA principal
- `/empresa/login/` - Login
- `/empresa/dashboard/` - Dashboard (web)
- `/empresa/eventos/` - Gestão de eventos
- `/empresa/vagas/` - Gestão de vagas
- `/empresa/candidaturas/` - Candidaturas recebidas

> 📖 **Para mais detalhes sobre a implementação futura, consulte [PWA_ARQUITETURA_FUTURA.md](./PWA_ARQUITETURA_FUTURA.md)**

---

## 📋 Resumo dos Links

### **Links Atuais:**

- **Raiz:** `https://eventix-development.up.railway.app/`
  - Redireciona baseado no tipo de usuário
  - Não tem PWA configurado (apenas redirecionamento)
  
- **PWA Freelancer:** `https://eventix-development.up.railway.app/freelancer/app/`
  - ✅ Tem PWA configurado
  - ✅ Funciona para freelancers
  - ✅ Pode ser instalado no dispositivo

- **Dashboard Empresa:** `https://eventix-development.up.railway.app/empresa/dashboard/`
  - ✅ Funciona (web tradicional)
  - ❌ Não tem PWA configurado (planejado para o futuro)

### **Links Futuros:**

- **PWA Empresa:** `https://eventix-development.up.railway.app/empresa/app/`
  - 🔜 Será implementado no futuro
  - 🔜 Funcionará para empresas
  - 🔜 Poderá ser instalado no dispositivo

---

## 🎯 Vantagens da Arquitetura Separada

1. **Isolamento:** Cada PWA é independente
2. **Manutenção:** Mais fácil de manter e atualizar
3. **Performance:** Menor bundle size por PWA
4. **Customização:** Cada PWA pode ter seu próprio tema e funcionalidades
5. **Segurança:** Escopo separado por tipo de usuário
6. **UX:** Experiência otimizada para cada tipo de usuário

---

## 🔄 Fluxo de Redirecionamento

### **Na Home (`/`)**

**Botão "Área do Freelancer":**
```javascript
// Detecta dispositivo
if (isMobile() || isAndroid()) {
    // Mobile/Android → PWA
    window.location.href = "/freelancer/app/";
} else {
    // Desktop → Web Login
    window.location.href = "/freelancer/login/";
}
```

**Botão "Área da Empresa":**
```javascript
// Atualmente sempre redireciona para web
// No futuro, quando PWA Empresa estiver implementado:
if (isMobile() || isAndroid()) {
    // Mobile/Android → PWA (futuro)
    window.location.href = "/empresa/app/";
} else {
    // Desktop → Web Login
    window.location.href = "/empresa/login/";
}
```

---

## 🔐 Autenticação

### **PWA Freelancer**
- Login em `/freelancer/login/`
- Redireciona para `/freelancer/app/` após login
- Verifica perfil de freelancer
- Se já autenticado, redireciona automaticamente para dashboard

### **PWA Empresa (Futuro)**
- Login em `/empresa/login/`
- Redireciona para `/empresa/app/` após login (futuro)
- Verifica perfil de empresa (admin_empresa ou operador_empresa)
- Se já autenticado, redireciona automaticamente para dashboard

---

## 📱 Instalação

### **PWA Freelancer**
1. Acessar `/freelancer/app/` no dispositivo móvel
2. Banner "Adicionar à tela inicial" aparece
3. Instalar no dispositivo
4. Ícone aparece na tela inicial
5. Abre em modo standalone

### **PWA Empresa (Futuro)**
1. Acessar `/empresa/app/` no dispositivo móvel
2. Banner "Adicionar à tela inicial" aparece
3. Instalar no dispositivo
4. Ícone aparece na tela inicial
5. Abre em modo standalone

---

## 🎯 Próximos Passos

### **PWA Freelancer (Atual)**
- ✅ Implementado e funcional
- ✅ Detecção de dispositivo na home
- ✅ Redirecionamento inteligente

### **PWA Empresa (Futuro)**
1. 🔜 Criar estrutura de diretórios `static/empresa_pwa/`
2. 🔜 Criar manifest e service worker
3. 🔜 Criar template e view
4. 🔜 Implementar interface e funcionalidades
5. 🔜 Atualizar redirecionamento na home
6. 🔜 Testar instalação e funcionamento

> 📖 **Para checklist completo de implementação, consulte [PWA_ARQUITETURA_FUTURA.md](./PWA_ARQUITETURA_FUTURA.md)**

---

**Última atualização:** Janeiro 2025
**Status:** PWA Freelancer ✅ Implementado | PWA Empresa 🔜 Planejado

