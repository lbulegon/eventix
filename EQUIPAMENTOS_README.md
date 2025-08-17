# Sistema de Gerenciamento de Equipamentos - Eventix

## 📋 Visão Geral

O sistema de equipamentos permite gerenciar todos os equipamentos necessários para os setores dos eventos, incluindo controle de quantidade, disponibilidade, responsáveis e manutenções.

## 🏗️ Modelos Criados

### 1. CategoriaEquipamento
- **Propósito**: Categorizar equipamentos (Áudio, Iluminação, Segurança, etc.)
- **Campos**: nome, descricao

### 2. Equipamento
- **Propósito**: Cadastro completo de equipamentos
- **Campos principais**:
  - Informações básicas: nome, categoria, descricao, especificacoes_tecnicas
  - Detalhes técnicos: marca, modelo, numero_serie, estado_conservacao
  - Financeiro: data_aquisicao, valor_aquisicao
  - Arquivos: foto, manual_instrucoes
  - Status: ativo, criado_em, atualizado_em

### 3. EquipamentoSetor
- **Propósito**: Relacionar equipamentos com setores de eventos
- **Campos principais**:
  - Relacionamentos: setor, equipamento, responsavel_equipamento
  - Quantidades: quantidade_necessaria, quantidade_disponivel
  - Período: data_inicio_uso, data_fim_uso
  - Status: status (disponivel, em_uso, manutencao, indisponivel)
  - Propriedades calculadas: quantidade_faltante, percentual_cobertura

### 4. ManutencaoEquipamento
- **Propósito**: Registrar manutenções dos equipamentos
- **Campos principais**:
  - Detalhes: equipamento, tipo_manutencao, descricao
  - Período: data_inicio, data_fim
  - Custos: custo, fornecedor
  - Responsabilidade: responsavel, status

## 🔧 Funcionalidades

### Admin Django
- Interface completa para gerenciar todos os modelos
- Filtros e buscas avançadas
- Relacionamentos automáticos
- Validações de dados

### APIs REST
- **Categorias**: `GET/POST/PUT/DELETE /api/equipamentos/categorias/`
- **Equipamentos**: `GET/POST/PUT/DELETE /api/equipamentos/equipamentos/`
- **Equipamentos por Setor**: `GET/POST/PUT/DELETE /api/equipamentos/equipamentos-setor/`
- **Manutenções**: `GET/POST/PUT/DELETE /api/equipamentos/manutencoes/`

### Endpoints Especiais
- `GET /api/equipamentos/equipamentos/{id}/setores_utilizacao/` - Setores onde equipamento é usado
- `GET /api/equipamentos/equipamentos/{id}/manutencoes/` - Manutenções do equipamento
- `GET /api/equipamentos/equipamentos-setor/por_setor/?setor_id=X` - Equipamentos de um setor
- `GET /api/equipamentos/equipamentos-setor/por_evento/?evento_id=X` - Equipamentos de um evento
- `GET /api/equipamentos/equipamentos-setor/resumo_evento/?evento_id=X` - Resumo estatístico
- `POST /api/equipamentos/manutencoes/{id}/finalizar/` - Finalizar manutenção

### Interface Web
- `GET /setor/{id}/equipamentos/` - Visualizar equipamentos de um setor
- Dashboard com estatísticas e progresso de cobertura
- Links diretos para admin

## 🚀 Como Usar

### 1. Configuração Inicial
```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar categorias iniciais
python manage.py criar_categorias_equipamentos
```

### 2. Fluxo de Trabalho

#### Para Administradores:
1. **Cadastrar Categorias**: Criar categorias de equipamentos (Áudio, Iluminação, etc.)
2. **Cadastrar Equipamentos**: Adicionar equipamentos com todas as informações
3. **Alocar em Setores**: Associar equipamentos aos setores dos eventos
4. **Definir Quantidades**: Especificar quantidade necessária vs. disponível
5. **Designar Responsáveis**: Atribuir freelancers responsáveis pelos equipamentos
6. **Acompanhar Status**: Monitorar disponibilidade e manutenções

#### Para Freelancers:
1. **Visualizar Equipamentos**: Ver equipamentos atribuídos ao setor
2. **Atualizar Status**: Informar quando equipamentos estão em uso
3. **Solicitar Manutenção**: Reportar problemas ou necessidade de manutenção

### 3. Exemplos de Uso

#### Criar um equipamento via API:
```bash
curl -X POST http://localhost:8000/api/equipamentos/equipamentos/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Caixa de Som JBL",
    "categoria": 1,
    "marca": "JBL",
    "modelo": "EON615",
    "estado_conservacao": "bom",
    "ativo": true
  }'
```

#### Adicionar equipamento a um setor:
```bash
curl -X POST http://localhost:8000/api/equipamentos/equipamentos-setor/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "setor": 1,
    "equipamento": 1,
    "quantidade_necessaria": 4,
    "quantidade_disponivel": 2,
    "status": "disponivel"
  }'
```

#### Obter resumo de equipamentos de um evento:
```bash
curl -X GET "http://localhost:8000/api/equipamentos/equipamentos-setor/resumo_evento/?evento_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📊 Relatórios e Estatísticas

### Por Evento:
- Total de equipamentos
- Quantidade necessária vs. disponível
- Percentual de cobertura
- Distribuição por categoria
- Status dos equipamentos

### Por Setor:
- Lista detalhada de equipamentos
- Progresso de cobertura individual
- Responsáveis designados
- Histórico de manutenções

### Por Equipamento:
- Setores onde é utilizado
- Histórico de manutenções
- Status atual
- Informações técnicas completas

## 🔍 Filtros Disponíveis

### Equipamentos:
- Por categoria
- Por estado de conservação
- Por status ativo/inativo
- Por nome (busca)

### Equipamentos por Setor:
- Por setor específico
- Por evento
- Por categoria de equipamento
- Por status

### Manutenções:
- Por equipamento
- Por tipo de manutenção
- Por status
- Por período

## 🛠️ Comandos de Gerenciamento

```bash
# Criar categorias iniciais
python manage.py criar_categorias_equipamentos

# Verificar equipamentos em manutenção
python manage.py shell
>>> from app_eventos.models import ManutencaoEquipamento
>>> ManutencaoEquipamento.objects.filter(status='em_andamento').count()

# Verificar cobertura de equipamentos
>>> from app_eventos.models import EquipamentoSetor
>>> EquipamentoSetor.objects.filter(quantidade_faltante__gt=0).count()
```

## 🔐 Permissões

- **IsAuthenticated**: Todas as APIs requerem autenticação
- **Admin Django**: Acesso completo via interface administrativa
- **Freelancers**: Visualização limitada aos setores atribuídos

## 📱 Interface Web

A interface web permite:
- Visualizar equipamentos de um setor específico
- Ver estatísticas de cobertura
- Acessar links diretos para edição no admin
- Monitorar progresso com barras visuais
- Identificar rapidamente equipamentos com problemas

## 🔄 Próximos Passos

1. **Notificações**: Alertas automáticos para equipamentos com baixa cobertura
2. **Calendário**: Visualização de uso de equipamentos ao longo do tempo
3. **Relatórios**: Exportação de relatórios em PDF/Excel
4. **Mobile**: Interface mobile para freelancers
5. **Integração**: Conectar com sistema de fornecedores
6. **QR Code**: Identificação rápida de equipamentos via QR Code
