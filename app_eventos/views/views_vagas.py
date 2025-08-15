from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app_eventos.permissions.permissions_freelance import IsCadastroCompleto
from app_eventos.models import Vaga  # Exemplo

class ListaVagasFreelanceView(APIView):
    permission_classes = [IsAuthenticated, IsCadastroCompleto]

    def get(self, request):
        vagas = Vaga.objects.filter(ativa=True)
        vagas_data = [{"id": v.id, "titulo": v.titulo, "descricao": v.descricao} for v in vagas]
        return Response(vagas_data)
