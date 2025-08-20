# services/pagamentos.py
import mercadopago
from django.conf import settings

# services/pagamentos.py
from app_eventos.models import Freelance
from services.pix_service import pagar_freelancer

sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

def criar_pagamento_pix(valor, descricao, email_cliente):
    payment_data = {
        "transaction_amount": float(valor),
        "description": descricao,
        "payment_method_id": "pix",
        "payer": {
            "email": email_cliente
        }
    }
    result = sdk.payment().create(payment_data)
    return result["response"]




def pagar_todos():
    freelas = Freelance.objects.filter(pago=False)
    resultados = []
    for f in freelas:
        resultado = pagar_freelancer(f)
        resultados.append({f.nome: resultado})
    return resultados
