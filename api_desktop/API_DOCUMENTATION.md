# API Desktop - Documentação

## Visão Geral

A API Desktop é uma API REST específica para o aplicativo desktop Electron do Eventix. Ela fornece endpoints otimizados para interfaces desktop com funcionalidades avançadas de gerenciamento, relatórios e configurações.

## Base URL

```
https://eventix-development.up.railway.app/api/desktop/
```

## Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação. Inclua o token no header:

```
Authorization: Bearer <seu_token>
```

## Endpoints Principais

### 1. Autenticação

#### Login Desktop
```http
POST /api/desktop/auth/login/
```

**Body:**
```json
{
    "username": "usuario",
    "password": "senha"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@eventix.com",
        "tipo_usuario": "admin_sistema",
        "empresa": null,
        "permissoes": ["gerenciar_usuarios", "gerenciar_eventos", ...]
    }
}
```

#### Refresh Token
```http
POST /api/desktop/auth/refresh/
```

#### Logout
```http
POST /api/desktop/auth/logout/
```

#### Verificar Token
```http
GET /api/desktop/auth/verify/
```

### 2. Dashboard

#### Dashboard Principal
```http
GET /api/desktop/dashboard/
```

**Response:**
```json
{
    "usuario": {
        "nome": "Administrador",
        "tipo": "Administrador do Sistema",
        "empresa": null,
        "permissoes": ["gerenciar_usuarios", "gerenciar_eventos"]
    },
    "estatisticas": {
        "total_usuarios": 150,
        "total_empresas": 25,
        "total_eventos": 300,
        "total_freelancers": 500
    },
    "alertas": [
        {
            "tipo": "warning",
            "mensagem": "5 empresa(s) com contrato vencendo em 30 dias"
        }
    ],
    "atividades_recentes": [
        {
            "tipo": "usuario_novo",
            "descricao": "Novo usuário: joao_silva",
            "data": "2025-01-08T10:30:00Z"
        }
    ]
}
```

### 3. Usuários

#### Listar Usuários
```http
GET /api/desktop/usuarios/
```

#### Estatísticas de Usuários
```http
GET /api/desktop/usuarios/estatisticas/
```

**Response:**
```json
{
    "total_usuarios": 150,
    "usuarios_ativos": 145,
    "freelancers": 120,
    "admins_empresa": 20,
    "operadores": 10,
    "novos_este_mes": 15
}
```

### 4. Empresas

#### Listar Empresas
```http
GET /api/desktop/empresas/
```

#### Estatísticas de Empresas
```http
GET /api/desktop/empresas/estatisticas/
```

### 5. Eventos

#### Listar Eventos
```http
GET /api/desktop/eventos/
```

#### Estatísticas de Eventos
```http
GET /api/desktop/eventos/estatisticas/
```

### 6. Freelancers

#### Listar Freelancers
```http
GET /api/desktop/freelancers/
```

#### Estatísticas de Freelancers
```http
GET /api/desktop/freelancers/estatisticas/
```

### 7. Vagas

#### Listar Vagas
```http
GET /api/desktop/vagas/
```

### 8. Equipamentos

#### Listar Equipamentos
```http
GET /api/desktop/equipamentos/
```

### 9. Relatórios

#### Relatório Financeiro
```http
GET /api/desktop/relatorios/financeiro/
```

**Response:**
```json
{
    "total_despesas": 50000.00,
    "total_receitas": 75000.00,
    "despesas_pendentes": 5,
    "receitas_pendentes": 3
}
```

### 10. Estatísticas Detalhadas

#### Estatísticas por Período
```http
GET /api/desktop/estatisticas/?periodo=30
```

### 11. Exportação de Dados

#### Exportar Dados
```http
POST /api/desktop/exportar-dados/
```

**Body:**
```json
{
    "tipo": "usuarios",
    "formato": "json"
}
```

### 12. Configurações

#### Obter Configurações
```http
GET /api/desktop/configuracoes/
```

#### Salvar Configurações
```http
POST /api/desktop/configuracoes/
```

### 13. Backup

#### Iniciar Backup
```http
POST /api/desktop/backup/
```

### 14. Logs

#### Visualizar Logs
```http
GET /api/desktop/logs/
```

## Permissões

### Tipos de Usuário

1. **admin_sistema**: Acesso total ao sistema
2. **admin_empresa**: Acesso total à empresa específica
3. **operador_empresa**: Acesso limitado à empresa
4. **freelancer**: Acesso apenas a dados públicos

### Permissões Específicas

- `gerenciar_usuarios`: Gerenciar usuários
- `gerenciar_eventos`: Gerenciar eventos
- `gerenciar_freelancers`: Gerenciar freelancers
- `visualizar_relatorios`: Visualizar relatórios
- `gerenciar_financeiro`: Gerenciar dados financeiros
- `gerenciar_equipamentos`: Gerenciar equipamentos

## Códigos de Status HTTP

- `200 OK`: Sucesso
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Dados inválidos
- `401 Unauthorized`: Não autenticado
- `403 Forbidden`: Sem permissão
- `404 Not Found`: Recurso não encontrado
- `500 Internal Server Error`: Erro interno do servidor

## Filtros e Paginação

### Filtros Comuns

- `search`: Busca textual
- `ativo`: Filtrar por status ativo/inativo
- `data_inicio`: Filtrar por data de início
- `data_fim`: Filtrar por data de fim
- `empresa`: Filtrar por empresa

### Paginação

- `page`: Número da página
- `page_size`: Tamanho da página (padrão: 20)

**Exemplo:**
```http
GET /api/desktop/usuarios/?search=joao&ativo=true&page=1&page_size=10
```

## Rate Limiting

- **Limite**: 1000 requests por hora por usuário
- **Header de resposta**: `X-RateLimit-Remaining`

## Webhooks

A API Desktop suporta webhooks para notificações em tempo real:

- `usuario.criado`: Novo usuário criado
- `evento.criado`: Novo evento criado
- `candidatura.aprovada`: Candidatura aprovada
- `empresa.vencimento`: Contrato próximo do vencimento

## Exemplos de Uso

### JavaScript/Electron

```javascript
// Login
const response = await fetch('/api/desktop/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'admin',
        password: 'senha123'
    })
});

const data = await response.json();
localStorage.setItem('access_token', data.access_token);

// Dashboard
const dashboardResponse = await fetch('/api/desktop/dashboard/', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
});

const dashboardData = await dashboardResponse.json();
```

### Python

```python
import requests

# Login
response = requests.post('https://eventix-development.up.railway.app/api/desktop/auth/login/', 
                        json={'username': 'admin', 'password': 'senha123'})
data = response.json()
access_token = data['access_token']

# Dashboard
headers = {'Authorization': f'Bearer {access_token}'}
dashboard_response = requests.get('https://eventix-development.up.railway.app/api/desktop/dashboard/', 
                                 headers=headers)
dashboard_data = dashboard_response.json()
```

## Suporte

Para suporte técnico ou dúvidas sobre a API Desktop, entre em contato com a equipe de desenvolvimento.
