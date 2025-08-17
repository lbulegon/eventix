# Sistema de Gerenciamento de Equipamentos

Este documento descreve o sistema de gerenciamento de equipamentos implementado no projeto Eventix.

## Visão Geral

O sistema permite:
- Cadastrar e gerenciar equipamentos por categoria e empresa proprietária
- Associar equipamentos aos setores dos eventos (apenas da mesma empresa)
- Controlar quantidades necessárias e disponíveis
- Gerenciar manutenções dos equipamentos
- Visualizar relatórios e estatísticas
- **Controle de propriedade**: Equipamentos pertencem a empresas específicas e só podem ser usados em eventos da mesma empresa

## Modelos de Dados

### CategoriaEquipamento
Categorias para classificar os equipamentos (ex: Áudio, Iluminação, Segurança, etc.)

### Equipamento
- **empresa_proprietaria**: Empresa que possui o equipamento (obrigatório)
- **codigo_patrimonial**: Código patrimonial do equipamento (opcional)
- **categoria**: Categoria do equipamento
- **descricao**: Descrição detalhada
- **especificacoes_tecnicas**: Especificações técnicas
- **marca**: Marca do equipamento
- **modelo**: Modelo do equipamento
- **numero_serie**: Número de série
- **data_aquisicao**: Data de aquisição
- **valor_aquisicao**: Valor de aquisição
- **estado_conservacao**: Estado de conservação (excelente, bom, regular, ruim, inutilizável)
- **foto**: Foto do equipamento
- **manual_instrucoes**: Manual de instruções
- **ativo**: Se o equipamento está ativo

### EquipamentoSetor
Relacionamento entre equipamentos e setores de eventos:
- **setor**: Setor do evento
- **equipamento**: Equipamento a ser usado
- **quantidade_necessaria**: Quantidade necessária
- **quantidade_disponivel**: Quantidade disponível
- **observacoes**: Observações adicionais
- **data_inicio_uso**: Data de início do uso
- **data_fim_uso**: Data de fim do uso
- **responsavel_equipamento**: Freelance responsável
- **status**: Status (disponível, em uso, em manutenção, indisponível)

**Validação de Negócio**: Só é possível associar equipamentos a setores da mesma empresa. O sistema valida automaticamente se o equipamento pertence à mesma empresa do evento.

### ManutencaoEquipamento
Registro de manutenções:
- **equipamento**: Equipamento em manutenção
- **tipo_manutencao**: Tipo (preventiva, corretiva, calibração)
- **descricao**: Descrição da manutenção
- **data_inicio**: Data de início
- **data_fim**: Data de fim
- **custo**: Custo da manutenção
- **fornecedor**: Fornecedor da manutenção
- **responsavel**: Freelance responsável
- **status**: Status (agendada, em andamento, concluída, cancelada)

## Funcionalidades

### 1. Cadastro de Equipamentos
- Cadastro com empresa proprietária obrigatória
- Categorização por tipo de equipamento
- Upload de fotos e manuais
- Controle de estado de conservação

### 2. Associação a Setores
- **Validação automática**: Só permite associar equipamentos da mesma empresa
- Controle de quantidades necessárias vs disponíveis
- Definição de responsáveis
- Controle de período de uso

### 3. Controle de Manutenções
- Agendamento de manutenções
- Controle de custos
- Acompanhamento de status
- Relacionamento com fornecedores

### 4. Relatórios e Estatísticas
- Resumo por evento
- Cobertura de equipamentos
- Análise por categoria
- Status de manutenções

## APIs Disponíveis

### Equipamentos
- `GET /api/equipamentos/` - Lista equipamentos
- `POST /api/equipamentos/` - Cria equipamento
- `GET /api/equipamentos/{id}/` - Detalhes do equipamento
- `PUT /api/equipamentos/{id}/` - Atualiza equipamento
- `DELETE /api/equipamentos/{id}/` - Remove equipamento
- `GET /api/equipamentos/por_empresa/?empresa_id={id}` - Equipamentos por empresa

### Equipamentos em Setores
- `GET /api/equipamentos-setor/` - Lista associações
- `POST /api/equipamentos-setor/` - Cria associação (com validação)
- `GET /api/equipamentos-setor/por_setor/?setor_id={id}` - Por setor
- `GET /api/equipamentos-setor/por_evento/?evento_id={id}` - Por evento
- `GET /api/equipamentos-setor/resumo_evento/?evento_id={id}` - Resumo do evento

### Manutenções
- `GET /api/manutencoes/` - Lista manutenções
- `POST /api/manutencoes/` - Cria manutenção
- `POST /api/manutencoes/{id}/finalizar/` - Finaliza manutenção
- `GET /api/manutencoes/agendadas/` - Manutenções agendadas
- `GET /api/manutencoes/em_andamento/` - Manutenções em andamento

## Interface Web

### Visualização por Setor
- URL: `/setor/{setor_id}/equipamentos/`
- Mostra equipamentos associados ao setor
- Exibe quantidades e percentual de cobertura
- Filtros por categoria e status

## Filtros Disponíveis

### Equipamentos
- Por empresa proprietária
- Por categoria
- Por estado de conservação
- Por status (ativo/inativo)
- Por código patrimonial (busca)

### Equipamentos em Setores
- Por empresa
- Por evento
- Por setor
- Por categoria
- Por status

### Manutenções
- Por equipamento
- Por tipo de manutenção
- Por status

## Validações de Negócio

1. **Propriedade de Equipamentos**: Todo equipamento deve pertencer a uma empresa
2. **Compatibilidade de Empresas**: Só é possível associar equipamentos a setores da mesma empresa
3. **Quantidades**: Quantidade disponível não pode ser maior que a necessária
4. **Datas**: Data de fim de uso deve ser posterior à data de início
5. **Status**: Transições de status seguem regras específicas

## Comandos de Gerenciamento

### Criar Categorias Iniciais
```bash
python manage.py criar_categorias_equipamentos
```

Categorias criadas:
- Áudio
- Iluminação
- Segurança
- Mobiliário
- Tecnologia
- Limpeza
- Cozinha
- Transporte

## Próximos Passos

1. **Interface de Usuário**: Desenvolver interface mais robusta para gerenciamento
2. **Notificações**: Sistema de alertas para manutenções pendentes
3. **Relatórios Avançados**: Dashboards com métricas detalhadas
4. **Integração**: Conectar com sistemas de fornecedores
5. **Mobile**: Aplicativo mobile para controle em campo

## Exemplos de Uso

### Criar Equipamento
```python
equipamento = Equipamento.objects.create(
    empresa_proprietaria=empresa,
    codigo_patrimonial="AUD001",
    categoria=categoria_audio,
    marca="JBL",
    modelo="EON615",
    estado_conservacao="bom"
)
```

### Associar a Setor (com validação)
```python
# Só funciona se equipamento e setor forem da mesma empresa
equipamento_setor = EquipamentoSetor.objects.create(
    setor=setor,
    equipamento=equipamento,
    quantidade_necessaria=2,
    quantidade_disponivel=1
)
```

### Verificar Cobertura
```python
cobertura = equipamento_setor.percentual_cobertura
faltante = equipamento_setor.quantidade_faltante
```
