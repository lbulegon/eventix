#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_eventos.models import Vaga, Funcao

def alterar_vagas_para_seguranca():
    print("🔧 Iniciando alteração de vagas para Segurança...")
    
    # Buscar ou criar a função de Segurança
    funcao_seguranca, created = Funcao.objects.get_or_create(
        nome='Segurança',
        defaults={
            'descricao': 'Função de segurança para eventos',
            'tipo_funcao_id': 1
        }
    )
    
    if created:
        print(f'✅ Função "Segurança" criada com ID: {funcao_seguranca.id}')
    else:
        print(f'✅ Função "Segurança" encontrada com ID: {funcao_seguranca.id}')
    
    # Buscar todas as vagas
    vagas = Vaga.objects.all()
    total_vagas = vagas.count()
    
    print(f'📊 Total de vagas encontradas: {total_vagas}')
    
    if total_vagas == 0:
        print('⚠️ Nenhuma vaga encontrada no sistema!')
        return
    
    # Alterar todas as vagas para a função de Segurança
    vagas_atualizadas = 0
    for vaga in vagas:
        vaga.funcao = funcao_seguranca
        vaga.titulo = f'Segurança - {vaga.setor.nome if vaga.setor else "Setor"}'
        vaga.descricao = f'Vaga para Segurança no setor {vaga.setor.nome if vaga.setor else "Setor"} do evento {vaga.setor.evento.nome if vaga.setor and vaga.setor.evento else "Evento"}.'
        vaga.save()
        vagas_atualizadas += 1
    
    print(f'✅ {vagas_atualizadas} vagas alteradas para a função de Segurança!')
    
    # Mostrar algumas vagas como exemplo
    print('\n📋 Exemplos de vagas alteradas:')
    for vaga in vagas[:5]:
        print(f'   - {vaga.titulo} (ID: {vaga.id})')
    
    if total_vagas > 5:
        print(f'   ... e mais {total_vagas - 5} vagas')
    
    print('\n🎯 Todas as vagas agora são para a função de Segurança!')

if __name__ == '__main__':
    alterar_vagas_para_seguranca()
