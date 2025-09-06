# 📊 Análise de Endpoints - Eventix Mobile vs Django Backend

## 🎯 Resumo Executivo

**Status**: Análise completa dos endpoints existentes vs. necessários para o app mobile Eventix.

## 📋 Endpoints Configurados no Flutter (app_config.dart)

### ✅ **Autenticação**
- `POST /api/v1/token/` - Login
- `POST /api/v1/token/refresh/` - Refresh token
- `POST /api/v1/token/verify/` - Verificar token
- `GET /api/v1/users/profile/` - Perfil do usuário

### ✅ **Freelancers**
- `POST /api/v1/freelancer/pre-cadastro/` - Pré-cadastro freelancer
- `GET /api/v1/vagas/` - Vagas disponíveis
- `POST /api/v1/freelancer-vaga/candidatar/` - Candidatar-se
- `POST /api/v1/freelancer-vaga/cancelar/` - Cancelar candidatura
- `GET /api/v1/freelancer-vaga/minhas-vagas/` - Minhas candidaturas

### ✅ **Eventos**
- `GET /api/v1/eventos/` - Listar eventos
- `GET /api/v1/eventos/meus-eventos/` - Meus eventos
- `POST /api/v1/eventos/criar/` - Criar evento

### ✅ **Empresas**
- `GET /api/v1/empresas/` - Listar empresas
- `GET /api/v1/empresas/minha-empresa/` - Minha empresa

### ✅ **Recuperação de Senha**
- `POST /api/v1/password/password-reset/` - Reset senha
- `POST /api/v1/password/password-reset/confirm/` - Confirmar reset

## 🔍 Endpoints Existentes no Django Backend

### ✅ **Autenticação (api_v01)**
- `POST /api/auth/login/` - Login único
- `POST /api/auth/refresh/` - Refresh token
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/perfil/` - Perfil do usuário
- `GET /api/auth/tipo-usuario/` - Verificar tipo de usuário

### ✅ **Registro (api_v01)**
- `POST /api/auth/registro/` - Registro único
- `POST /api/auth/registro/freelancer/` - Registro freelancer
- `POST /api/auth/registro/empresa/` - Registro empresa

### ✅ **Empresas (api_v01)**
- `GET /api/auth/empresas/` - Listar empresas

### ✅ **Sistema Financeiro (api_v01)**
- `GET /api/auth/categorias-financeiras/` - Categorias financeiras
- `GET /api/auth/eventos/<id>/despesas/` - Despesas do evento
- `POST /api/auth/despesas/` - Criar despesa
- `PUT /api/auth/despesas/<id>/` - Atualizar despesa
- `GET /api/auth/eventos/<id>/receitas/` - Receitas do evento
- `POST /api/auth/receitas/` - Criar receita
- `PUT /api/auth/receitas/<id>/` - Atualizar receita
- `GET /api/auth/eventos/<id>/fluxo-caixa/` - Fluxo de caixa do evento
- `GET /api/auth/fluxo-caixa-empresa/` - Fluxo de caixa da empresa

### ✅ **Fornecedores (api_v01)**
- `GET /api/auth/fornecedores/` - Listar fornecedores
- `GET /api/auth/fornecedores/<id>/` - Detalhes do fornecedor
- `POST /api/auth/fornecedores/criar/` - Criar fornecedor
- `PUT /api/auth/fornecedores/<id>/atualizar/` - Atualizar fornecedor
- `GET /api/auth/fornecedores/<id>/despesas/` - Despesas do fornecedor

### ✅ **Equipamentos (app_eventos)**
- `GET /api/equipamentos/categorias/` - Categorias de equipamentos
- `GET /api/equipamentos/equipamentos/` - Listar equipamentos
- `POST /api/equipamentos/equipamentos/` - Criar equipamento
- `GET /api/equipamentos/equipamentos/<id>/` - Detalhes do equipamento
- `PUT /api/equipamentos/equipamentos/<id>/` - Atualizar equipamento
- `DELETE /api/equipamentos/equipamentos/<id>/` - Remover equipamento
- `GET /api/equipamentos/equipamentos-setor/` - Equipamentos por setor
- `POST /api/equipamentos/equipamentos-setor/` - Associar equipamento ao setor
- `GET /api/equipamentos/manutencoes/` - Listar manutenções
- `POST /api/equipamentos/manutencoes/` - Criar manutenção

## ❌ **Endpoints FALTANDO no Django Backend**

### 🚨 **Críticos para o App Mobile**

#### **1. Sistema de Vagas e Candidaturas**
```
❌ GET /api/v1/vagas/ - Vagas disponíveis
❌ POST /api/v1/freelancer-vaga/candidatar/ - Candidatar-se
❌ POST /api/v1/freelancer-vaga/cancelar/ - Cancelar candidatura
❌ GET /api/v1/freelancer-vaga/minhas-vagas/ - Minhas candidaturas
```

#### **2. Sistema de Eventos Completo**
```
❌ GET /api/v1/eventos/ - Listar eventos
❌ GET /api/v1/eventos/meus-eventos/ - Meus eventos
❌ POST /api/v1/eventos/criar/ - Criar evento
❌ GET /api/v1/eventos/<id>/ - Detalhes do evento
❌ PUT /api/v1/eventos/<id>/ - Atualizar evento
❌ DELETE /api/v1/eventos/<id>/ - Remover evento
```

#### **3. Gestão de Empresas**
```
❌ GET /api/v1/empresas/minha-empresa/ - Minha empresa
❌ PUT /api/v1/empresas/minha-empresa/ - Atualizar empresa
```

#### **4. Sistema de Freelancers**
```
❌ POST /api/v1/freelancer/pre-cadastro/ - Pré-cadastro freelancer
❌ GET /api/v1/freelancer/perfil/ - Perfil do freelancer
❌ PUT /api/v1/freelancer/perfil/ - Atualizar perfil freelancer
```

#### **5. Recuperação de Senha**
```
❌ POST /api/v1/password/password-reset/ - Reset senha
❌ POST /api/v1/password/password-reset/confirm/ - Confirmar reset
```

#### **6. Verificação de Token**
```
❌ POST /api/v1/token/verify/ - Verificar token
```

## 🔧 **Problemas de Compatibilidade**

### **1. Diferenças de URL Base**
- **Flutter**: `/api/v1/`
- **Django**: `/api/auth/` (para autenticação)

### **2. Estrutura de Endpoints**
- **Flutter**: Endpoints específicos por funcionalidade
- **Django**: Endpoints agrupados por app (auth, equipamentos)

### **3. Nomenclatura**
- **Flutter**: `freelancer-vaga`, `minhas-vagas`
- **Django**: Não implementado

## 📋 **Plano de Implementação**

### **Fase 1: Endpoints Críticos (Prioridade ALTA)**
1. **Sistema de Vagas**
   - Modelo `Vaga`
   - Modelo `FreelancerVaga` (candidaturas)
   - ViewSets para CRUD

2. **Sistema de Eventos**
   - ViewSet para `Evento`
   - Endpoints de listagem e detalhes

3. **Autenticação Mobile**
   - Endpoint de verificação de token
   - Recuperação de senha

### **Fase 2: Endpoints de Suporte (Prioridade MÉDIA)**
1. **Gestão de Freelancers**
   - Perfil do freelancer
   - Pré-cadastro

2. **Gestão de Empresas**
   - Minha empresa
   - Atualização de dados

### **Fase 3: Endpoints Avançados (Prioridade BAIXA)**
1. **Sistema Financeiro Mobile**
2. **Fornecedores Mobile**
3. **Equipamentos Mobile**

## 🎯 **Recomendações**

### **1. Criar App API Mobile**
```python
# Criar novo app: api_mobile
python manage.py startapp api_mobile
```

### **2. Estrutura de URLs**
```python
# setup/urls.py
urlpatterns = [
    path("api/v1/", include("api_mobile.urls")),
    path("api/auth/", include("api_v01.urls.urls")),
    path("api/equipamentos/", include("app_eventos.urls.urls_equipamentos")),
]
```

### **3. Modelos Necessários**
```python
# api_mobile/models.py
class Vaga(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    funcao = models.ForeignKey(Funcao, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    # ... outros campos

class FreelancerVaga(models.Model):
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    data_candidatura = models.DateTimeField(auto_now_add=True)
    # ... outros campos
```

### **4. ViewSets Necessários**
```python
# api_mobile/views.py
class VagaViewSet(viewsets.ModelViewSet):
    queryset = Vaga.objects.all()
    serializer_class = VagaSerializer

class FreelancerVagaViewSet(viewsets.ModelViewSet):
    queryset = FreelancerVaga.objects.all()
    serializer_class = FreelancerVagaSerializer
```

## 📊 **Status Atual**

| Categoria | Endpoints Flutter | Endpoints Django | Status |
|-----------|------------------|------------------|---------|
| Autenticação | 4 | 5 | ✅ 80% |
| Freelancers | 5 | 0 | ❌ 0% |
| Eventos | 3 | 0 | ❌ 0% |
| Empresas | 2 | 1 | ⚠️ 50% |
| Recuperação | 2 | 0 | ❌ 0% |
| **TOTAL** | **16** | **6** | **37.5%** |

## 🚀 **Próximos Passos**

1. **Implementar endpoints críticos** (Vagas, Eventos)
2. **Criar app api_mobile** para organização
3. **Implementar ViewSets** com DRF
4. **Testar integração** Flutter ↔ Django
5. **Documentar APIs** com Swagger/OpenAPI

---

**Conclusão**: O backend Django tem uma base sólida, mas precisa de implementação significativa para suportar todas as funcionalidades do app mobile. A prioridade deve ser os endpoints de vagas e eventos, que são fundamentais para o funcionamento do app.
