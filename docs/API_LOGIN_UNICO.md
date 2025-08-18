# API de Login Único - Eventix

## 📋 Visão Geral

O sistema de login único permite que todos os tipos de usuário (freelancers, empresas e administradores) utilizem o mesmo endpoint de autenticação, com redirecionamento automático para o dashboard apropriado.

## 🔐 Endpoints de Autenticação

### 1. Login Único
**POST** `/api/auth/login/`

Endpoint único para login de todos os tipos de usuário.

**Request Body:**
```json
{
    "username": "usuario123",
    "password": "senha123"
}
```

**Response (Sucesso - 200):**
```json
{
    "success": true,
    "message": "Login realizado com sucesso!",
    "user": {
        "id": 1,
        "username": "usuario123",
        "email": "usuario@email.com",
        "first_name": "João",
        "last_name": "Silva",
        "tipo_usuario": "freelancer",
        "tipo_usuario_display": "Freelancer",
        "is_freelancer": true,
        "is_empresa_user": false,
        "is_admin_sistema": false,
        "empresa_contratante": null,
        "dashboard_url": "/freelancer/dashboard/"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

**Response (Erro - 401):**
```json
{
    "success": false,
    "message": "Credenciais inválidas ou usuário inativo."
}
```

### 2. Registro de Freelancer
**POST** `/api/auth/registro/freelancer/`

**Request Body:**
```json
{
    "username": "freelancer123",
    "email": "freelancer@email.com",
    "password": "senha123",
    "password_confirm": "senha123",
    "first_name": "João",
    "last_name": "Silva",
    "nome_completo": "João Silva Santos",
    "telefone": "(11) 99999-9999",
    "cpf": "123.456.789-00"
}
```

### 3. Registro de Empresa
**POST** `/api/auth/registro/empresa/`

**Request Body:**
```json
{
    "usuario": {
        "username": "empresa123",
        "email": "empresa@email.com",
        "password": "senha123",
        "password_confirm": "senha123",
        "first_name": "Maria",
        "last_name": "Santos"
    },
    "empresa": {
        "nome_fantasia": "Empresa Eventos LTDA",
        "razao_social": "Empresa Eventos LTDA",
        "cnpj": "12.345.678/0001-90",
        "email": "contato@empresa.com",
        "telefone": "(11) 3333-3333",
        "website": "https://empresa.com"
    }
}
```

### 4. Perfil do Usuário
**GET** `/api/auth/perfil/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "success": true,
    "user": {
        "id": 1,
        "username": "usuario123",
        "email": "usuario@email.com",
        "first_name": "João",
        "last_name": "Silva",
        "tipo_usuario": "freelancer",
        "tipo_usuario_display": "Freelancer",
        "ativo": true,
        "is_freelancer": true,
        "is_empresa_user": false,
        "is_admin_sistema": false,
        "empresa_contratante_nome": null,
        "dashboard_url": "/freelancer/dashboard/",
        "data_ultimo_acesso": "2024-01-15T10:30:00Z",
        "date_joined": "2024-01-01T00:00:00Z"
    },
    "dashboard_url": "/freelancer/dashboard/"
}
```

### 5. Verificar Tipo de Usuário
**GET** `/api/auth/tipo-usuario/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (Freelancer):**
```json
{
    "success": true,
    "user_type": "freelancer",
    "user_type_display": "Freelancer",
    "is_freelancer": true,
    "is_empresa_user": false,
    "is_admin_sistema": false,
    "dashboard_url": "/freelancer/dashboard/",
    "freelance_info": {
        "id": 1,
        "nome_completo": "João Silva Santos",
        "cpf": "123.456.789-00",
        "cadastro_completo": true
    }
}
```

**Response (Empresa):**
```json
{
    "success": true,
    "user_type": "admin_empresa",
    "user_type_display": "Administrador da Empresa",
    "is_freelancer": false,
    "is_empresa_user": true,
    "is_admin_sistema": false,
    "dashboard_url": "/empresa/dashboard/",
    "empresa_info": {
        "id": 1,
        "nome_fantasia": "Empresa Eventos LTDA",
        "cnpj": "12.345.678/0001-90",
        "ativo": true
    }
}
```

### 6. Logout
**POST** `/api/auth/logout/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
    "success": true,
    "message": "Logout realizado com sucesso!"
}
```

### 7. Refresh Token
**POST** `/api/auth/refresh/`

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 🎯 Tipos de Usuário

### Propriedades do Usuário

| Propriedade | Descrição |
|-------------|-----------|
| `is_freelancer` | `true` se o usuário é freelancer |
| `is_empresa_user` | `true` se o usuário é da empresa (admin ou operador) |
| `is_admin_sistema` | `true` se o usuário é administrador do sistema |

### Tipos Disponíveis

| Tipo | Descrição | Dashboard |
|------|-----------|-----------|
| `freelancer` | Freelancer | `/freelancer/dashboard/` |
| `admin_empresa` | Administrador da Empresa | `/empresa/dashboard/` |
| `operador_empresa` | Operador da Empresa | `/empresa/dashboard/` |
| `admin_sistema` | Administrador do Sistema | `/admin/` |

## 🔄 Fluxo de Autenticação

1. **Login**: Usuário faz login via `/api/auth/login/`
2. **Verificação**: Sistema identifica o tipo de usuário
3. **Redirecionamento**: Usuário é redirecionado para o dashboard apropriado
4. **Acesso**: Usuário acessa funcionalidades específicas do seu tipo

## 🛡️ Segurança

- **JWT Tokens**: Autenticação baseada em tokens JWT
- **Refresh Tokens**: Renovação automática de tokens
- **Blacklist**: Tokens invalidados no logout
- **Validação**: Verificação de usuário ativo e empresa ativa

## 📱 Exemplo de Uso (JavaScript)

```javascript
// Login
const loginResponse = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'usuario123',
        password: 'senha123'
    })
});

const loginData = await loginResponse.json();

if (loginData.success) {
    // Salva tokens
    localStorage.setItem('access_token', loginData.tokens.access);
    localStorage.setItem('refresh_token', loginData.tokens.refresh);
    
    // Redireciona para dashboard
    window.location.href = loginData.user.dashboard_url;
}

// Verificar tipo de usuário
const checkUserType = async () => {
    const response = await fetch('/api/auth/tipo-usuario/', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    
    const data = await response.json();
    
    if (data.is_freelancer) {
        // Mostrar interface de freelancer
        showFreelancerInterface();
    } else if (data.is_empresa_user) {
        // Mostrar interface de empresa
        showEmpresaInterface();
    } else if (data.is_admin_sistema) {
        // Mostrar interface de admin
        showAdminInterface();
    }
};
```

## 🚀 Próximos Passos

1. **Interface Web**: Criar páginas de login e registro
2. **Validação**: Adicionar validações mais robustas
3. **Recuperação de Senha**: Implementar sistema de recuperação
4. **2FA**: Adicionar autenticação de dois fatores
5. **Auditoria**: Log de tentativas de login
