# Eventix — Guia de Implementação Operacional (PostgreSQL)

## Objetivo

Implementar o blueprint operacional completo do Eventix sem alterar a estrutura já existente dos apps `eventos`, `vagas`, `setores`, `funcoes` e `freelancers`. Todo desenvolvimento deve ser incremental, com compatibilidade total ao banco PostgreSQL 14+, utilizando apenas migrations aditivas.

- **Banco:** PostgreSQL 14+
- **Driver:** `psycopg2`
- **Campos especiais:** utilizar `JSONField` e, quando necessário, `ArrayField` nativos do PostgreSQL.
- **Apps intocáveis:** `eventos`, `vagas`, `setores`, `funcoes`, `freelancers`
- **Regra de ouro:** novas funcionalidades sempre se relacionam a `eventos.Evento` via `ForeignKey` ou `OneToOneField`.

## Visão Geral do Blueprint

Fluxo completo do evento:

`Briefing → Menu → Orçamento → Contrato → Pré-Produção → Mise en Place → Dia do Evento → Finalização → Fechamento Interno → Planejamento Futuro`

Cada etapa se tornará um app Django independente, mantendo o core imutável.

## Apps Novos

| Ordem | App           | Responsabilidade principal |
|-------|---------------|-----------------------------|
| 1     | `briefing`    | Contexto e objetivos do evento |
| 2     | `menu`        | Cardápios, pratos e fichas técnicas |
| 3     | `financeiro`  | Orçamento operacional e custos |
| 4     | `contratos`   | Geração e assinatura de contratos |
| 5     | `producao`    | Cronogramas e tarefas de pré-produção |
| 6     | `mise`        | Preparação operacional (mise en place) |
| 7     | `operacao`    | Acompanhamento do dia do evento |
| 8     | `finalizacao` | Fechamento imediato pós-evento |
| 9     | `fechamento`  | Balanço interno e indicadores |
| 10    | `planejamento`| Insights e recomendações futuras |

### Recursos mínimos por app

- `models.py`: modelos conforme especificações.
- `serializers.py`: serializers DRF para CRUD/API.
- `views.py`: viewsets ou APIViews com regras de permissão.
- `urls.py`: rotas rest sob namespace do app.
- `tests.py`: pelo menos um teste de criação e leitura.
- `migrations/`: apenas migrations aditivas.
- `admin.py`: registros básicos para administração.

## Modelos a Implementar

### 1. briefing
```python
class Briefing(models.Model):
    evento = models.OneToOneField("eventos.Evento", on_delete=models.CASCADE, related_name="briefing")
    proposito = models.TextField()
    experiencia_desejada = models.TextField(blank=True)
    tipo_servico = models.CharField(max_length=100)
    publico_estimado = models.PositiveIntegerField(default=0)
    restricoes_alimentares = models.TextField(blank=True)
    orcamento_disponivel = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    infraestrutura_local = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
```

### 2. menu
```python
class Menu(models.Model):
    evento = models.ForeignKey("eventos.Evento", on_delete=models.CASCADE, related_name="menus")
    titulo = models.CharField(max_length=100)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

class Prato(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="pratos")
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    custo_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tempo_preparo_min = models.IntegerField(default=0)

class FichaTecnica(models.Model):
    prato = models.ForeignKey(Prato, on_delete=models.CASCADE, related_name="fichas")
    modo_preparo = models.TextField()
    rendimento = models.DecimalField(max_digits=8, decimal_places=2)
    tempo_execucao = models.IntegerField(default=0)
    insumos = models.JSONField(default=dict)
```

### 3. financeiro
```python
class OrcamentoOperacional(models.Model):
    evento = models.OneToOneField("eventos.Evento", on_delete=models.CASCADE, related_name="orcamento_operacional")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    margem = models.DecimalField(max_digits=5, decimal_places=2)
    lucro_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_precificacao = models.CharField(max_length=20, choices=[("percentual", "percentual"), ("minimo", "minimo")])
    data_calculo = models.DateTimeField(auto_now_add=True)
    detalhes_custos = models.JSONField(default=dict)
```

### 4. contratos
```python
class ContratoEvento(models.Model):
    evento = models.OneToOneField("eventos.Evento", on_delete=models.CASCADE)
    orcamento = models.ForeignKey("financeiro.OrcamentoOperacional", on_delete=models.SET_NULL, null=True)
    pdf_url = models.CharField(max_length=255, blank=True)
    assinatura_cliente = models.BooleanField(default=False)
    data_assinatura = models.DateTimeField(null=True, blank=True)
    condicoes_gerais = models.TextField()
```

### 5. producao
```python
class CronogramaPreProducao(models.Model):
    evento = models.ForeignKey("eventos.Evento", on_delete=models.CASCADE)
    etapa = models.CharField(max_length=100)
    prazo = models.DateTimeField()
    responsavel = models.ForeignKey("freelancers.Freelancer", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=15, default="pendente")
```

### 6. mise
```python
class MiseEnPlace(models.Model):
    evento = models.ForeignKey("eventos.Evento", on_delete=models.CASCADE)
    setor = models.ForeignKey("setores.Setor", on_delete=models.PROTECT)
    tarefa = models.CharField(max_length=255)
    responsavel = models.ForeignKey("freelancers.Freelancer", on_delete=models.SET_NULL, null=True)
    tempo_estimado_min = models.IntegerField(default=0)
    status = models.CharField(max_length=15, default="pendente")
```

### 7. operacao
```python
class OperacaoEvento(models.Model):
    evento = models.OneToOneField("eventos.Evento", on_delete=models.CASCADE)
    inicio_real = models.DateTimeField(null=True)
    fim_real = models.DateTimeField(null=True)
    status = models.CharField(max_length=15, default="em_preparacao")
    timeline = models.JSONField(default=dict)
```

### 8. finalizacao
```python
class FinalizacaoEvento(models.Model):
    evento = models.OneToOneField("eventos.Evento", on_delete=models.CASCADE)
    hora_extra = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)
    fechamento_bebidas = models.JSONField(default=dict)
    materiais_recolhidos = models.BooleanField(default=False)
```

### 9. fechamento
```python
class FechamentoInterno(models.Model):
    evento = models.OneToOneField("eventos.Evento", on_delete=models.CASCADE)
    perdas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    extravios = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    custo_real = models.DecimalField(max_digits=12, decimal_places=2)
    lucro_liquido = models.DecimalField(max_digits=12, decimal_places=2)
    aprendizado = models.TextField(blank=True)
    indicadores = models.JSONField(default=dict)
    criado_em = models.DateTimeField(auto_now_add=True)
```

### 10. planejamento
```python
class InsightEvento(models.Model):
    evento_base = models.ForeignKey("eventos.Evento", on_delete=models.CASCADE)
    recomendacao = models.TextField()
    relevancia = models.IntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
```

## Endpoints REST (api_v01)

Todos com prefixo `/api/v1/eventos/{id}/…`.

| Recurso | Método | Caminho | Descrição |
|---------|--------|---------|-----------|
| Briefing | GET/POST/PUT | `/briefing/` | Recupera ou cria briefing para o evento |
| Menu | GET/POST | `/menu/` | Lista ou cria menus do evento |
| Orçamento | POST | `/orcamento/gerar` | Gera orçamento operacional |
| Contrato | POST | `/contrato/gerar` | Gera contrato e PDF |
| Pré-produção | GET/POST | `/preproducao/cronograma` | CRUD do cronograma de pré-produção |
| Mise en Place | GET/POST | `/mise/` | CRUD das tarefas de mise |
| Operação | GET/PUT | `/operacao/timeline` | Atualiza timeline e status do dia do evento |
| Finalização | GET/PUT | `/finalizacao/` | Registra pós-evento imediato |
| Fechamento Interno | GET/PUT | `/fechamento/` | Persiste indicadores internos |
| Planejamento | GET/POST | `/planejamento/insights` | Cria/consulta insights para eventos futuros |

## Permissões

| Perfil | Ação |
|--------|------|
| Coordenador | CRUD completo em todos os módulos |
| Cozinha / Logística / Salão | Atualiza tarefas/checklists (mise, cronogramas) |
| Cliente | Consulta briefing/menu, aprova orçamento e contrato |

Implementar via DRF permissions customizadas, aproveitando os papéis já existentes no sistema.

## Geração de Contratos (PDF)

- Utilizar WeasyPrint (preferencial) ou ReportLab.
- Armazenar arquivos em S3 ou `MEDIA_ROOT` local (`pdf_url`).
- Assinatura simulada com `assinatura_cliente=True` + `data_assinatura`.

## Testes

Cada app novo deve conter ao menos:

- Teste de criação (POST) do recurso principal.
- Teste de leitura (GET) do recurso.
- Uso de `pytest-django` ou `django.test.TestCase`.

## Documentação (DRF Spectacular)

- Registrar todos os endpoints no schema.
- Descrever parâmetros, retornos e permissões.
- Expor documentação em `/api/schema/` e `/api/docs/` (caso ainda não exista).

## Roadmap de Implementação

1. **Setup**
   - Criar os apps e adicioná-los a `INSTALLED_APPS`.
   - Configurar URLs base em `api_v01`/`setup.urls`.

2. **Módulos Iniciais**
   - `briefing`: modelos, API e testes.
   - `menu`: integrações com fichas técnicas.

3. **Financeiro e Contratos**
   - `financeiro`: cálculos/margens e geração de dados.
   - `contratos`: geração de PDF e controle de assinatura.

4. **Operação**
   - `producao`, `mise`, `operacao` para pré-produção e dia do evento.

5. **Encerramento**
   - `finalizacao`, `fechamento`, `planejamento` para pós-evento e insights.

6. **Documentação e QA**
   - Atualizar schema DRF.
   - Executar testes e revisar integrações.

## Boas Práticas

- Manter migrations pequenas e bem descritas.
- Reutilizar serviços/utilitários em `app_eventos` quando fizer sentido.
- Validar dados via serializers (ex.: `orcamento_disponivel >= 0`).
- Garantir que filtros e buscas respeitem o escopo da empresa (`empresa_contratante`).
- Incluir seeds/fixtures quando necessário para ambientes de teste.

---

Seguindo este guia, o Eventix ganha todos os módulos do blueprint operacional sem quebrar o que já está em andamento, mantendo compatibilidade com PostgreSQL e preparando o terreno para automações futuras.

