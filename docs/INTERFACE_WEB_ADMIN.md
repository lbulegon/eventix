# Interface Web Administrativa - Eventix

## 📋 Visão Geral

A Interface Web Administrativa do Eventix é uma aplicação web moderna e responsiva que permite às empresas contratantes e freelancers gerenciarem todos os aspectos do sistema de forma intuitiva e eficiente.

## 🎯 Objetivo

Esta interface é **distinta do Django Admin** e foi criada especificamente para:
- **Empresas Contratantes**: Gerenciar eventos, equipamentos, vagas, candidaturas e finanças
- **Freelancers**: Visualizar vagas, enviar candidaturas e acompanhar contratos
- **Administradores do Sistema**: Monitorar o sistema globalmente

## 🚀 Acesso

### URL Base
```
http://localhost:8000/admin-web/
```

### Página de Boas-vindas
Quando acessado sem estar logado, a interface mostra uma página de boas-vindas com:
- Informações sobre as funcionalidades
- Botão para fazer login
- Link para o Django Admin
- Design moderno e responsivo

### Tipos de Usuário e Dashboards

#### 1. Empresa Contratante
- **Dashboard**: `/admin-web/empresa/`
- **Funcionalidades**:
  - Gestão completa de eventos
  - Controle de equipamentos e manutenções
  - Criação e gerenciamento de vagas
  - Aprovação/rejeição de candidaturas
  - Dashboard financeiro
  - Gestão de fornecedores

#### 2. Freelancer
- **Dashboard**: `/admin-web/freelancer/`
- **Funcionalidades**:
  - Visualização de vagas disponíveis
  - Envio de candidaturas
  - Acompanhamento de status
  - Gestão de contratos ativos
  - Perfil pessoal

#### 3. Administrador do Sistema
- **Dashboard**: `/admin-web/admin-sistema/`
- **Funcionalidades**:
  - Visão geral do sistema
  - Gestão de usuários
  - Gestão de empresas
  - Relatórios globais

## 🏗️ Estrutura da Interface

### Template Base
- **Arquivo**: `app_eventos/templates/web_admin/base.html`
- **Características**:
  - Design moderno com Bootstrap 5
  - Sidebar responsiva
  - Sistema de notificações
  - Tema personalizado com cores do Eventix
  - Navegação intuitiva por tipo de usuário

### Componentes Principais

#### 1. Sidebar de Navegação
- **Dashboard**: Visão geral com estatísticas
- **Eventos**: Gestão completa de eventos
- **Equipamentos**: Controle de equipamentos e manutenções
- **Vagas**: Criação e gerenciamento de vagas
- **Candidaturas**: Aprovação e acompanhamento
- **Financeiro**: Dashboard financeiro e relatórios
- **Fornecedores**: Gestão de fornecedores

#### 2. Cards de Estatísticas
- Design com gradientes coloridos
- Ícones intuitivos
- Informações em tempo real
- Cores baseadas no status (sucesso, aviso, perigo)

#### 3. Tabelas Interativas
- Paginação automática
- Filtros avançados
- Ações em lote
- Busca em tempo real

## 📱 Funcionalidades Implementadas

### ✅ Dashboard Empresa
- **Arquivo**: `app_eventos/templates/web_admin/dashboard_empresa.html`
- **Recursos**:
  - Estatísticas em tempo real
  - Eventos recentes
  - Candidaturas pendentes
  - Equipamentos em manutenção
  - Criação rápida de eventos

### ✅ Dashboard Freelancer
- **Arquivo**: `app_eventos/templates/web_admin/dashboard_freelancer.html`
- **Recursos**:
  - Candidaturas enviadas
  - Status de aprovação
  - Vagas recomendadas
  - Contratos ativos
  - Histórico de atividades

### ✅ Gestão de Eventos
- **Lista de Eventos**: `app_eventos/templates/web_admin/eventos_list.html`
- **Detalhes do Evento**: `app_eventos/templates/web_admin/evento_detail.html`
- **Recursos**:
  - CRUD completo de eventos
  - Filtros por status e busca
  - Gestão de setores
  - Resumo financeiro
  - Estatísticas detalhadas

### ✅ Views e URLs
- **Views**: `app_eventos/views/views_web.py`
- **URLs**: `app_eventos/urls/urls_admin.py`
- **Integração**: `setup/urls.py`

## 🎨 Design e UX

### Características Visuais
- **Cores Principais**:
  - Primária: `#2c3e50` (Azul escuro)
  - Secundária: `#3498db` (Azul claro)
  - Sucesso: `#27ae60` (Verde)
  - Aviso: `#f39c12` (Laranja)
  - Perigo: `#e74c3c` (Vermelho)

### Responsividade
- **Desktop**: Layout completo com sidebar fixa
- **Tablet**: Sidebar colapsável
- **Mobile**: Menu hambúrguer e layout adaptativo

### Componentes Modernos
- **Cards com sombras**: Efeito de elevação
- **Gradientes**: Visual moderno e atrativo
- **Ícones Bootstrap**: Interface intuitiva
- **Animações**: Transições suaves
- **Loading states**: Feedback visual

## 🔧 Tecnologias Utilizadas

### Frontend
- **Bootstrap 5**: Framework CSS
- **Bootstrap Icons**: Ícones
- **Chart.js**: Gráficos (preparado)
- **JavaScript Vanilla**: Interatividade

### Backend
- **Django**: Framework web
- **Django Templates**: Sistema de templates
- **Django ORM**: Banco de dados
- **Django Auth**: Sistema de autenticação

## 📊 Funcionalidades por Módulo

### 1. Eventos
- ✅ Listagem com filtros
- ✅ Criação e edição
- ✅ Visualização detalhada
- ✅ Gestão de setores
- ✅ Estatísticas financeiras

### 2. Equipamentos (Pendente)
- 🔄 Listagem de equipamentos
- 🔄 Detalhes e manutenções
- 🔄 Alocação por setor
- 🔄 Controle de status

### 3. Vagas e Candidaturas (Pendente)
- 🔄 Criação de vagas
- 🔄 Listagem de candidaturas
- 🔄 Aprovação/rejeição
- 🔄 Sistema de matching

### 4. Financeiro (Pendente)
- 🔄 Dashboard financeiro
- 🔄 Relatórios de receitas/despesas
- 🔄 Análise de lucros
- 🔄 Exportação de dados

## 🚀 Como Usar

### 1. Acesso Inicial
```bash
# Acesse a interface
http://localhost:8000/admin-web/

# O sistema redirecionará automaticamente para o dashboard apropriado
# baseado no tipo de usuário logado
```

### 2. Navegação
- Use a **sidebar** para navegar entre módulos
- **Cards de estatísticas** mostram informações em tempo real
- **Filtros** permitem encontrar informações rapidamente
- **Modais** para ações rápidas (criar, editar, excluir)

### 3. Responsividade
- **Desktop**: Use a sidebar completa
- **Mobile**: Toque no ícone de menu para abrir a sidebar
- **Tablet**: A sidebar se adapta automaticamente

## 🔄 Próximos Passos

### Funcionalidades Pendentes
1. **Gestão de Equipamentos**: Interface completa
2. **Sistema de Vagas**: Criação e gerenciamento
3. **Dashboard Financeiro**: Relatórios e análises
4. **Notificações**: Sistema em tempo real
5. **Relatórios**: Exportação em PDF/Excel

### Melhorias Futuras
1. **PWA**: Aplicativo web progressivo
2. **Offline**: Funcionalidade offline
3. **Push Notifications**: Notificações push
4. **Analytics**: Métricas avançadas
5. **Integração**: APIs externas

## 🛠️ Desenvolvimento

### Estrutura de Arquivos
```
app_eventos/
├── templates/web_admin/
│   ├── base.html                 # Template base
│   ├── dashboard_empresa.html    # Dashboard empresa
│   ├── dashboard_freelancer.html # Dashboard freelancer
│   ├── eventos_list.html         # Lista de eventos
│   └── evento_detail.html        # Detalhes do evento
├── views/
│   └── views_web.py              # Views da interface web
└── urls/
    └── urls_admin.py             # URLs da interface
```

### Adicionando Novas Funcionalidades
1. **Criar View**: Adicione em `views_web.py`
2. **Criar Template**: Adicione em `templates/web_admin/`
3. **Adicionar URL**: Configure em `urls_admin.py`
4. **Atualizar Sidebar**: Modifique `base.html`

### Notas Importantes
- **Formulários**: Atualmente os formulários estão configurados como GET para evitar erros de CSRF
- **Funcionalidades**: Os modais estão prontos para implementação das funcionalidades CRUD
- **Separação**: Interface web e Django Admin são completamente independentes

## 📞 Suporte

Para dúvidas ou problemas com a interface web administrativa:
1. Verifique os logs do Django
2. Confirme as permissões do usuário
3. Teste em diferentes navegadores
4. Verifique a responsividade em diferentes dispositivos

---

**A Interface Web Administrativa do Eventix está pronta para uso e oferece uma experiência moderna e intuitiva para gerenciar todos os aspectos do sistema de eventos!** 🎉
