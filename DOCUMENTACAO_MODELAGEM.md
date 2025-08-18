# Documentação da Modelagem do Sistema Eventix

## Visão Geral

O sistema Eventix é uma plataforma completa de gestão de eventos com arquitetura multi-tenant, permitindo que múltiplas empresas utilizem o sistema de forma isolada e segura. A modelagem foi desenvolvida seguindo as melhores práticas do Django e inclui funcionalidades avançadas para gestão de eventos, recursos humanos, equipamentos, financeiro e muito mais.

## Arquitetura Multi-Tenant

O sistema utiliza uma arquitetura multi-tenant baseada em **EmpresaContratante**, onde cada empresa tem seus dados completamente isolados através de relacionamentos com a empresa contratante.

### Modelo Base: EmpresaContratante
- **Propósito**: Representa uma empresa que contratou o sistema Eventix
- **Isolamento**: Todos os dados são vinculados a uma empresa contratante específica
- **Controle de Acesso**: Middleware personalizado para controle de acesso por empresa

## Estrutura dos Modelos

### 1. Gestão de Usuários e Autenticação

#### User (Modelo de Usuário Customizado)
- **Herança**: `AbstractUser` do Django
- **Tipos de Usuário**:
  - `admin_empresa`: Administrador da Empresa
  - `operador_empresa`: Operador da Empresa
  - `freelancer`: Freelancer
  - `admin_sistema`: Administrador do Sistema
- **Funcionalidades**:
  - Controle de permissões por tipo de usuário
  - Vinculação com empresa contratante
  - Controle de acesso e atividade

### 2. Gestão de Empresas e Parceiros

#### EmpresaContratante
- **Dados Fiscais**: CNPJ, Razão Social, Nome Fantasia
- **Contato**: Telefone, E-mail, Website
- **Endereço**: CEP, Logradouro, Número, Complemento, Bairro, Cidade, UF
- **Contrato**: Data de Contratação, Vencimento, Plano, Valor Mensal
- **Status**: Controle de atividade

#### Empresa (Parceiras)
- **Propósito**: Empresas parceiras (locais, fornecedores, etc.)
- **Vinculação**: Relacionamento com empresa contratante
- **Tipos**: Categorização por tipo de empresa

### 3. Gestão de Eventos

#### Evento
- **Informações Básicas**: Nome, Data Início/Fim, Descrição
- **Localização**: Vinculação com LocalEvento
- **Empresas**: Produtora e Contratante de Mão de Obra
- **Controle**: Status ativo/inativo

#### LocalEvento
- **Características**: Nome, Endereço, Capacidade
- **Proprietário**: Empresa proprietária do local
- **Vinculação**: Com empresa contratante

#### SetorEvento
- **Propósito**: Divisão de áreas dentro de um evento
- **Vinculação**: Relacionamento com evento

### 4. Gestão de Equipamentos

#### CategoriaEquipamento
- **Classificação**: Categorias como Áudio, Iluminação, Segurança
- **Isolamento**: Por empresa contratante

#### Equipamento
- **Identificação**: Código Patrimonial, Marca, Modelo, Número de Série
- **Especificações**: Descrição, Especificações Técnicas
- **Valor**: Data de Aquisição, Valor de Aquisição
- **Estado**: Conservação (Excelente, Bom, Regular, Ruim, Inutilizável)
- **Arquivos**: Foto, Manual de Instruções

#### EquipamentoSetor
- **Relacionamento**: Equipamento ↔ Setor de Evento
- **Controle**: Quantidade Necessária vs Disponível
- **Status**: Disponível, Em Uso, Em Manutenção, Indisponível
- **Responsabilidade**: Freelance responsável pelo equipamento

#### ManutencaoEquipamento
- **Tipos**: Preventiva, Corretiva, Calibração
- **Controle**: Data Início/Fim, Custo, Fornecedor
- **Status**: Agendada, Em Andamento, Concluída, Cancelada

### 5. Gestão de Recursos Humanos

#### Freelance
- **Dados Pessoais**: Nome Completo, CPF, RG, Data de Nascimento
- **Documentação**: PIS/PASEP, Carteira de Trabalho, Título de Eleitor
- **Endereço**: Endereço completo
- **Dados Bancários**: Banco, Agência, Conta, PIX
- **Arquivos Obrigatórios**: Exame Médico, Comprovante de Residência, Identidade
- **Controle**: Verificação de cadastro completo

#### Vaga
- **Vinculação**: Com Setor de Evento
- **Informações**: Título, Quantidade, Remuneração, Descrição

#### Candidatura
- **Propósito**: Pré-cadastro de freelance para vaga
- **Status**: Pendente, Aprovado, Rejeitado

#### ContratoFreelance
- **Propósito**: Freelance aprovado para vaga
- **Status**: Ativo, Finalizado, Cancelado

### 6. Sistema de Avaliações

#### AvaliacaoFreelance
- **Avaliador**: Usuário que avalia o freelance
- **Critérios**: Desempenho, Pontualidade, Profissionalismo (1-5)
- **Feedback**: Comentários, Recomendação

#### AvaliacaoEvento
- **Avaliador**: Freelance que avalia o evento
- **Critérios**: Organização, Condições de Trabalho, Remuneração (1-5)
- **Feedback**: Comentários, Recomendação

### 7. Sistema Financeiro

#### FormaPagamento
- **Tipos**: PIX, Transferência, Boleto, Cartão, etc.
- **Isolamento**: Por empresa contratante

#### PagamentoFreelance
- **Vinculação**: Com ContratoFreelance
- **Controle**: Valor, Data de Pagamento/Vencimento
- **Status**: Pendente, Aprovado, Pago, Cancelado, Estornado
- **Comprovante**: Arquivo de comprovante

#### DespesaEvento
- **Tipos**: Equipamento, Alimentação, Transporte, Hospedagem, Material, Serviço
- **Controle**: Valor, Fornecedor, Data, Forma de Pagamento
- **Comprovante**: Arquivo de comprovante

### 8. Sistema de Notificações

#### TipoNotificacao
- **Templates**: Título e mensagem padrão
- **Reutilização**: Templates para diferentes tipos de notificação

#### Notificacao
- **Destinatário**: Usuário específico
- **Prioridade**: Baixa, Média, Alta, Urgente
- **Status**: Lida/Não lida
- **Link**: Relacionado à notificação

### 9. Sistema de Comunicação

#### CanalComunicacao
- **Tipos**: E-mail, SMS, WhatsApp, Push Notification, Sistema Interno
- **Configuração**: Por empresa contratante

#### Mensagem
- **Destinatários**: Múltiplos usuários
- **Canal**: Vinculação com canal de comunicação
- **Status**: Rascunho, Enviada, Entregue, Lida, Falha
- **Anexos**: Arquivos anexados

### 10. Gestão de Tarefas e Checklists

#### ChecklistEvento
- **Vinculação**: Com evento específico
- **Responsabilidade**: Usuário responsável
- **Controle**: Data limite, conclusão

#### ItemChecklist
- **Vinculação**: Com checklist
- **Ordem**: Sequência dos itens
- **Responsabilidade**: Usuário responsável pelo item
- **Status**: Concluído/Não concluído

#### Tarefa
- **Propósito**: Tarefas gerais do sistema
- **Prioridade**: Baixa, Média, Alta, Urgente
- **Status**: Pendente, Em Andamento, Concluída, Cancelada
- **Vinculação**: Com evento (opcional)

### 11. Sistema de Templates e Documentos

#### TemplateDocumento
- **Tipos**: Contrato, Termo de Compromisso, Checklist, Relatório, E-mail, SMS
- **Variáveis**: JSON com variáveis disponíveis
- **Reutilização**: Templates por empresa

#### DocumentoGerado
- **Vinculação**: Com template
- **Variáveis**: Valores utilizados na geração
- **Arquivo**: Documento gerado
- **Evento**: Relacionamento com evento (opcional)

### 12. Relatórios e Estatísticas

#### RelatorioEvento
- **Tipos**: Financeiro, Recursos Humanos, Equipamentos, Avaliações, Geral
- **Arquivo**: Relatório gerado
- **Controle**: Usuário que gerou, data de geração

#### EstatisticaEmpresa
- **Métricas**: Total de eventos, freelances, equipamentos
- **Financeiro**: Receita total, despesa total, lucro total
- **Atualização**: Data da última atualização

### 13. Configurações do Sistema

#### ConfiguracaoSistema
- **Notificações**: Configurações de e-mail, push, SMS
- **Segurança**: Tempo de sessão, tentativas de login, senha forte
- **Relatórios**: Geração automática, frequência
- **Backup**: Configurações de backup automático

#### ConfiguracaoEmpresa
- **Eventos**: Máximo simultâneos, prazo de cancelamento
- **Freelances**: Exigência de documentos, avaliação obrigatória
- **Equipamentos**: Controle de estoque, alerta de manutenção
- **Pagamentos**: Prazo, multa por atraso

### 14. Sistema de Auditoria e Logs

#### LogAuditoria
- **Ações**: Criar, Editar, Excluir, Visualizar, Login, Logout, Exportar, Importar
- **Rastreamento**: Usuário, IP, User Agent
- **Objeto**: Modelo e ID do objeto afetado
- **Descrição**: Detalhes da ação

### 15. Integrações e APIs

#### IntegracaoAPI
- **Tipos**: Pagamento, E-mail, SMS, WhatsApp, Calendário
- **Configuração**: URL base, API Key, API Secret
- **Controle**: Status ativo/inativo, última sincronização

#### LogIntegracao
- **Rastreamento**: Ações, status, dados enviados/recebidos
- **Performance**: Tempo de resposta
- **Erros**: Detalhes de falhas

### 16. Backup e Versionamento

#### BackupSistema
- **Tipos**: Completo, Incremental, Diferencial
- **Controle**: Status, tamanho do arquivo, data início/conclusão
- **Arquivo**: Backup gerado

#### VersaoSistema
- **Controle**: Número da versão, nome, data de lançamento
- **Mudanças**: Lista de alterações em JSON
- **Obrigatoriedade**: Versões obrigatórias vs opcionais

## Características Técnicas

### Multi-Tenancy
- **Isolamento**: Todos os modelos principais têm relacionamento com `EmpresaContratante`
- **Segurança**: Middleware para controle de acesso por empresa
- **Escalabilidade**: Suporte a múltiplas empresas sem interferência

### Validações e Integridade
- **Constraints**: `unique_together` para evitar duplicatas
- **Validações**: Métodos `clean()` para validações customizadas
- **Relacionamentos**: Foreign Keys com `CASCADE` e `SET_NULL` apropriados

### Performance
- **Índices**: Campos de busca e relacionamentos indexados
- **Queries**: Otimização através de `select_related` e `prefetch_related`
- **Paginação**: Suporte para grandes volumes de dados

### Segurança
- **Auditoria**: Logs completos de todas as ações
- **Controle de Acesso**: Permissões baseadas em tipo de usuário
- **Isolamento**: Dados completamente separados por empresa

## Funcionalidades Avançadas

### Sistema de Avaliações Bidirecional
- Empresas avaliam freelances
- Freelances avaliam eventos
- Cálculo automático de notas médias

### Gestão Completa de Equipamentos
- Controle de estoque automático
- Sistema de manutenção
- Rastreamento de responsáveis

### Sistema Financeiro Integrado
- Controle de pagamentos
- Gestão de despesas
- Relatórios financeiros

### Comunicação Multicanal
- Múltiplos canais de comunicação
- Templates reutilizáveis
- Rastreamento de entrega

### Workflow de Tarefas
- Checklists para eventos
- Tarefas com prioridades
- Controle de responsabilidades

## Próximos Passos

1. **Migrações**: Criar e aplicar migrações do banco de dados
2. **Admin**: Configurar interface administrativa
3. **API**: Desenvolver endpoints REST
4. **Frontend**: Interface de usuário
5. **Testes**: Testes unitários e de integração
6. **Deploy**: Configuração de produção

Esta modelagem fornece uma base sólida e escalável para o sistema Eventix, com todas as funcionalidades necessárias para gestão completa de eventos, recursos humanos, equipamentos e financeiro.

## Novos Modelos Adicionados - Controle de Estoque e Transporte

### 17. Gestão de Estoque e Insumos

#### CategoriaInsumo
- **Classificação**: Categorias como Alimentação, Bebidas, Material de Limpeza
- **Isolamento**: Por empresa contratante
- **Controle**: Status ativo/inativo

#### Insumo
- **Identificação**: Código, Nome, Categoria
- **Especificações**: Descrição, Especificações, Unidade de Medida
- **Controle de Estoque**: Estoque Mínimo, Estoque Atual, Local de Armazenamento
- **Validade**: Data de validade para controle de perecíveis
- **Fornecedor**: Empresa fornecedora do insumo
- **Preço**: Preço unitário para controle financeiro
- **Arquivos**: Foto do insumo

#### InsumoSetor
- **Relacionamento**: Insumo ↔ Setor de Evento
- **Controle**: Quantidade Necessária vs Alocada vs Transportada
- **Status**: Pendente, Alocado, Em Transporte, Entregue, Insuficiente
- **Responsabilidade**: Freelance responsável pelo insumo
- **Data de Necessidade**: Quando o insumo é necessário no setor

### 18. Planejamento de Transporte

#### TipoVeiculo
- **Características**: Nome, Descrição
- **Capacidades**: Capacidade de Carga (kg), Capacidade de Volume (m³)
- **Controle**: Status ativo/inativo

#### Veiculo
- **Identificação**: Placa, Modelo, Ano, Cor
- **Tipo**: Vinculação com TipoVeiculo
- **Proprietário**: Empresa proprietária
- **Motorista**: Freelance responsável
- **Status**: Disponível, Em Uso, Em Manutenção, Indisponível

#### RotaTransporte
- **Informações**: Nome da Rota, Origem, Destino
- **Veículo e Motorista**: Vinculação com veículo e motorista
- **Datas**: Saída, Chegada Prevista, Chegada Real
- **Custos**: Combustível, Pedágio
- **Status**: Planejada, Em Andamento, Concluída, Cancelada

#### ItemTransporte
- **Tipos**: Equipamento, Insumo, Outro
- **Vinculação**: Com rota de transporte
- **Especificações**: Quantidade, Peso Unitário, Volume Unitário
- **Destino**: Setor de destino
- **Cálculos**: Peso Total, Volume Total

### 19. Controle Avançado de Equipamentos

#### StatusEquipamento
- **Personalização**: Status customizados por empresa
- **Identificação Visual**: Cor em hexadecimal
- **Controle**: Status ativo/inativo

#### ControleEquipamento
- **Tipos de Controle**: Estoque, Manutenção, Compra, Aluguel, Empréstimo
- **Quantidades**: Atual, Necessária, Em Manutenção, Para Comprar, Alugada
- **Controle Temporal**: Última Verificação, Próxima Verificação
- **Responsabilidade**: Freelance responsável
- **Cálculos**: Quantidade Disponível, Faltante, Percentual de Cobertura

#### PedidoCompraEquipamento
- **Identificação**: Número do Pedido único
- **Fornecedor**: Empresa fornecedora
- **Detalhes**: Quantidade, Valor Unitário, Valor Total
- **Datas**: Pedido, Entrega Prevista, Entrega Real
- **Status**: Rascunho, Enviado, Aprovado, Em Produção, Pronto para Envio, Enviado, Recebido, Cancelado
- **Controle**: Solicitante, Aprovador

#### AluguelEquipamento
- **Fornecedor**: Empresa de aluguel
- **Período**: Data Início, Data Fim, Data Devolução
- **Valores**: Valor Diário, Valor Total
- **Status**: Solicitado, Aprovado, Em Uso, Devolvido, Cancelado
- **Cálculos**: Dias de Aluguel, Valor Calculado

### 20. Relatórios e Dashboards de Estoque

#### RelatorioEstoque
- **Tipos**: Estoque Geral, Estoque Baixo, Controle de Validade, Relatório de Transporte, Status de Equipamentos, Pedidos de Compra, Aluguéis
- **Dados**: JSON com dados do relatório
- **Arquivo**: Relatório gerado
- **Controle**: Usuário que gerou, data de geração

#### DashboardEstoque
- **Métricas de Equipamentos**: Total, Disponíveis, Em Manutenção, Alugados
- **Métricas de Insumos**: Total, Estoque Baixo, Vencendo
- **Métricas de Transporte**: Rotas Ativas, Veículos Disponíveis
- **Métricas de Compras**: Pedidos Pendentes, Aluguéis Ativos
- **Cálculos**: Percentual de Equipamentos Disponíveis, Percentual de Insumos Críticos

## Funcionalidades Avançadas de Logística

### Controle Completo de Estoque
- **Insumos**: Controle de quantidade, validade, local de armazenamento
- **Equipamentos**: Status detalhado, manutenção, aluguel, compra
- **Alertas**: Estoque baixo, vencimento próximo, manutenção necessária

### Planejamento de Transporte
- **Rotas**: Planejamento completo de rotas com veículos e motoristas
- **Itens**: Controle de peso e volume dos itens transportados
- **Custos**: Combustível, pedágio, custos totais
- **Rastreamento**: Status em tempo real das rotas

### Gestão de Fornecedores
- **Insumos**: Controle de fornecedores de insumos
- **Equipamentos**: Fornecedores de equipamentos e aluguel
- **Veículos**: Empresas proprietárias de veículos

### Relatórios e Dashboards
- **Relatórios Específicos**: Por tipo de material, status, fornecedor
- **Dashboards**: Visão geral de toda a logística
- **Métricas**: Percentuais de disponibilidade, cobertura, eficiência

### Workflow de Aprovação
- **Pedidos de Compra**: Fluxo de aprovação com solicitante e aprovador
- **Aluguéis**: Controle de solicitação e aprovação
- **Transporte**: Planejamento e execução de rotas

## Benefícios dos Novos Modelos

### Para Gestão de Eventos
- **Controle Total**: Tudo que é necessário para o evento
- **Rastreabilidade**: Onde está cada item, equipamento ou insumo
- **Eficiência**: Otimização de recursos e transporte

### Para Controle Financeiro
- **Custos de Transporte**: Combustível, pedágio, manutenção
- **Pedidos de Compra**: Controle de gastos com equipamentos
- **Aluguéis**: Custos de aluguel de equipamentos

### Para Logística
- **Planejamento**: Rotas otimizadas com veículos adequados
- **Capacidade**: Controle de peso e volume dos transportes
- **Tempo**: Controle de datas de entrega e necessidade

### Para Auditoria
- **Rastreamento**: Histórico completo de movimentações
- **Responsabilidades**: Quem é responsável por cada item
- **Status**: Situação atual de cada equipamento e insumo

Esta expansão da modelagem torna o sistema Eventix uma solução completa de gestão logística para eventos, com controle total de estoque, transporte e equipamentos.
