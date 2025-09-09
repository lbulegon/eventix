#!/usr/bin/env python
"""
Script para testar todas as funções do sistema (incluindo Auxiliar de Cozinha)
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_eventos.models import Funcao, TipoFuncao, FreelancerFuncao, Freelance

def test_funcoes_completas():
    """Testar todas as funções do sistema"""
    print("=== TESTANDO TODAS AS FUNÇÕES DO SISTEMA ===")
    
    try:
        # 1. Verificar funções disponíveis
        print("1. Funções disponíveis:")
        funcoes = Funcao.objects.all()
        for funcao in funcoes:
            print(f"   - {funcao.nome}: {funcao.descricao}")
        
        print(f"\nTotal de funções: {funcoes.count()}")
        
        # 2. Verificar se as 6 funções estão corretas
        print(f"\n2. Verificação das funções:")
        funcoes_esperadas = ['Segurança', 'Atendente', 'Caixa', 'Chapista', 'Cachorrista', 'Auxiliar de Cozinha']
        funcoes_existentes = [f.nome for f in funcoes]
        
        todas_presentes = True
        for funcao_esperada in funcoes_esperadas:
            if funcao_esperada in funcoes_existentes:
                print(f"   ✅ {funcao_esperada}")
            else:
                print(f"   ❌ {funcao_esperada} - FALTANDO!")
                todas_presentes = False
        
        if todas_presentes:
            print(f"\n🎉 Todas as 6 funções estão presentes!")
        else:
            print(f"\n❌ Algumas funções estão faltando!")
        
        # 3. Estatísticas por função
        print(f"\n3. Estatísticas por função:")
        for funcao in funcoes:
            count = FreelancerFuncao.objects.filter(funcao=funcao).count()
            print(f"   - {funcao.nome}: {count} freelancers")
        
        # 4. Freelancers com função Auxiliar de Cozinha
        print(f"\n4. Freelancers com função 'Auxiliar de Cozinha':")
        auxiliares = FreelancerFuncao.objects.filter(funcao__nome='Auxiliar de Cozinha').select_related('freelancer')
        for auxiliar in auxiliares:
            print(f"   - {auxiliar.freelancer.nome_completo}: {auxiliar.nivel}")
        
        # 5. Estatísticas por nível
        print(f"\n5. Estatísticas por nível:")
        niveis = ['iniciante', 'intermediario', 'avancado', 'expert']
        for nivel in niveis:
            count = FreelancerFuncao.objects.filter(nivel=nivel).count()
            print(f"   - {nivel}: {count} associações")
        
        # 6. Resumo geral
        print(f"\n6. Resumo geral:")
        print(f"   - Tipos de função: {TipoFuncao.objects.count()}")
        print(f"   - Funções: {funcoes.count()}")
        print(f"   - Freelancers: {Freelance.objects.count()}")
        print(f"   - Associações freelancer-função: {FreelancerFuncao.objects.count()}")
        
        # 7. Verificar se não há funções extras
        funcoes_extras = [f for f in funcoes_existentes if f not in funcoes_esperadas]
        if funcoes_extras:
            print(f"\n⚠️ Funções extras encontradas: {funcoes_extras}")
        else:
            print(f"\n✅ Nenhuma função extra encontrada - apenas as 6 esperadas!")
        
        print(f"\n🎉 Teste das funções completas concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_funcoes_completas()
