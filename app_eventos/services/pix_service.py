# services/pix_service.py
import mercadopago

sdk = mercadopago.SDK("SEU_ACCESS_TOKEN")

def pagar_freelancer(freelancer):
    if not freelancer.chave_pix or freelancer.valor_a_receber <= 0:
        return {"error": "Chave Pix inválida ou valor zerado"}

    payment_data = {
        "transaction_amount": float(freelancer.valor_a_receber),
        "description": f"Pagamento Eventix - {freelancer.nome}",
        "payment_method_id": "pix",
        "payer": {
            "email": freelancer.email,
            "first_name": freelancer.nome
        }
    }

    result = sdk.payment().create(payment_data)
    response = result["response"]

    if response.get("status") == "approved":
        freelancer.pago = True
        freelancer.save()
    return response
