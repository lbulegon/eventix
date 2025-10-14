import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_eventos.models import Freelance, FreelancerFuncao

print("📋 Lista de Freelancers:\n")
for f in Freelance.objects.all()[:10]:
    funcoes = FreelancerFuncao.objects.filter(freelancer=f)
    print(f"ID {f.id}: {f.nome_completo} ({f.usuario.username})")
    print(f"   Funções: {[ff.funcao.nome for ff in funcoes]}")
    print(f"   CPF: {f.cpf}")
    print(f"   Telefone: {f.telefone}")
    print()

print(f"\n📊 Total: {Freelance.objects.count()} freelancers")
print(f"📊 Com função associada: {FreelancerFuncao.objects.values('freelancer').distinct().count()}")

