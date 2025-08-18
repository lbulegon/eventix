# API de Registro Único - Eventix

## 📋 Visão Geral

O sistema de registro único permite cadastrar qualquer tipo de usuário (freelancer, empresa, administrador) através de um único endpoint, com validações específicas e vínculo automático com empresas.

## 🔐 Endpoints de Registro

### 1. Registro Único
**POST** `/api/auth/registro/`

Endpoint único para registro de qualquer tipo de usuário.

#### **Request Body:**

**Para Freelancer:**
```json
{
    "username": "joao_freelancer",
    "email": "joao@email.com",
    "password": "12345678",
    "password_confirm": "12345678",
    "tipo_usuario": "freelancer",
    "first_name": "João",
    "last_name": "Silva",
    "nome_completo": "João Silva",
    "telefone": "11988887777",
    "cpf": "12345678901"
}
```

**Para Usuário de Empresa (vincular a empresa existente):**
```json
{
    "username": "maria_empresa",
    "email": "maria@empresateste.com",
    "password": "12345678",
    "password_confirm": "12345678",
    "tipo_usuario": "admin_empresa",
    "empresa_id": 6,
    "first_name": "Maria",
    "last_name": "Santos"
}
```

**Para Usuário de Empresa (criar nova empresa):**
```json
{
    "username": "admin_nova_empresa",
    "email": "admin@novaempresa.com",
    "password": "12345678",
    "password_confirm": "12345678",
    "tipo_usuario": "admin_empresa",
    "empresa_nova": {
        "nome_fantasia": "Nova Empresa",
        "razao_social": "Nova Empresa LTDA",
        "cnpj": "98765432000199",
        "email": "contato@novaempresa.com",
        "telefone": "11888889999",
        "data_vencimento": "2026-12-31",
        "valor_mensal": 149.90
    },
    "first_name": "Admin",
    "last_name": "Nova"
}
```

#### **Response (Sucesso - 200):**
```json
{
    "success": true,
    "message": "Freelancer registrado com sucesso!",
    "user": {
        "id": 7,
        "username": "joao_freelancer",
        "email": "joao@email.com",
        "tipo_usuario": "freelancer",
        "tipo_usuario_display": "Freelancer",
        "is_freelancer": true,
        "is_empresa_user": false,
        "is_admin_sistema": false,
        "empresa_contratante": "Eventix",
        "empresa_owner": "Eventix",
        "dashboard_url": "/freelancer/dashboard/"
    },
    "tokens": {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

### 2. Listar Empresas Disponíveis
**GET** `/api/auth/empresas/`

Lista todas as empresas ativas disponíveis para vínculo.

#### **Response (Sucesso - 200):**
```json
{
    "success": true,
    "empresas": [
        {
            "id": 1,
            "nome_fantasia": "Eventix",
            "razao_social": "Eventix LTDA",
            "cnpj": "00.000.000/0001-00",
            "email": "admin@eventix.com"
        },
        {
            "id": 6,
            "nome_fantasia": "Empresa Teste",
            "razao_social": "Empresa Teste LTDA",
            "cnpj": "12345678000199",
            "email": "contato@empresateste.com"
        }
    ]
}
```

## 📝 Tipos de Usuário Suportados

### 1. **Freelancer** (`tipo_usuario: "freelancer"`)
- **Campos obrigatórios:** `nome_completo`
- **Campos opcionais:** `telefone`, `cpf`
- **Cria automaticamente:** Perfil de freelancer
- **Empresa Owner:** Automaticamente vinculado à **Eventix**
- **Dashboard:** `/freelancer/dashboard/`

### 2. **Administrador da Empresa** (`tipo_usuario: "admin_empresa"`)
- **Obrigatório:** `empresa_id` OU `empresa_nova`
- **Permissões:** Acesso total à empresa
- **Dashboard:** `/empresa/dashboard/`

### 3. **Operador da Empresa** (`tipo_usuario: "operador_empresa"`)
- **Obrigatório:** `empresa_id` OU `empresa_nova`
- **Permissões:** Acesso limitado à empresa
- **Dashboard:** `/empresa/dashboard/`

### 4. **Administrador do Sistema** (`tipo_usuario: "admin_sistema"`)
- **Permissões:** Acesso total ao sistema
- **Dashboard:** `/admin/`

## 🔧 Validações

### **Validações Gerais:**
- Senhas devem coincidir
- Username único
- Email único
- Senha mínima de 8 caracteres

### **Validações por Tipo:**

**Freelancer:**
- `nome_completo` obrigatório

**Usuários de Empresa:**
- Deve fornecer `empresa_id` OU `empresa_nova`
- Se `empresa_id`: empresa deve existir e estar ativa
- Se `empresa_nova`: campos obrigatórios da empresa

**Empresa Nova:**
- `nome_fantasia`, `cnpj`, `email` obrigatórios
- CNPJ único no sistema

## 🚀 Fluxo de Uso

### **1. Registrar Freelancer:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/registro/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joao_freelancer",
    "email": "joao@email.com",
    "password": "12345678",
    "password_confirm": "12345678",
    "tipo_usuario": "freelancer",
    "nome_completo": "João Silva"
  }'
```

### **2. Registrar Usuário de Empresa (vincular existente):**
```bash
# Primeiro, listar empresas disponíveis
curl -X GET http://127.0.0.1:8000/api/auth/empresas/

# Depois, registrar usuário
curl -X POST http://127.0.0.1:8000/api/auth/registro/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria_empresa",
    "email": "maria@empresateste.com",
    "password": "12345678",
    "password_confirm": "12345678",
    "tipo_usuario": "admin_empresa",
    "empresa_id": 6
  }'
```

### **3. Registrar Usuário de Empresa (criar nova empresa):**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/registro/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_nova_empresa",
    "email": "admin@novaempresa.com",
    "password": "12345678",
    "password_confirm": "12345678",
    "tipo_usuario": "admin_empresa",
    "empresa_nova": {
        "nome_fantasia": "Nova Empresa",
        "razao_social": "Nova Empresa LTDA",
        "cnpj": "98765432000199",
        "email": "contato@novaempresa.com",
        "telefone": "11888889999",
        "data_vencimento": "2026-12-31",
        "valor_mensal": 149.90
    }
  }'
```

## ⚠️ Códigos de Erro

### **400 - Dados Inválidos:**
```json
{
    "success": false,
    "message": "Dados inválidos.",
    "errors": {
        "username": ["Este nome de usuário já está em uso."],
        "password_confirm": ["As senhas não coincidem."]
    }
}
```

### **400 - Validações Específicas:**
```json
{
    "success": false,
    "message": "Empresa é obrigatória para usuários de empresa."
}
```

## 🔐 Segurança

- **Autenticação:** JWT Tokens
- **Validação:** Campos obrigatórios por tipo
- **Transações:** Atomic para garantir consistência
- **Permissões:** Baseadas no tipo de usuário
- **Empresas:** Apenas empresas ativas podem ser vinculadas

## 🏢 Sistema de Empresa Owner

### **Freelancers e Eventix:**
- Todos os freelancers são automaticamente vinculados à empresa **Eventix**
- A Eventix é considerada a "empresa owner" de todos os freelancers
- Isso garante que a Eventix tenha controle e visibilidade sobre todos os freelancers do sistema

### **Usuários de Empresa:**
- Usuários do tipo `admin_empresa` e `operador_empresa` são vinculados à sua respectiva empresa
- A empresa contratante é também a empresa owner para estes usuários

### **Campos de Resposta:**
- `empresa_contratante`: Empresa diretamente vinculada ao usuário
- `empresa_owner`: Empresa proprietária/controladora do usuário (sempre Eventix para freelancers)

## 📊 Exemplos de Resposta

### **Freelancer Registrado:**
```json
{
    "success": true,
    "message": "Freelancer registrado com sucesso!",
    "user": {
        "id": 7,
        "username": "joao_freelancer",
        "email": "joao@email.com",
        "tipo_usuario": "freelancer",
        "tipo_usuario_display": "Freelancer",
        "is_freelancer": true,
        "is_empresa_user": false,
        "is_admin_sistema": false,
        "empresa_contratante": "Eventix",
        "empresa_owner": "Eventix",
        "dashboard_url": "/freelancer/dashboard/"
    },
    "tokens": {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

### **Usuário de Empresa Registrado:**
```json
{
    "success": true,
    "message": "Administrador da Empresa registrado com sucesso!",
    "user": {
        "id": 8,
        "username": "maria_empresa",
        "email": "maria@empresateste.com",
        "tipo_usuario": "admin_empresa",
        "tipo_usuario_display": "Administrador da Empresa",
        "is_freelancer": false,
        "is_empresa_user": true,
        "is_admin_sistema": false,
        "empresa_contratante": "Empresa Teste",
        "dashboard_url": "/empresa/dashboard/"
    },
    "tokens": {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

### **Nova Empresa Criada:**
```json
{
    "success": true,
    "message": "Administrador da Empresa registrado com sucesso!",
    "user": {
        "id": 9,
        "username": "admin_nova_empresa",
        "email": "admin@novaempresa.com",
        "tipo_usuario": "admin_empresa",
        "tipo_usuario_display": "Administrador da Empresa",
        "is_freelancer": false,
        "is_empresa_user": true,
        "is_admin_sistema": false,
        "empresa_contratante": "Nova Empresa",
        "dashboard_url": "/empresa/dashboard/"
    },
    "empresa": {
        "id": 7,
        "nome_fantasia": "Nova Empresa",
        "cnpj": "98765432000199"
    },
    "tokens": {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```
