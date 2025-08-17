from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from app_eventos.models import SetorEvento, EquipamentoSetor


@login_required
def equipamentos_setor(request, setor_id):
    """
    Exibe os equipamentos de um setor específico
    """
    setor = get_object_or_404(SetorEvento, id=setor_id)
    equipamentos = EquipamentoSetor.objects.filter(
        setor=setor
    ).select_related(
        'equipamento', 'equipamento__categoria', 'responsavel_equipamento'
    ).order_by('equipamento__categoria__nome', 'equipamento__codigo_patrimonial')
    
    # Calcular estatísticas
    total_equipamentos = equipamentos.count()
    total_necessario = equipamentos.aggregate(
        total=Sum('quantidade_necessaria')
    )['total'] or 0
    total_disponivel = equipamentos.aggregate(
        total=Sum('quantidade_disponivel')
    )['total'] or 0
    
    if total_necessario > 0:
        percentual_cobertura = (total_disponivel / total_necessario) * 100
    else:
        percentual_cobertura = 100
    
    context = {
        'setor': setor,
        'equipamentos': equipamentos,
        'total_equipamentos': total_equipamentos,
        'total_necessario': total_necessario,
        'total_disponivel': total_disponivel,
        'percentual_cobertura': percentual_cobertura,
    }
    
    return render(request, 'equipamentos_setor.html', context)
