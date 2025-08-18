# Exemplo Prático - Gestão de Estoque Hierárquico

## Cenário: Evento "Festival de Música 2024"

### 1. Configuração Inicial

#### Estoque Geral da Empresa (Insumo)
```python
# Criar insumo no estoque geral
insumo_cabo = Insumo.objects.create(
    empresa_contratante=empresa_eventix,
    empresa_fornecedora=fornecedor_eletronicos,
    categoria=categoria_cabos,
    codigo="CAB-001",
    nome="Cabo de Energia 10m",
    unidade_medida="unidade",
    preco_unitario=25.00,
    estoque_minimo=10,
    estoque_atual=100,
    local_armazenamento="Depósito Central"
)

print(f"Estoque disponível: {insumo_cabo.estoque_disponivel}")  # 90 unidades
```

### 2. Planejamento do Evento

#### Criar Evento
```python
evento_festival = Evento.objects.create(
    empresa_contratante=empresa_eventix,
    nome="Festival de Música 2024",
    data_inicio=date(2024, 7, 15),
    data_fim=date(2024, 7, 17),
    local=local_parque_central
)

# Criar setores do evento
setor_palco_principal = SetorEvento.objects.create(
    evento=evento_festival,
    nome="Palco Principal",
    descricao="Palco principal do festival"
)

setor_palco_secundario = SetorEvento.objects.create(
    evento=evento_festival,
    nome="Palco Secundário",
    descricao="Palco secundário do festival"
)
```

### 3. Alocação de Estoque para o Evento

#### Alocar Insumos do Estoque Geral para o Evento
```python
# Alocar 50 cabos para o evento
sucesso, resultado = insumo_cabo.alocar_para_evento(
    evento=evento_festival,
    quantidade=50,
    responsavel=usuario_admin
)

if sucesso:
    insumo_evento = resultado
    print(f"Alocados {insumo_evento.quantidade_alocada_evento} cabos para o evento")
else:
    print(f"Erro: {resultado}")

# Verificar estoque disponível após alocação
print(f"Estoque geral disponível: {insumo_cabo.estoque_real_disponivel}")  # 40 unidades
```

### 4. Distribuição pelos Setores

#### Definir Necessidades por Setor
```python
# Palco Principal precisa de 30 cabos
insumo_setor_principal = InsumoSetor.objects.create(
    setor=setor_palco_principal,
    insumo_evento=insumo_evento,
    quantidade_necessaria=30,
    responsavel_insumo=freelance_tecnico
)

# Palco Secundário precisa de 20 cabos
insumo_setor_secundario = InsumoSetor.objects.create(
    setor=setor_palco_secundario,
    insumo_evento=insumo_evento,
    quantidade_necessaria=20,
    responsavel_insumo=freelance_tecnico
)
```

#### Alocar Quantidades para os Setores
```python
# Alocar 25 cabos para o palco principal
sucesso = insumo_setor_principal.alocar_quantidade(25)
if sucesso:
    print("25 cabos alocados para o palco principal")

# Alocar 15 cabos para o palco secundário
sucesso = insumo_setor_secundario.alocar_quantidade(15)
if sucesso:
    print("15 cabos alocados para o palco secundário")

# Verificar distribuição
print(f"Quantidade distribuída pelos setores: {insumo_evento.quantidade_distribuida_setores}")  # 40
print(f"Quantidade disponível para distribuição: {insumo_evento.quantidade_disponivel_distribuicao}")  # 10
```

### 5. Utilização Durante o Evento

#### Registrar Utilização nos Setores
```python
# Palco principal utilizou 22 cabos
sucesso = insumo_setor_principal.registrar_utilizacao(22)
if sucesso:
    print("22 cabos utilizados no palco principal")

# Palco secundário utilizou 12 cabos
sucesso = insumo_setor_secundario.registrar_utilizacao(12)
if sucesso:
    print("12 cabos utilizados no palco secundário")

# Verificar utilização total do evento
print(f"Quantidade utilizada no evento: {insumo_evento.quantidade_utilizada_evento}")  # 34
print(f"Percentual de utilização: {insumo_evento.percentual_utilizacao:.1f}%")  # 85.0%
```

### 6. Análise e Relatórios

#### Relatório de Utilização por Setor
```python
# Verificar quantidade não utilizada por setor
nao_utilizado_principal = insumo_setor_principal.quantidade_nao_utilizada  # 3
nao_utilizado_secundario = insumo_setor_secundario.quantidade_nao_utilizada  # 3

print(f"Palco Principal - Não utilizado: {nao_utilizado_principal}")
print(f"Palco Secundário - Não utilizado: {nao_utilizado_secundario}")

# Verificar quantidade não utilizada no evento
nao_utilizado_evento = insumo_evento.quantidade_nao_utilizada  # 6
print(f"Total não utilizado no evento: {nao_utilizado_evento}")
```

#### Relatório de Estoque Geral
```python
# Verificar alocações para todos os eventos
total_alocado_eventos = insumo_cabo.get_quantidade_alocada_eventos()
total_utilizado_eventos = insumo_cabo.get_quantidade_utilizada_eventos()

print(f"Total alocado para eventos: {total_alocado_eventos}")
print(f"Total utilizado em eventos: {total_utilizado_eventos}")
print(f"Estoque realmente disponível: {insumo_cabo.estoque_real_disponivel}")
```

### 7. Cenários de Uso

#### Cenário 1: Estoque Insuficiente
```python
# Tentar alocar mais do que disponível
sucesso, resultado = insumo_cabo.alocar_para_evento(
    evento=evento_festival,
    quantidade=100,  # Mais do que disponível
    responsavel=usuario_admin
)

if not sucesso:
    print(f"Erro: {resultado}")  # "Estoque insuficiente"
```

#### Cenário 2: Distribuição Excedente
```python
# Tentar alocar mais do que disponível no evento
sucesso = insumo_setor_principal.alocar_quantidade(20)  # Só tem 10 disponíveis
if not sucesso:
    print("Quantidade não disponível para distribuição")
```

#### Cenário 3: Utilização Excedente
```python
# Tentar registrar mais utilização do que alocado
sucesso = insumo_setor_secundario.registrar_utilizacao(10)  # Só tem 3 alocados
if not sucesso:
    print("Quantidade não disponível para utilização")
```

### 8. Benefícios da Arquitetura

#### Controle Granular
- **Estoque Geral**: Controle central da empresa
- **Estoque do Evento**: Controle por evento específico
- **Estoque do Setor**: Controle detalhado por área

#### Rastreabilidade
- Saber exatamente quanto foi alocado para cada evento
- Acompanhar utilização real vs. planejada
- Identificar desperdícios e otimizações

#### Flexibilidade
- Reutilização de insumos entre eventos
- Redistribuição entre setores
- Planejamento baseado em dados históricos

#### Relatórios Precisos
- Quantidade usada em cada evento
- Eficiência de utilização por setor
- Custos reais por evento
- Previsão para eventos futuros

### 9. Comandos Úteis

#### Verificar Status do Estoque
```python
# Verificar todos os insumos que precisam de reposição
insumos_baixo_estoque = Insumo.objects.filter(
    estoque_atual__lte=F('estoque_minimo')
)

# Verificar alocações pendentes
alocacoes_pendentes = InsumoEvento.objects.filter(status='pendente')

# Verificar distribuições pendentes
distribuicoes_pendentes = InsumoSetor.objects.filter(status='pendente')
```

#### Relatórios Automáticos
```python
# Relatório de utilização por evento
for evento in Evento.objects.all():
    insumos_evento = evento.insumos_evento.all()
    total_utilizado = sum(ie.quantidade_utilizada_evento for ie in insumos_evento)
    print(f"{evento.nome}: {total_utilizado} unidades utilizadas")

# Relatório de eficiência por setor
for setor in SetorEvento.objects.all():
    insumos_setor = setor.insumos_setor.all()
    for insumo_setor in insumos_setor:
        eficiencia = (insumo_setor.quantidade_utilizada / insumo_setor.quantidade_alocada) * 100
        print(f"{setor.nome} - {insumo_setor.insumo_evento.insumo.nome}: {eficiencia:.1f}%")
```

Esta arquitetura permite um controle preciso e rastreável do estoque, garantindo que você possa calcular exatamente as quantidades usadas em cada evento, conforme solicitado.
