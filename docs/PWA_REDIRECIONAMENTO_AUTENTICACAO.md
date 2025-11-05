# 🔐 Sistema de Redirecionamento PWA - Eventix

## 📋 Visão Geral

O sistema agora redireciona automaticamente os usuários baseado no seu status de autenticação, mantendo a compatibilidade completa com PWA.

---

## 🔄 Fluxo de Redirecionamento

### **1. Usuário NÃO Autenticado**
- **Ação:** Mostra a página inicial (`home.html`)
- **URL:** `/`
- **Opções disponíveis:**
  - Botão "Área do Freelancer" → `/freelancer-publico/login/`
  - Botão "Área da Empresa" → `/empresa/login/`
  - Ver eventos públicos

### **2. Usuário Autenticado - Freelancer**
- **Ação:** Redireciona automaticamente para o dashboard do freelancer
- **URL destino:** `/freelancer-publico/dashboard/`
- **Detecção:** `user.tipo_usuario == 'freelancer'` ou `hasattr(user, 'freelance')`

### **3. Usuário Autenticado - Empresa (Admin/Operador)**
- **Ação:** Redireciona automaticamente para o dashboard da empresa
- **URL destino:** `/empresa/dashboard/`
- **Detecção:** `user.tipo_usuario in ['admin_empresa', 'operador_empresa']`

### **4. Usuário Autenticado - Admin Sistema**
- **Ação:** Redireciona para o admin do Django
- **URL destino:** `/admin/`
- **Detecção:** `user.tipo_usuario == 'admin_sistema'`

---

## ✅ Implementação

### **View `home` Atualizada** (`app_eventos/views/__init__.py`)

```python
def home(request):
    # Se não estiver autenticado, mostrar página inicial
    if not request.user.is_authenticated:
        return render(request, "home.html")
    
    # Redirecionar baseado no tipo de usuário
    user = request.user
    
    if hasattr(user, 'freelance') or user.tipo_usuario == 'freelancer':
        return redirect('freelancer_publico:dashboard')
    
    if user.tipo_usuario in ['admin_empresa', 'operador_empresa']:
        return redirect('dashboard_empresa:dashboard_empresa')
    
    if user.tipo_usuario == 'admin_sistema':
        return redirect('admin:index')
    
    return render(request, "home.html")
```

### **Página Inicial Atualizada** (`app_eventos/templates/home.html`)

- ✅ Botão "Área do Freelancer" → `/freelancer-publico/login/`
- ✅ Botão "Área da Empresa" → `/empresa/login/`
- ✅ Mantém compatibilidade com PWA

---

## 🔒 Compatibilidade com PWA

### **URLs Públicas (Não Requerem Autenticação)**

O sistema garante que as seguintes URLs funcionem sem autenticação:

- ✅ `/` - Página inicial (redireciona se autenticado)
- ✅ `/service-worker.js` - Service Worker (PWA)
- ✅ `/manifest.json` - Manifest (PWA)
- ✅ `/freelancer-publico/login/` - Login freelancer
- ✅ `/empresa/login/` - Login empresa
- ✅ `/eventos/` - Lista de eventos públicos
- ✅ `/static/` - Arquivos estáticos
- ✅ `/media/` - Arquivos de mídia

### **Proteção de Rotas**

- ✅ Rotas de dashboard requerem autenticação (`@login_required`)
- ✅ Middleware verifica permissões por tipo de usuário
- ✅ Redirecionamentos automáticos baseados no tipo de usuário

---

## 🧪 Como Testar

### **1. Usuário Não Autenticado**
```
1. Acesse: https://eventix-development.up.railway.app/
2. Deve ver: Página inicial com botões de login
3. Service Worker deve registrar normalmente
```

### **2. Usuário Freelancer**
```
1. Faça login como freelancer: /freelancer-publico/login/
2. Acesse: https://eventix-development.up.railway.app/
3. Deve redirecionar automaticamente para: /freelancer-publico/dashboard/
4. PWA continua funcionando normalmente
```

### **3. Usuário Empresa**
```
1. Faça login como empresa: /empresa/login/
2. Acesse: https://eventix-development.up.railway.app/
3. Deve redirecionar automaticamente para: /empresa/dashboard/
4. PWA continua funcionando normalmente
```

---

## ⚠️ Importante

### **Service Worker e Manifest**

- ✅ **Nunca** devem requerer autenticação
- ✅ Devem estar acessíveis na raiz do domínio
- ✅ Headers corretos configurados em `views_pwa.py`

### **PWA Instalado**

Quando o PWA está instalado:
- ✅ O redirecionamento funciona normalmente
- ✅ Service Worker continua ativo
- ✅ Cache funciona corretamente
- ✅ Offline funciona (com cache)

---

## 🔄 Fluxo Completo

```
Usuário acessa "/"
    ↓
Está autenticado?
    ├─ NÃO → Mostra home.html (com botões de login)
    │
    └─ SIM → Verifica tipo_usuario
             ├─ freelancer → /freelancer-publico/dashboard/
             ├─ admin_empresa/operador_empresa → /empresa/dashboard/
             └─ admin_sistema → /admin/
```

---

## 📝 Notas Técnicas

1. **Service Worker:** Funciona independente de autenticação
2. **Manifest:** Acessível publicamente
3. **Redirecionamentos:** Usam `redirect()` do Django (HTTP 302)
4. **PWA:** Continua funcionando após redirecionamento
5. **Cache:** Service Worker cacheia páginas visitadas

---

**Última atualização:** Janeiro 2025

