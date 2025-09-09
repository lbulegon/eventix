#!/usr/bin/env python
"""
Script para atualizar os valores das vagas do evento no Parque do Harmonia
- Limpeza: R$ 80,00 -> R$ 150,00
- Segurança: R$ 120,00 -> R$ 180,00
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventix.settings')
django.setup()

from app_eventos.models import Vaga, Funcao, Evento

def atualizar_valores_vagas():
    print("=== ATUALIZANDO VALORES DAS VAGAS ===")
    
    try:
        # Buscar o evento "Evento no Parque do Harmonia"
        evento = Evento.objects.get(nome="Evento no Parque do Harmonia")
        print(f"✅ Evento encontrado: {evento.nome}")
        
        # Buscar as funções
        funcao_limpeza = Funcao.objects.get(nome="Limpeza")
        funcao_seguranca = Funcao.objects.get(nome="Segurança")
        print(f"✅ Função Limpeza encontrada: ID {funcao_limpeza.id}")
        print(f"✅ Função Segurança encontrada: ID {funcao_seguranca.id}")
        
        # Atualizar vagas de Limpeza
        vagas_limpeza = Vaga.objects.filter(
            setor__evento=evento,
            funcao=funcao_limpeza
        )
        
        print(f"\n📋 Vagas de Limpeza encontradas: {vagas_limpeza.count()}")
        for vaga in vagas_limpeza:
            print(f"  - Vaga ID {vaga.id}: R$ {vaga.remuneracao} -> R$ 150.00")
            vaga.remuneracao = 150.00
            vaga.save()
        
        # Atualizar vagas de Segurança
        vagas_seguranca = Vaga.objects.filter(
            setor__evento=evento,
            funcao=funcao_seguranca
        )
        
        print(f"\n📋 Vagas de Segurança encontradas: {vagas_seguranca.count()}")
        for vaga in vagas_seguranca:
            print(f"  - Vaga ID {vaga.id}: R$ {vaga.remuneracao} -> R$ 180.00")
            vaga.remuneracao = 180.00
            vaga.save()
        
        print(f"\n✅ Atualização concluída!")
        print(f"   - {vagas_limpeza.count()} vagas de Limpeza atualizadas para R$ 150,00")
        print(f"   - {vagas_seguranca.count()} vagas de Segurança atualizadas para R$ 180,00")
        
        # Verificar se as alterações foram aplicadas
        print(f"\n🔍 Verificando alterações...")
        for vaga in vagas_limpeza:
            vaga.refresh_from_db()
            print(f"   - Limpeza ID {vaga.id}: R$ {vaga.remuneracao}")
        
        for vaga in vagas_seguranca:
            vaga.refresh_from_db()
            print(f"   - Segurança ID {vaga.id}: R$ {vaga.remuneracao}")
        
    except Evento.DoesNotExist:
        print("❌ Evento 'Evento no Parque do Harmonia' não encontrado!")
    except Funcao.DoesNotExist as e:
        print(f"❌ Função não encontrada: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    atualizar_valores_vagas()
