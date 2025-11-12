import io
from pathlib import Path

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_eventos.models import Evento
from app_financeiro.models import OrcamentoOperacional

from .models import ContratoEvento
from .serializers import ContratoEventoSerializer

try:
    from reportlab.pdfgen import canvas

    REPORTLAB_AVAILABLE = True
except ImportError:  # pragma: no cover
    REPORTLAB_AVAILABLE = False


class BaseContratoView(APIView):
    permission_classes = [IsAuthenticated]

    def get_evento(self, request, evento_id: int) -> Evento:
        queryset = Evento.objects.all()
        user = request.user

        if getattr(user, "is_empresa_user", False):
            queryset = queryset.filter(empresa_contratante=user.empresa_contratante)
        elif getattr(user, "is_admin_sistema", False):
            queryset = queryset
        else:
            queryset = queryset.filter(ativo=True)

        return get_object_or_404(queryset, pk=evento_id)

    @staticmethod
    def can_edit(user) -> bool:
        return getattr(user, "is_empresa_user", False) or getattr(user, "is_admin_sistema", False)


class ContratoGerarView(BaseContratoView):
    def post(self, request, evento_id: int):
        evento = self.get_evento(request, evento_id)
        if not self.can_edit(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        orcamento_id = request.data.get("orcamento")
        orcamento = None
        if orcamento_id:
            orcamento = get_object_or_404(OrcamentoOperacional, pk=orcamento_id)

        condicoes = request.data.get("condicoes_gerais", "")

        pdf_url = self._gerar_pdf(evento, condicoes)

        contrato, created = ContratoEvento.objects.update_or_create(
            evento=evento,
            defaults={
                "orcamento": orcamento,
                "pdf_url": pdf_url,
                "assinatura_cliente": False,
                "data_assinatura": None,
                "condicoes_gerais": condicoes,
            },
        )

        serializer = ContratoEventoSerializer(contrato)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

    def _gerar_pdf(self, evento: Evento, condicoes: str) -> str:
        relative_path = Path("contratos") / f"contrato_evento_{evento.id}.pdf"
        output_path = Path(settings.MEDIA_ROOT) / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if REPORTLAB_AVAILABLE:
            buffer = io.BytesIO()
            pdf_canvas = canvas.Canvas(str(output_path))
            pdf_canvas.setFont("Helvetica", 12)
            pdf_canvas.drawString(50, 800, f"Contrato do Evento: {evento.nome}")
            pdf_canvas.drawString(50, 780, f"Data: {evento.data_inicio}")
            pdf_canvas.drawString(50, 760, "Condições Gerais:")
            text_object = pdf_canvas.beginText(50, 740)
            for line in condicoes.splitlines() or ["N/A"]:
                text_object.textLine(line)
            pdf_canvas.drawText(text_object)
            pdf_canvas.save()
            buffer.close()
        else:  # pragma: no cover - fallback textual
            output_path.write_text(
                f"Contrato do evento {evento.nome}\nCondições:\n{condicoes}",
                encoding="utf-8",
            )

        return f"{settings.MEDIA_URL}{relative_path.as_posix()}" if settings.MEDIA_URL else str(relative_path)


class ContratoAssinarView(BaseContratoView):
    def post(self, request, evento_id: int):
        evento = self.get_evento(request, evento_id)
        contrato = get_object_or_404(ContratoEvento, evento=evento)

        if not getattr(request.user, "is_empresa_user", False) and not getattr(request.user, "is_admin_sistema", False):
            return Response(status=status.HTTP_403_FORBIDDEN)

        contrato.assinatura_cliente = True
        contrato.data_assinatura = request.data.get("data_assinatura") or contrato.data_assinatura
        contrato.save(update_fields=["assinatura_cliente", "data_assinatura"])

        serializer = ContratoEventoSerializer(contrato)
        return Response(serializer.data, status=status.HTTP_200_OK)

