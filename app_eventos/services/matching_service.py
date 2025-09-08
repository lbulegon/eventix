# app_eventos/services/matching_service.py
from django.db.models import Q, F, Count
from django.utils import timezone
from typing import List, Dict, Any
import logging

from app_eventos.models import Vaga, Freelance, Candidatura, Funcao, SetorEvento

logger = logging.getLogger(__name__)


class MatchingService:
    """
    Serviço para matching inteligente entre freelancers e vagas
    """
    
    @staticmethod
    def encontrar_vagas_para_freelancer(freelancer: Freelance, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Encontra vagas recomendadas para um freelancer baseado em:
        - Experiência e habilidades
        - Localização
        - Disponibilidade
        - Histórico de candidaturas
        """
        try:
            # Buscar vagas ativas e publicadas
            vagas_base = Vaga.objects.filter(
                ativa=True,
                publicada=True,
                data_limite_candidatura__gte=timezone.now()
            ).select_related('setor__evento', 'funcao')
            
            # Filtrar vagas que o freelancer já se candidatou
            candidaturas_existentes = Candidatura.objects.filter(
                freelance=freelancer
            ).values_list('vaga_id', flat=True)
            
            vagas_base = vagas_base.exclude(id__in=candidaturas_existentes)
            
            # Calcular score para cada vaga
            vagas_com_score = []
            
            for vaga in vagas_base:
                score = MatchingService._calcular_score_freelancer_vaga(freelancer, vaga)
                
                if score > 0:  # Só incluir vagas com score positivo
                    vagas_com_score.append({
                        'vaga': vaga,
                        'score': score,
                        'motivos': MatchingService._obter_motivos_score(freelancer, vaga)
                    })
            
            # Ordenar por score (maior primeiro)
            vagas_com_score.sort(key=lambda x: x['score'], reverse=True)
            
            return vagas_com_score[:limite]
            
        except Exception as e:
            logger.error(f"Erro ao encontrar vagas para freelancer {freelancer.id}: {e}")
            return []
    
    @staticmethod
    def encontrar_freelancers_para_vaga(vaga: Vaga, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Encontra freelancers recomendados para uma vaga baseado em:
        - Experiência e habilidades
        - Localização
        - Disponibilidade
        - Histórico de performance
        """
        try:
            # Buscar freelancers ativos com cadastro completo
            freelancers_base = Freelance.objects.filter(
                usuario__is_active=True,
                cadastro_completo=True
            ).select_related('usuario')
            
            # Filtrar freelancers que já se candidataram
            candidaturas_existentes = Candidatura.objects.filter(
                vaga=vaga
            ).values_list('freelance_id', flat=True)
            
            freelancers_base = freelancers_base.exclude(id__in=candidaturas_existentes)
            
            # Calcular score para cada freelancer
            freelancers_com_score = []
            
            for freelancer in freelancers_base:
                score = MatchingService._calcular_score_vaga_freelancer(vaga, freelancer)
                
                if score > 0:  # Só incluir freelancers com score positivo
                    freelancers_com_score.append({
                        'freelancer': freelancer,
                        'score': score,
                        'motivos': MatchingService._obter_motivos_score(freelancer, vaga)
                    })
            
            # Ordenar por score (maior primeiro)
            freelancers_com_score.sort(key=lambda x: x['score'], reverse=True)
            
            return freelancers_com_score[:limite]
            
        except Exception as e:
            logger.error(f"Erro ao encontrar freelancers para vaga {vaga.id}: {e}")
            return []
    
    @staticmethod
    def _calcular_score_freelancer_vaga(freelancer: Freelance, vaga: Vaga) -> float:
        """
        Calcula score de compatibilidade entre freelancer e vaga
        Score de 0 a 100
        """
        score = 0.0
        
        # 1. Experiência (30 pontos)
        score += MatchingService._score_experiencia(freelancer, vaga) * 0.3
        
        # 2. Habilidades (25 pontos)
        score += MatchingService._score_habilidades(freelancer, vaga) * 0.25
        
        # 3. Localização (20 pontos)
        score += MatchingService._score_localizacao(freelancer, vaga) * 0.2
        
        # 4. Disponibilidade (15 pontos)
        score += MatchingService._score_disponibilidade(freelancer, vaga) * 0.15
        
        # 5. Histórico de performance (10 pontos)
        score += MatchingService._score_performance(freelancer) * 0.1
        
        return min(score, 100.0)  # Máximo 100
    
    @staticmethod
    def _calcular_score_vaga_freelancer(vaga: Vaga, freelancer: Freelance) -> float:
        """
        Calcula score de compatibilidade entre vaga e freelancer
        Mesma lógica, mas perspectiva da empresa
        """
        return MatchingService._calcular_score_freelancer_vaga(freelancer, vaga)
    
    @staticmethod
    def _score_experiencia(freelancer: Freelance, vaga: Vaga) -> float:
        """Calcula score baseado na experiência"""
        # Implementar lógica baseada em:
        # - Experiência mínima da vaga vs experiência do freelancer
        # - Nível de experiência (iniciante, intermediário, etc.)
        # - Experiência específica na área
        
        if not vaga.experiencia_minima:
            return 50.0  # Score neutro se não há requisito mínimo
        
        # Calcular experiência do freelancer (implementar baseado em histórico)
        experiencia_freelancer = 0  # TODO: Implementar cálculo real
        
        if experiencia_freelancer >= vaga.experiencia_minima:
            return 100.0
        elif experiencia_freelancer >= vaga.experiencia_minima * 0.7:
            return 70.0
        elif experiencia_freelancer >= vaga.experiencia_minima * 0.5:
            return 50.0
        else:
            return 20.0
    
    @staticmethod
    def _score_habilidades(freelancer: Freelance, vaga: Vaga) -> float:
        """Calcula score baseado nas habilidades"""
        # Implementar matching de habilidades
        # - Habilidades do freelancer vs requisitos da vaga
        # - Função específica vs experiência do freelancer
        
        if not vaga.requisitos:
            return 50.0  # Score neutro se não há requisitos específicos
        
        # TODO: Implementar análise de texto dos requisitos
        # e matching com habilidades do freelancer
        
        return 60.0  # Placeholder
    
    @staticmethod
    def _score_localizacao(freelancer: Freelance, vaga: Vaga) -> float:
        """Calcula score baseado na localização"""
        # Implementar lógica de proximidade geográfica
        # - Cidade do freelancer vs cidade do evento
        # - Distância máxima aceitável
        
        try:
            cidade_freelancer = freelancer.cidade.lower() if freelancer.cidade else ""
            cidade_evento = vaga.setor.evento.local.cidade.lower() if vaga.setor.evento.local else ""
            
            if cidade_freelancer == cidade_evento:
                return 100.0
            elif cidade_freelancer and cidade_evento:
                # TODO: Implementar cálculo de distância real
                return 70.0
            else:
                return 30.0
        except:
            return 50.0
    
    @staticmethod
    def _score_disponibilidade(freelancer: Freelance, vaga: Vaga) -> float:
        """Calcula score baseado na disponibilidade"""
        # Implementar lógica de disponibilidade
        # - Horários disponíveis do freelancer vs horários da vaga
        # - Conflitos com outros eventos
        
        # TODO: Implementar verificação de conflitos de agenda
        return 80.0  # Placeholder
    
    @staticmethod
    def _score_performance(freelancer: Freelance) -> float:
        """Calcula score baseado no histórico de performance"""
        try:
            # Calcular taxa de aprovação
            total_candidaturas = Candidatura.objects.filter(freelance=freelancer).count()
            candidaturas_aprovadas = Candidatura.objects.filter(
                freelance=freelancer,
                status='aprovado'
            ).count()
            
            if total_candidaturas == 0:
                return 50.0  # Score neutro para freelancers sem histórico
            
            taxa_aprovacao = candidaturas_aprovadas / total_candidaturas
            return taxa_aprovacao * 100
            
        except:
            return 50.0
    
    @staticmethod
    def _obter_motivos_score(freelancer: Freelance, vaga: Vaga) -> List[str]:
        """Retorna motivos do score calculado"""
        motivos = []
        
        # Adicionar motivos baseados nos scores calculados
        if MatchingService._score_experiencia(freelancer, vaga) > 80:
            motivos.append("Experiência adequada")
        
        if MatchingService._score_localizacao(freelancer, vaga) > 80:
            motivos.append("Localização próxima")
        
        if MatchingService._score_habilidades(freelancer, vaga) > 70:
            motivos.append("Habilidades compatíveis")
        
        return motivos


class VagaRecommendationService:
    """
    Serviço para recomendações de vagas
    """
    
    @staticmethod
    def obter_vagas_trending(limite: int = 10) -> List[Vaga]:
        """Retorna vagas em alta (com mais candidaturas)"""
        return Vaga.objects.filter(
            ativa=True,
            publicada=True,
            data_limite_candidatura__gte=timezone.now()
        ).annotate(
            total_candidaturas=Count('candidaturas')
        ).order_by('-total_candidaturas', '-data_criacao')[:limite]
    
    @staticmethod
    def obter_vagas_urgentes(limite: int = 10) -> List[Vaga]:
        """Retorna vagas urgentes"""
        return Vaga.objects.filter(
            ativa=True,
            publicada=True,
            urgente=True,
            data_limite_candidatura__gte=timezone.now()
        ).order_by('data_limite_candidatura')[:limite]
    
    @staticmethod
    def obter_vagas_por_localizacao(cidade: str, limite: int = 10) -> List[Vaga]:
        """Retorna vagas por localização"""
        return Vaga.objects.filter(
            ativa=True,
            publicada=True,
            data_limite_candidatura__gte=timezone.now(),
            setor__evento__local__cidade__icontains=cidade
        ).order_by('-data_criacao')[:limite]
    
    @staticmethod
    def obter_vagas_por_funcao(funcao_id: int, limite: int = 10) -> List[Vaga]:
        """Retorna vagas por função"""
        return Vaga.objects.filter(
            ativa=True,
            publicada=True,
            data_limite_candidatura__gte=timezone.now(),
            funcao_id=funcao_id
        ).order_by('-data_criacao')[:limite]
