import mercadopago
from django.conf import settings

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
