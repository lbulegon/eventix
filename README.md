# Eventix - Sistema de Gestão de Eventos

## Visão Geral

O Eventix é um sistema completo de gestão de eventos que permite o controle de todos os aspectos de um evento, desde o planejamento até a execução. O sistema é baseado em Django e implementa uma arquitetura multi-tenant, permitindo que múltiplas empresas utilizem a plataforma de forma isolada.

## Arquitetura Multi-Tenant

O sistema utiliza uma arquitetura multi-tenant onde cada empresa contratante (`EmpresaContratante`) possui seus próprios dados isolados. Todos os modelos principais possuem uma relação com `EmpresaContratante` para garantir a separação de dados.

## Estrutura de Estoque e Insumos

### Hierarquia de Estoque

O sistema implementa uma hierarquia de três níveis para o gerenciamento de estoque:

1. **Estoque Geral da Empresa** (`Insumo`)
   - Controle central do estoque da empresa
   - Estoque mínimo e atual
   - Local de armazenamento
   - Fornecedores

2. **Estoque do Evento** (`InsumoEvento`)
   - Alocação de insumos para um evento específico
   - Controle de quantidades alocadas vs. utilizadas
   - Permite calcular quantidades usadas em cada evento

3. **Estoque do Setor** (`InsumoSetor`)
   - Distribuição dos insumos pelos setores do evento
   - Controle de utilização por setor
   - Consome do estoque alocado para o evento

### Fluxo de Estoque

```
Estoque Geral (Insumo)
    ↓ (alocação)
Estoque do Evento (InsumoEvento)
    ↓ (distribuição)
Estoque do Setor (InsumoSetor)
    ↓ (utilização)
Consumo Real
```

## Modelos Principais

### Usuários e Autenticação

- **User**: Usuário customizado com tipos (admin_empresa, operador_empresa, freelancer, admin_sistema)
- **EmpresaContratante**: Empresa que contrata o sistema
- **Empresa**: Empresas fornecedoras e parceiras

### Eventos e Locais

- **LocalEvento**: Locais onde os eventos acontecem
- **Evento**: Eventos principais
- **SetorEvento**: Setores/áreas dentro de um evento

### Equipamentos

- **CategoriaEquipamento**: Categorias de equipamentos
- **Equipamento**: Equipamentos disponíveis
- **EquipamentoSetor**: Alocação de equipamentos por setor
- **ManutencaoEquipamento**: Controle de manutenções

### Recursos Humanos

- **TipoFuncao**: Tipos de funções disponíveis
- **Funcao**: Funções específicas
- **Freelance**: Profissionais freelancers
- **Candidatura**: Candidaturas para vagas
- **ContratoFreelance**: Contratos com freelancers

### Estoque e Insumos

- **CategoriaInsumo**: Categorias de insumos
- **Insumo**: Insumos disponíveis (estoque geral)
- **InsumoEvento**: Alocação de insumos para eventos
- **InsumoSetor**: Distribuição de insumos por setores

### Transporte

- **TipoVeiculo**: Tipos de veículos
- **Veiculo**: Veículos disponíveis
- **RotaTransporte**: Rotas de transporte
- **ItemTransporte**: Itens transportados

### Financeiro

- **FormaPagamento**: Formas de pagamento
- **PagamentoFreelance**: Pagamentos a freelancers
- **DespesaEvento**: Despesas dos eventos

### Avaliações e Feedback

- **AvaliacaoFreelance**: Avaliações de freelancers
- **AvaliacaoEvento**: Avaliações de eventos

### Notificações

- **TipoNotificacao**: Tipos de notificações
- **Notificacao**: Notificações do sistema

### Relatórios e Estatísticas

- **RelatorioEvento**: Relatórios de eventos
- **EstatisticaEmpresa**: Estatísticas da empresa

### Configurações

- **ConfiguracaoSistema**: Configurações globais
- **ConfiguracaoEmpresa**: Configurações por empresa

### Auditoria

- **LogAuditoria**: Logs de auditoria

### Comunicação

- **CanalComunicacao**: Canais de comunicação
- **Mensagem**: Mensagens trocadas

### Checklists e Tarefas

- **ChecklistEvento**: Checklists de eventos
- **ItemChecklist**: Itens de checklist
- **Tarefa**: Tarefas do sistema

### Templates e Documentos

- **TemplateDocumento**: Templates de documentos
- **DocumentoGerado**: Documentos gerados

### Integrações

- **IntegracaoAPI**: Integrações com APIs externas
- **LogIntegracao**: Logs de integração

### Backup e Versionamento

- **BackupSistema**: Backups do sistema
- **VersaoSistema**: Controle de versões

## Funcionalidades Principais

### Gestão de Estoque
- Controle hierárquico de estoque (Empresa → Evento → Setor)
- Alocação automática de insumos para eventos
- Distribuição controlada pelos setores
- Rastreamento de utilização real
- Alertas de estoque baixo

### Gestão de Eventos
- Criação e configuração de eventos
- Definição de setores e áreas
- Alocação de recursos (equipamentos, insumos, pessoas)
- Controle de cronograma

### Gestão de RH
- Cadastro de freelancers
- Criação de vagas
- Processo de candidatura
- Contratos e pagamentos
- Avaliações de performance

### Relatórios e Analytics
- Relatórios de eventos
- Estatísticas de utilização
- Análise de custos
- Performance de freelancers

### Comunicação
- Sistema de notificações
- Canais de comunicação
- Templates de mensagens

### Integrações
- APIs externas
- Webhooks
- Logs de integração





## Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Django 4.0+
- PostgreSQL (recomendado) ou SQLite
- Node.js (para frontend)

### Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd eventix
```NSTALL 

2. Crie um ambiente virtual:
```bash
python -m venv .venv
```

3. Ative o ambiente virtual:
```bash
# Windows

- .venv\Scripts\activate  
# Linux/Mac
source .venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

Variáveis esperadas no `.env` (exemplo no `.env.example`):

- `DJANGO_SECRET_KEY`
- `DEBUG` (True/False)
- `ALLOWED_HOSTS` (separados por vírgula)
- `CSRF_TRUSTED_ORIGINS` (URLs completas separadas por vírgula)
- `DATABASE_ENGINE` (ex.: `django.db.backends.postgresql` ou `django.db.backends.sqlite3`)
- `DATABASE_NAME`
- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `DATABASE_HOST`
- `DATABASE_PORT`
- `MERCADOPAGO_ACCESS_TOKEN`
- (Opcional) `CORS_ALLOWED_ORIGINS` (separados por vírgula)

6. Execute as migrações:
```bash
python manage.py makemigrations app_eventos
python manage.py migrate
```

7. Crie um superusuário:
```bash
python manage.py createsuperuser
```

8. Execute o servidor:
```bash
python manage.py runserver
```

## Deploy

### Railway

1. Instale o CLI do Railway:
```bash
npm i -g @railway/cli
```

2. Faça login:
```bash
railway login
```

3. Conecte ao projeto:
```bash
railway link -p <project-id>
```

4. Deploy:
```bash
railway up
```

5. Execute migrações:
```bash
railway run python manage.py migrate
```

6. Colete arquivos estáticos:
```bash
railway run python manage.py collectstatic
```

## API Endpoints

Todas as rotas de API abaixo estão sob o prefixo `/api/auth/` conforme `setup/urls.py` e `api_v01/urls/urls.py`.

### Autenticação e Perfil
- `POST /api/auth/login/` — Login único (gera tokens JWT)
- `POST /api/auth/refresh/` — Refresh do token JWT
- `POST /api/auth/logout/` — Logout com blacklist de refresh token
- `GET /api/auth/perfil/` — Perfil do usuário logado
- `GET /api/auth/tipo-usuario/` — Informações do tipo de usuário e contexto

### Registro
- `POST /api/auth/registro/` — Registro unificado (fluxo geral)
- `POST /api/auth/registro/freelancer/` — Registro de freelancer
- `POST /api/auth/registro/empresa/` — Registro de empresa contratante
- `GET /api/auth/empresas/` — Listar empresas ativas

### Sistema Financeiro
- `GET /api/auth/categorias-financeiras/` — Listar categorias financeiras
- `GET /api/auth/eventos/<evento_id>/despesas/` — Listar despesas do evento
- `POST /api/auth/despesas/` — Criar despesa
- `PUT /api/auth/despesas/<despesa_id>/` — Atualizar despesa
- `GET /api/auth/eventos/<evento_id>/receitas/` — Listar receitas do evento
- `POST /api/auth/receitas/` — Criar receita
- `PUT /api/auth/receitas/<receita_id>/` — Atualizar receita
- `GET /api/auth/eventos/<evento_id>/fluxo-caixa/` — Resumo do fluxo de caixa do evento
- `GET /api/auth/fluxo-caixa-empresa/` — Resumo agregado da empresa

### Fornecedores
- `GET /api/auth/fornecedores/` — Listar fornecedores (filtros opcionais)
- `GET /api/auth/fornecedores/<fornecedor_id>/` — Detalhes do fornecedor
- `POST /api/auth/fornecedores/criar/` — Criar fornecedor
- `PUT /api/auth/fornecedores/<fornecedor_id>/atualizar/` — Atualizar fornecedor
- `GET /api/auth/fornecedores/<fornecedor_id>/despesas/` — Despesas relacionadas ao fornecedor

## Comandos de Gerenciamento

### Utilitários
```bash
# Escanear portas
python manage.py escanear_portas --host 127.0.0.1 --inicio 31400 --fim 31409

# Extrair PDF
python manage.py extrair_pdf docs/exemplo.pdf

# Gerar vagas fixas
python manage.py geravagas_fixas

# Mostrar URLs
python manage.py show_urls | findstr motoboy
```

## Estrutura de Diretórios

```
eventix/
├── app_eventos/          # App principal com todos os modelos
├── api_v01/             # API REST
├── setup/               # Configurações do projeto
├── static/              # Arquivos estáticos
├── templates/           # Templates HTML
├── docs/                # Documentação
├── requirements.txt     # Dependências Python
├── manage.py           # Script de gerenciamento Django
└── README.md           # Este arquivo
```

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
