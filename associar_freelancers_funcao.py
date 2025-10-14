"""
Script para associar freelancers existentes à função Auxiliar de Cozinha (ID 58)
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_eventos.models import User, Freelance, Funcao, FreelancerFuncao

def associar_freelancers():
    try:
        # Buscar a função
        funcao = Funcao.objects.get(id=58)
        print(f"✅ Função encontrada: {funcao.nome} (ID {funcao.id})")
        
        # Buscar todos os freelancers
        freelancers = Freelance.objects.all()
        print(f"✅ Total de freelancers no sistema: {freelancers.count()}")
        
        associados = 0
        ja_associados = 0
        
        for freelance in freelancers:
            # Verificar se já está associado
            if FreelancerFuncao.objects.filter(freelancer=freelance, funcao=funcao).exists():
                ja_associados += 1
                print(f"   ⚠️ {freelance.nome_completo} já está associado à função")
                continue
            
            # Associar à função
            FreelancerFuncao.objects.create(
                freelancer=freelance,
                funcao=funcao,
                nivel='intermediario',
            )
            associados += 1
            print(f"   ✅ {freelance.nome_completo} associado à função")
        
        print(f"\n🎉 Resumo:")
        print(f"   - Total de freelancers: {freelancers.count()}")
        print(f"   - Associados agora: {associados}")
        print(f"   - Já associados antes: {ja_associados}")
        print(f"   - Função: {funcao.nome} (ID {funcao.id})")
        
        # Mostrar lista de freelancers
        print(f"\n📋 Lista de Freelancers:")
        for freelance in freelancers:
            funcoes = FreelancerFuncao.objects.filter(freelancer=freelance)
            print(f"   - {freelance.nome_completo} ({freelance.usuario.username})")
            print(f"     Funções: {', '.join([ff.funcao.nome for ff in funcoes])}")
        
    except Funcao.DoesNotExist:
        print("❌ Função ID 58 não encontrada!")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🚀 Associando freelancers à função Auxiliar de Cozinha...\n")
    associar_freelancers()

