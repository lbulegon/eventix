from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from app_eventos.models import Freelance
from app_eventos.serializers.serializers_freelance import FreelanceDocumentosSerializer

class UploadDocumentosFreelanceView(APIView):
    """
    Endpoint para upload de documentos obrigatórios do freelancer.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            freelance = Freelance.objects.get(usuario=request.user)
        except Freelance.DoesNotExist:
            return Response({"detail": "Perfil de freelancer não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FreelanceDocumentosSerializer(freelance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Documentos enviados com sucesso!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
