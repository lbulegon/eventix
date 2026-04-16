# Contrato de Dominio: Emissao de Vagas

Este documento define a regra oficial para emissao, publicacao e governanca de `Vaga` no Eventix.
Objetivo: remover ambiguidade entre "mercado aberto para freelancers" e "isolamento por empresa contratante".

## 1) Definicao do Agregado

- **Agregado principal:** `Vaga`
- **Dono do agregado (tenant owner):** `Vaga.empresa_contratante`
- **Origem operacional obrigatoria:**
  - `evento` (com `setor` opcional), **ou**
  - `ponto_operacao`
- **Especialidade obrigatoria:** `funcao`

### Invariantes (sempre verdade)

1. Uma vaga pertence a exatamente um tenant (`empresa_contratante`).
2. Uma vaga tem exatamente uma origem: evento/setor **ou** ponto de operacao.
3. A funcao da vaga deve estar disponivel para o tenant:
   - global (`funcao.empresa_contratante is null`), ou
   - da propria empresa da vaga.
4. Usuario de empresa nao pode criar/editar/publicar vaga de outro tenant.

## 2) Visibilidade e Escopo

### 2.1 Descoberta de vagas (lado freelancer)

- As vagas ativas/publicadas entram em **mercado aberto**.
- Nao depende de historico previo com a empresa (`FreelancerPrestacaoServico`).
- Afinidade por especialidade ocorre por `funcao` da vaga + filtros.

### 2.2 Gestao de freelancers (lado empresa)

- A lista de freelancers da empresa e privada por tenant.
- Exibe apenas quem:
  - ja prestou servico para a empresa, ou
  - foi cadastrado explicitamente por ela
  (base: `FreelancerPrestacaoServico` ativo).

## 3) Estados de Ciclo de Vida da Vaga

Estados observaveis no dominio atual:

- **Rascunho/Interna:** `ativa=True` e `publicada=False`
- **Publicada:** `ativa=True` e `publicada=True`
- **Despublicada:** `ativa=True` e `publicada=False`
- **Encerrada/Inativa:** `ativa=False` (independente de `publicada`)

Transicoes permitidas:

1. Criacao -> Rascunho/Interna
2. Rascunho/Interna -> Publicada
3. Publicada -> Despublicada
4. Qualquer ativa -> Encerrada/Inativa

## 4) Matriz de Permissoes

- `admin_empresa` / `operador_empresa`
  - criar vaga: **sim**, no proprio tenant
  - editar vaga: **sim**, no proprio tenant
  - publicar/despublicar: **sim**, no proprio tenant
  - listar todas as vagas do sistema: **nao**
- `gestor_grupo`
  - permitido apenas com contexto explicito de empresa quando endpoint suportar contexto tenant
  - nunca "cross-tenant" sem contexto
- `freelancer`
  - criar/editar/publicar vaga: **nao**
  - listar vagas abertas: **sim**
- `admin_sistema`
  - pode atuar sobre todos os tenants (quando a view permitir)

## 5) Mapeamento de Endpoints (Atual)

## 5.1 Web (Dashboard Empresa)

Arquivo: `app_eventos/urls_dashboard_empresa.py`

- `POST /empresa/setores/<setor_id>/criar-vaga/`
  - View: `criar_vaga`
  - Escopo: empresa do usuario via `require_empresa_dashboard`
  - Origem: evento/setor
- `POST /empresa/eventos/<evento_id>/criar-vaga-generica/`
  - View: `criar_vaga_generica`
  - Escopo: empresa do usuario
  - Origem: evento (sem setor)
- `POST /empresa/vagas/<vaga_id>/editar/`
  - View: `editar_vaga`
- `POST /empresa/vagas/<vaga_id>/desativar/`
  - View: `desativar_vaga`

## 5.2 API Mobile (v1)

Arquivo: `api_mobile/urls.py` (montado em `/api/v1/` via `setup/urls.py`)

- `GET /api/v1/vagas/` (`VagaViewSet`)
  - Lista vagas para descoberta (mercado aberto)
- `POST /api/v1/vagas-avancadas/` (`VagaAvancadaViewSet`)
  - Criacao por usuario empresa
- `PATCH/PUT /api/v1/vagas-avancadas/<id>/`
  - Edicao de vaga
- `POST /api/v1/vagas-avancadas/<id>/publicar/`
  - Publicacao
- `POST /api/v1/vagas-avancadas/<id>/despublicar/`
  - Despublicacao

## 5.3 API v01 (eventos)

- Existe `VagaViewSet` em `api_v01/views/views.py` para leitura.
- Rotas de eventos em `/api/v1/` tambem sao carregadas por `api_v01.urls.eventos`.
- Como coexistem includes em `/api/v1/`, toda nova rota de vaga deve evitar colisao de namespace/path.

## 6) Regras de Validacao Backend (Checklist obrigatorio)

Em create/update de vaga:

1. Validar origem:
   - setor/evento xor ponto_operacao
2. Validar tenant:
   - setor.evento.empresa_contratante == usuario.empresa_contratante
   - ponto_operacao.empresa_contratante == usuario.empresa_contratante
3. Validar funcao:
   - global ou da empresa do usuario
   - ativa e disponivel para vagas
4. Impedir `empresa_contratante` forjada no payload para outro tenant.
5. Em publicacao/despublicacao, conferir ownership da vaga.

## 7) Anti-Regras (o que nao fazer)

- Nao filtrar descoberta de vagas por `FreelancerPrestacaoServico`.
- Nao permitir empresa criar vaga usando setor/ponto de outro tenant.
- Nao permitir funcao privada de outra empresa.
- Nao permitir update/publicacao cross-tenant.

## 8) Plano de Endurecimento (curto prazo)

1. Consolidar criacao de vaga em servico de dominio unico (web + APIs).
2. Padronizar serializer/validator para tenant + funcao.
3. Cobrir com testes:
   - create cross-tenant (deve falhar)
   - create com funcao de outra empresa (deve falhar)
   - publicar vaga de outra empresa (deve falhar)
   - freelancer listando vagas abertas (deve funcionar)

## 9) Decisao de Produto Congelada

**A emissao de vaga e privada por empresa contratante. A descoberta de vaga e aberta para freelancers por especialidade.**

Se esse principio mudar no futuro (ex.: redes privadas por grupo), deve ser versionado como nova politica de marketplace e migracao de regras.
