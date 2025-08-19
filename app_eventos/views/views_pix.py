from rest_framework.response import Response
from rest_framework.decorators import api_view
from app_eventos.services.pagamentos import criar_pagamento_pix

@api_view(["POST"])
def gerar_pix(request):
    valor = request.data.get("valor")
    descricao = request.data.get("descricao")
    email = request.data.get("email")

    pagamento = criar_pagamento_pix(valor, descricao, email)
    return Response(pagamento)



@api_view(["POST"])
def webhook_mp(request):
    data = request.data
    print("Webhook Mercado Pago:", data)

    # Aqui você pode atualizar o status do pagamento no banco
    # Exemplo: Pedido.objects.filter(id=data["data"]["id"]).update(status="pago")

    return Response({"status": "ok"})
