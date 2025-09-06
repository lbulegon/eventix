# 📱 API Mobile - Eventix

## 🎯 Visão Geral

API REST para o aplicativo mobile Eventix, fornecendo endpoints para gerenciamento de vagas, candidaturas, eventos e freelancers.

**Base URL**: `https://eventix-development.up.railway.app/api/v1/`

## 🔐 Autenticação

Todos os endpoints (exceto pré-cadastro e reset de senha) requerem autenticação via JWT token.

```http
Authorization: Bearer <access_token>
```

## 📋 Endpoints Disponíveis

### 🔑 **Autenticação**

#### **Verificar Token**
```http
POST /api/v1/token/verify/
```
**Resposta:**
```json
{
  "valid": true,
  "user_id": 123
}
```

#### **Perfil do Usuário**
```http
GET /api/v1/users/profile/
```
**Resposta:**
```json
{
  "id": 123,
  "username": "user@example.com",
  "email": "user@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "tipo_usuario": "freelancer",
  "ativo": true,
  "freelance": {
    "id": 456,
    "nome_completo": "João Silva",
    "telefone": "11999999999",
    "cpf": "12345678901",
    "cadastro_completo": true
  }
}
```

### 💼 **Vagas**

#### **Listar Vagas Disponíveis**
```http
GET /api/v1/vagas/
```
**Parâmetros de Query:**
- `evento_id`: Filtrar por evento
- `funcao_id`: Filtrar por função
- `cidade`: Filtrar por cidade
- `search`: Buscar por título, descrição ou função

**Resposta:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "titulo": "Garçom para Evento",
      "funcao": {
        "id": 1,
        "nome": "Garçom",
        "descricao": "Atendimento ao cliente",
        "tipo_funcao": "Alimentação"
      },
      "setor": {
        "id": 1,
        "nome": "Salão Principal",
        "evento": 1
      },
      "quantidade": 5,
      "remuneracao": "100.00",
      "descricao": "Vaga para garçom experiente",
      "ativa": true,
      "evento_nome": "Casamento João e Maria",
      "candidaturas_count": 3
    }
  ]
}
```

### 📝 **Candidaturas**

#### **Candidatar-se a uma Vaga**
```http
POST /api/v1/candidaturas/
```
**Body:**
```json
{
  "vaga_id": 1
}
```

#### **Listar Minhas Candidaturas**
```http
GET /api/v1/candidaturas/
```
**Resposta:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "vaga": {
        "id": 1,
        "titulo": "Garçom para Evento",
        "evento_nome": "Casamento João e Maria",
        "remuneracao": "100.00"
      },
      "data_candidatura": "2024-01-15T10:30:00Z",
      "status": "pendente"
    }
  ]
}
```

#### **Cancelar Candidatura**
```http
POST /api/v1/candidaturas/{id}/cancelar/
```

#### **Aprovar Candidatura** (Empresas)
```http
POST /api/v1/candidaturas/{id}/aprovar/
```

#### **Rejeitar Candidatura** (Empresas)
```http
POST /api/v1/candidaturas/{id}/rejeitar/
```

### 🎉 **Eventos**

#### **Listar Eventos**
```http
GET /api/v1/eventos/
```
**Resposta:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "nome": "Casamento João e Maria",
      "descricao": "Cerimônia e recepção",
      "data_inicio": "2024-12-15T18:00:00Z",
      "data_fim": "2024-12-15T23:00:00Z",
      "local": {
        "id": 1,
        "nome": "Salão de Festas",
        "endereco": "Rua das Flores, 123",
        "cidade": "São Paulo",
        "uf": "SP"
      },
      "status": "ativo"
    }
  ]
}
```

#### **Criar Evento** (Empresas)
```http
POST /api/v1/eventos/
```
**Body:**
```json
{
  "nome": "Novo Evento",
  "descricao": "Descrição do evento",
  "data_inicio": "2024-12-20T18:00:00Z",
  "data_fim": "2024-12-20T23:00:00Z",
  "local_id": 1
}
```

#### **Meus Eventos** (Empresas)
```http
GET /api/v1/eventos/meus_eventos/
```

### 👤 **Freelancers**

#### **Pré-cadastro de Freelancer**
```http
POST /api/v1/freelancers/pre_cadastro/
```
**Body:**
```json
{
  "nome_completo": "João Silva",
  "telefone": "11999999999",
  "cpf": "12345678901",
  "email": "joao@example.com",
  "password": "senha123",
  "data_nascimento": "1990-01-01",
  "sexo": "M",
  "habilidades": "Garçom, Bartender, Organizador"
}
```

#### **Atualizar Perfil Freelancer**
```http
PUT /api/v1/freelancers/{id}/
```

### 🏢 **Empresas**

#### **Listar Empresas**
```http
GET /api/v1/empresas/
```

#### **Minha Empresa** (Empresas)
```http
GET /api/v1/empresas-contratantes/
PUT /api/v1/empresas-contratantes/
```

### 🔒 **Recuperação de Senha**

#### **Solicitar Reset de Senha**
```http
POST /api/v1/password/password-reset/
```
**Body:**
```json
{
  "email": "user@example.com"
}
```

#### **Confirmar Reset de Senha**
```http
POST /api/v1/password/password-reset/confirm/
```
**Body:**
```json
{
  "token": "reset_token",
  "new_password": "nova_senha123"
}
```

## 📊 **Códigos de Status HTTP**

- `200 OK`: Sucesso
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Dados inválidos
- `401 Unauthorized`: Token inválido ou ausente
- `403 Forbidden`: Sem permissão para a ação
- `404 Not Found`: Recurso não encontrado
- `500 Internal Server Error`: Erro interno do servidor

## 🔍 **Filtros e Busca**

### **Vagas**
- `?evento_id=1`: Filtrar por evento
- `?funcao_id=2`: Filtrar por função
- `?cidade=São Paulo`: Filtrar por cidade
- `?search=garçom`: Buscar por texto

### **Paginação**
Todos os endpoints de listagem suportam paginação:
- `?page=1`: Página específica
- `?page_size=20`: Tamanho da página

## 🚨 **Tratamento de Erros**

### **Erro de Validação**
```json
{
  "field_name": ["Este campo é obrigatório."]
}
```

### **Erro de Permissão**
```json
{
  "error": "Apenas freelancers podem se candidatar"
}
```

### **Erro de Recurso Não Encontrado**
```json
{
  "detail": "Não encontrado."
}
```

## 🔄 **Fluxos Principais**

### **1. Fluxo de Candidatura (Freelancer)**
1. `GET /api/v1/vagas/` - Listar vagas disponíveis
2. `POST /api/v1/candidaturas/` - Candidatar-se
3. `GET /api/v1/candidaturas/` - Acompanhar status
4. `POST /api/v1/candidaturas/{id}/cancelar/` - Cancelar se necessário

### **2. Fluxo de Gestão de Eventos (Empresa)**
1. `POST /api/v1/eventos/` - Criar evento
2. `GET /api/v1/eventos/meus_eventos/` - Listar meus eventos
3. `GET /api/v1/candidaturas/` - Ver candidaturas recebidas
4. `POST /api/v1/candidaturas/{id}/aprovar/` - Aprovar candidatos

### **3. Fluxo de Cadastro (Freelancer)**
1. `POST /api/v1/freelancers/pre_cadastro/` - Pré-cadastro
2. `GET /api/v1/users/profile/` - Verificar perfil
3. `PUT /api/v1/freelancers/{id}/` - Completar cadastro

## 🧪 **Testes**

Execute os testes com:
```bash
python manage.py test api_mobile
```

## 📝 **Notas de Implementação**

- Todos os endpoints seguem o padrão REST
- Autenticação via JWT (Simple JWT)
- Paginação automática em listagens
- Filtros e busca implementados
- Validação de permissões por tipo de usuário
- Logs estruturados para monitoramento
