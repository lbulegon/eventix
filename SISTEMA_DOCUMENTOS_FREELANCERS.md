# 📄 Sistema de Documentação de Freelancers - Eventix

## 🎯 Visão Geral

O Eventix possui um **sistema completo de gestão de documentos** que permite que cada empresa contratante defina:
- ✅ Documentos obrigatórios para freelancers
- ✅ Período de validade de cada documento
- ✅ Reutilização de documentos entre vagas
- ✅ Validação de documentos por vaga ou evento

---

## 📋 Modelos Implementados

### 1. **DocumentoFreelancerEmpresa**
Armazena os documentos dos freelancers por empresa.

**Campos principais:**
- `empresa_contratante` - Empresa dona do documento
- `freelancer` - Freelancer que enviou o documento
- `tipo_documento` - Tipo do documento (RG, CPF, CTPS, etc.)
- `arquivo` - Arquivo do documento
- `status` - Status: pendente, aprovado, rejeitado, expirado
- `data_vencimento` - Data de vencimento do documento
- `pode_reutilizar` - Se pode ser reutilizado em outras vagas
- `total_reutilizacoes` - Quantas vezes foi reutilizado

**Tipos de Documentos:**
```python
- 'rg' - RG
- 'cpf' - CPF  
- 'ctps' - Carteira de Trabalho
- 'comprovante_residencia' - Comprovante de Residência
- 'certificado_reservista' - Certificado de Reservista
- 'comprovante_escolaridade' - Comprovante de Escolaridade
- 'certificado_profissional' - Certificado Profissional
- 'outros' - Outros
```

**Métodos úteis:**
```python
# Verifica se o documento está válido
documento.esta_valido  # True/False

# Verifica se pode ser reutilizado
documento.pode_ser_reutilizado  # True/False

# Marca como reutilizado
documento.marcar_como_reutilizado()
```

---

### 2. **ConfiguracaoDocumentosEmpresa**
Define quais documentos são obrigatórios para cada empresa.

**Campos de Configuração:**
```python
# Documentos obrigatórios
rg_obrigatorio = True/False
cpf_obrigatorio = True/False
ctps_obrigatorio = True/False
comprovante_residencia_obrigatorio = True/False
certificado_reservista_obrigatorio = False
comprovante_escolaridade_obrigatorio = False
certificado_profissional_obrigatorio = False

# Períodos de validade (em dias)
periodo_validade_rg = 365
periodo_validade_cpf = 365
periodo_validade_ctps = 365
periodo_validade_residencia = 90
periodo_validade_reservista = 365
periodo_validade_escolaridade = 365
periodo_validade_profissional = 365

# Configurações gerais
aceita_documentos_externos = True  # Aceita docs de outras empresas
periodo_validade_padrao = 365  # Validade padrão
```

**Métodos úteis:**
```python
# Retorna lista dos documentos obrigatórios
config.get_documentos_obrigatorios()  
# ['rg', 'cpf', 'ctps', 'comprovante_residencia']

# Retorna período de validade de um documento
config.get_periodo_validade('rg')  # 365
```

---

### 3. **ReutilizacaoDocumento**
Controla quando um documento é reutilizado em outra vaga.

**Campos:**
- `documento_original` - Documento que foi reutilizado
- `vaga_utilizada` - Vaga onde foi reutilizado
- `candidatura` - Candidatura associada
- `status_na_reutilizacao` - Status: aprovado, rejeitado, pendente

---

### 4. **VagaEmpresa**
Vagas específicas de cada empresa.

**Campos relacionados a documentos:**
```python
# Exige vínculo empregatício?
exige_vinculo_empregaticio = True/False

# Tipo de vínculo
tipo_vinculo = 'temporario' | 'intermitente' | 'terceirizado'

# Propriedade útil
vaga.exige_documentacao  # Retorna True se exige docs
```

---

## 🔄 Fluxos de Trabalho

### **Fluxo 1: Freelancer se Candidata a uma Vaga**

```
1. Freelancer visualiza vaga
2. Sistema verifica documentos obrigatórios da empresa
3. Se faltam documentos:
   - Mostra lista de documentos necessários
   - Freelancer faz upload
4. Se documentos OK:
   - Permite candidatura
5. Empresa valida documentos
6. Documento aprovado pode ser reutilizado
```

### **Fluxo 2: Reutilização de Documentos**

```
1. Freelancer tem documento aprovado na Empresa A
2. Freelancer se candidata a nova vaga da Empresa A
3. Sistema verifica:
   - Documento existe?
   - Está válido? (não venceu)
   - Está aprovado?
4. Se OK: Reutiliza automaticamente
5. Se não: Solicita novo upload
```

### **Fluxo 3: Configuração por Empresa**

```
1. Admin da empresa acessa configurações
2. Define documentos obrigatórios
3. Define períodos de validade
4. Configura se aceita documentos de outras empresas
5. Configuração salva
6. Aplica-se a todas as vagas da empresa
```

---

## 📊 Níveis de Exigência de Documentos

O sistema suporta **3 níveis de configuração**:

### **Nível 1: Global da Empresa**
```python
# Todos os freelancers da empresa precisam de:
ConfiguracaoDocumentosEmpresa
  ├── rg_obrigatorio = True
  ├── cpf_obrigatorio = True
  └── ctps_obrigatorio = True
```

### **Nível 2: Por Vaga**
```python
# Vagas específicas podem exigir documentos adicionais
VagaEmpresa
  ├── exige_vinculo_empregaticio = True  # Exige docs de vínculo
  └── tipo_vinculo = 'temporario'  # CTPS + Reservista (se homem)
```

### **Nível 3: Por Evento** (Para implementar)
```python
# TODO: Documentos específicos por evento
EventoDocumentacao
  ├── evento = Evento
  ├── documentos_obrigatorios = ['certificado_profissional']
  └── periodo_validade_especifico = 180
```

---

## 🚀 Funcionalidades Implementadas

### ✅ **Já Implementado:**

1. **Sistema de Documentos por Empresa**
   - Upload de documentos
   - Validação de documentos
   - Controle de validade
   - Reutilização de documentos

2. **Configuração Flexível**
   - Cada empresa define seus requisitos
   - Períodos de validade personalizáveis
   - Documentos obrigatórios por tipo

3. **Controle de Status**
   - Pendente → Aprovado → Expirado
   - Histórico de reutilizações
   - Validação por usuário autorizado

4. **Modelos de Vagas e Candidaturas**
   - VagaEmpresa com requisitos
   - CandidaturaEmpresa vinculada
   - FreelancerGlobal (marketplace)

---

## 📝 Funcionalidades a Implementar

### 🔧 **Para Completar o Sistema:**

#### 1. **Documentos Específicos por Evento**

```python
class EventoDocumentacao(models.Model):
    """Documentos específicos para um evento"""
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    documentos_obrigatorios = models.JSONField(
        default=list,
        help_text="Lista de tipos de documentos obrigatórios"
    )
    periodo_validade_especifico = models.PositiveIntegerField(
        default=180,
        help_text="Período de validade em dias para este evento"
    )
```

#### 2. **Documentos Específicos por Vaga**

```python
class VagaDocumentacao(models.Model):
    """Documentos específicos para uma vaga"""
    vaga = models.ForeignKey(VagaEmpresa, on_delete=models.CASCADE)
    tipo_documento = models.CharField(max_length=30, choices=TIPO_DOCUMENTO_CHOICES)
    obrigatorio = models.BooleanField(default=True)
    descricao = models.TextField(blank=True)
    periodo_validade = models.PositiveIntegerField(default=365)
```

#### 3. **API de Verificação de Documentos**

```python
# Endpoint para verificar se freelancer tem documentos OK
GET /api/v1/freelancers/{id}/verificar-documentos/?empresa_id=1&vaga_id=5

Response:
{
    "documentos_validos": true,
    "documentos_faltantes": [],
    "documentos_expirados": ["comprovante_residencia"],
    "pode_candidatar": false
}
```

#### 4. **Sistema de Notificações de Vencimento**

```python
# Signal para notificar documentos próximos ao vencimento
@receiver(post_save, sender=DocumentoFreelancerEmpresa)
def verificar_vencimento_proximo(sender, instance, **kwargs):
    if instance.dias_para_vencer() <= 30:
        criar_notificacao(
            freelancer=instance.freelancer,
            titulo="Documento próximo ao vencimento",
            mensagem=f"Seu {instance.get_tipo_documento_display()} vence em {instance.dias_para_vencer()} dias"
        )
```

#### 5. **Dashboard de Documentos para Freelancer**

```
/freelancer/documentos/
├── Documentos Enviados
│   ├── RG (Aprovado - Válido até 01/01/2026)
│   ├── CPF (Pendente)
│   └── CTPS (Expirado - Renovar)
├── Documentos Pendentes por Empresa
│   ├── Empresa A: Comprovante de Residência
│   └── Empresa B: Certificado Profissional
└── Histórico de Reutilizações
```

#### 6. **Dashboard de Validação para Empresa**

```
/empresa/documentos/
├── Documentos Pendentes de Validação (15)
│   ├── João Silva - RG (Enviado há 2 dias)
│   ├── Maria Santos - CTPS (Enviado há 1 hora)
│   └── ...
├── Documentos Aprovados (120)
├── Documentos Rejeitados (5)
└── Documentos Expirando em 30 dias (8)
```

---

## 💡 Exemplos de Uso

### **Exemplo 1: Configurar Documentos da Empresa**

```python
from app_eventos.models_documentos import ConfiguracaoDocumentosEmpresa

# Criar configuração
config = ConfiguracaoDocumentosEmpresa.objects.create(
    empresa_contratante=empresa,
    rg_obrigatorio=True,
    cpf_obrigatorio=True,
    ctps_obrigatorio=True,
    comprovante_residencia_obrigatorio=True,
    certificado_reservista_obrigatorio=False,  # Opcional
    periodo_validade_residencia=90,  # 3 meses
    aceita_documentos_externos=True
)

# Buscar documentos obrigatórios
docs = config.get_documentos_obrigatorios()
# ['rg', 'cpf', 'ctps', 'comprovante_residencia']
```

### **Exemplo 2: Freelancer Envia Documento**

```python
from app_eventos.models_documentos import DocumentoFreelancerEmpresa
from datetime import datetime, timedelta

# Upload de documento
documento = DocumentoFreelancerEmpresa.objects.create(
    empresa_contratante=empresa,
    freelancer=freelancer,
    tipo_documento='rg',
    arquivo=arquivo_upload,
    data_vencimento=datetime.now() + timedelta(days=365),
    status='pendente'
)
```

### **Exemplo 3: Empresa Valida Documento**

```python
# Aprovar documento
documento.status = 'aprovado'
documento.validado_por = usuario_empresa
documento.data_validacao = datetime.now()
documento.save()
```

### **Exemplo 4: Verificar se Freelancer Pode se Candidatar**

```python
def pode_candidatar(freelancer, vaga):
    """Verifica se freelancer tem todos os documentos"""
    empresa = vaga.empresa_contratante
    config = ConfiguracaoDocumentosEmpresa.objects.get(empresa_contratante=empresa)
    
    # Documentos obrigatórios
    docs_obrigatorios = config.get_documentos_obrigatorios()
    
    # Documentos do freelancer
    docs_freelancer = DocumentoFreelancerEmpresa.objects.filter(
        empresa_contratante=empresa,
        freelancer=freelancer,
        status='aprovado'
    )
    
    # Verificar cada documento
    for doc_tipo in docs_obrigatorios:
        doc = docs_freelancer.filter(tipo_documento=doc_tipo).first()
        
        if not doc:
            return False, f"Documento {doc_tipo} faltando"
        
        if not doc.esta_valido:
            return False, f"Documento {doc_tipo} expirado"
    
    return True, "Todos os documentos OK"
```

---

## 🎯 Recomendações de Implementação

### **Prioridade Alta:**

1. ✅ **API de Verificação de Documentos**
   - Endpoint para checar status dos documentos
   - Validação antes de permitir candidatura

2. ✅ **Dashboard de Documentos para Freelancer**
   - Página para ver status dos documentos
   - Upload de novos documentos
   - Notificações de vencimento

3. ✅ **Dashboard de Validação para Empresa**
   - Validar documentos pendentes
   - Ver histórico de documentos
   - Configurar documentos obrigatórios

### **Prioridade Média:**

4. ✅ **Documentos Específicos por Vaga**
   - Algumas vagas podem exigir certificados específicos
   - Interface para empresa definir

5. ✅ **Sistema de Notificações**
   - Alertas de documentos expirando
   - Notificações de documentos pendentes

### **Prioridade Baixa:**

6. ✅ **Documentos por Evento**
   - Para eventos específicos que exigem certificações

7. ✅ **Relatórios de Documentação**
   - Dashboard com estatísticas
   - Exportação de relatórios

---

## 📚 Arquivos Relacionados

**Modelos:**
- `app_eventos/models_documentos.py` - Modelos de documentos
- `app_eventos/models_freelancers.py` - Freelancers e vagas

**Views:**
- `app_eventos/views/views_freelance.py` - Upload de documentos

**Serializers:**
- `app_eventos/serializers/serializers_freelance.py` - Serializers

**Admin:**
- Configurável via Django Admin

---

## 🔒 Segurança

**Permissões:**
- Freelancer só vê seus próprios documentos
- Empresa só vê documentos de seus freelancers
- Admin do sistema vê tudo

**Armazenamento:**
- Documentos em: `media/documentos_freelancers_empresas/YYYY/MM/DD/`
- Protegidos por permissões

**Validação:**
- Apenas formatos permitidos (PDF, JPG, PNG)
- Tamanho máximo: 5MB
- Validação de autenticidade pela empresa

---

**Última atualização:** Outubro 2025  
**Status:** ✅ Sistema Base Implementado | 🔧 Melhorias em Andamento

