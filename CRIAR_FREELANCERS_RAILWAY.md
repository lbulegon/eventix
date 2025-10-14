# 🚀 Como Criar Freelancers no Railway

## 📋 Problema

Os freelancers foram criados no **banco de dados local**, mas não aparecem no Railway porque ele usa um **banco PostgreSQL separado**.

---

## ✅ Solução: Executar Comando no Railway

### **Método 1: Via Railway CLI (Recomendado)**

#### 1. Verificar se o Railway CLI está instalado:
```bash
railway --version
```

Se não estiver instalado:
```bash
npm i -g @railway/cli
```

#### 2. Fazer login no Railway:
```bash
railway login
```

#### 3. Executar o comando para criar freelancers:
```bash
railway run python manage.py criar_freelancers_teste --empresa-id=1 --funcao-id=58
```

**Parâmetros:**
- `--empresa-id=1` : ID da empresa contratante (padrão: 1)
- `--funcao-id=58` : ID da função Auxiliar de Cozinha

---

### **Método 2: Via Dashboard do Railway**

1. Acesse o [Railway Dashboard](https://railway.app/)
2. Abra seu projeto **eventix-development**
3. Clique na aba **Settings**
4. Role até **Deploy**
5. Clique em **Run Command**
6. Execute:
```bash
python manage.py criar_freelancers_teste --empresa-id=1 --funcao-id=58
```

---

### **Método 3: Via Django Admin no Railway**

1. Acesse: https://eventix-development.up.railway.app/admin/
2. Faça login como admin
3. Vá em **Freelancers**
4. Clique em **Adicionar Freelancer**
5. Preencha os dados manualmente

---

### **Método 4: Verificar IDs Corretos Primeiro**

Antes de criar, verifique se a empresa ID=1 e função ID=58 existem no Railway:

```bash
railway run python manage.py shell
```

Depois execute:
```python
from app_eventos.models import EmpresaContratante, Funcao

# Verificar empresas
print("Empresas:")
for e in EmpresaContratante.objects.all():
    print(f"  ID {e.id}: {e.nome_fantasia}")

# Verificar funções
print("\nFunções:")
for f in Funcao.objects.all()[:20]:
    print(f"  ID {f.id}: {f.nome}")

# Sair
exit()
```

---

## 🔍 Verificar se Funcionou

### **1. Via Django Admin:**
```
https://eventix-development.up.railway.app/admin/app_eventos/freelance/
```

### **2. Via Dashboard Empresa:**
```
https://eventix-development.up.railway.app/empresa/freelancers/
```

### **3. Via API:**
```bash
curl https://eventix-development.up.railway.app/api/auth/freelancers/
```

---

## 📝 Freelancers que Serão Criados

O comando criará 8 freelancers de teste:

1. João Silva (@joao_silva_teste)
2. Maria Santos (@maria_santos_teste)
3. Pedro Oliveira (@pedro_oliveira_teste)
4. Ana Costa (@ana_costa_teste)
5. Carlos Ferreira (@carlos_ferreira_teste)
6. Julia Almeida (@julia_almeida_teste)
7. Lucas Pereira (@lucas_pereira_teste)
8. Fernanda Lima (@fernanda_lima_teste)

**Credenciais:**
- Username: qualquer um dos acima
- Senha: `senha123`

---

## 🎯 Associar Freelancers Existentes à Função

Se já existem freelancers no Railway mas não estão associados à função, execute:

```bash
railway run python manage.py shell
```

```python
from app_eventos.models import Freelance, Funcao, FreelancerFuncao

funcao = Funcao.objects.get(id=58)  # Auxiliar de Cozinha

for freelance in Freelance.objects.all():
    FreelancerFuncao.objects.get_or_create(
        freelancer=freelance,
        funcao=funcao,
        defaults={'nivel': 'intermediario'}
    )
    print(f"✅ {freelance.nome_completo} associado")

exit()
```

---

## ⚠️ Troubleshooting

### **Erro: Empresa não encontrada**
```bash
# Listar empresas disponíveis
railway run python manage.py shell -c "from app_eventos.models import EmpresaContratante; [print(f'ID {e.id}: {e.nome_fantasia}') for e in EmpresaContratante.objects.all()]"
```

### **Erro: Função não encontrada**
```bash
# Listar funções disponíveis
railway run python manage.py shell -c "from app_eventos.models import Funcao; [print(f'ID {f.id}: {f.nome}') for f in Funcao.objects.all()[:50]]"
```

### **CPF duplicado**
Se o erro for de CPF duplicado, edite o arquivo e mude os CPFs.

---

## 🚀 Após Criar os Freelancers

1. ✅ Acesse o dashboard: https://eventix-development.up.railway.app/empresa/freelancers/
2. ✅ Verifique se os 8 freelancers aparecem
3. ✅ Crie uma vaga para a função "Auxiliar de Cozinha"
4. ✅ Verifique se as notificações foram enviadas

---

## 📚 Comandos Úteis

```bash
# Listar todos os comandos disponíveis
railway run python manage.py help

# Ver freelancers no banco
railway run python manage.py shell -c "from app_eventos.models import Freelance; print(f'Total: {Freelance.objects.count()}')"

# Ver funções de um freelancer
railway run python manage.py shell -c "from app_eventos.models import Freelance; f = Freelance.objects.first(); print([ff.funcao.nome for ff in f.funcoes.all()])"
```

---

**Última atualização:** Outubro 2025

