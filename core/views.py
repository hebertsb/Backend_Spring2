import stripe
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["POST"])
def crear_pago(request):
    try:
        # Cargar clave desde settings
        stripe.api_key = settings.STRIPE_SECRET_KEY

        amount = request.data.get("amount")
        currency = request.data.get("currency", "usd")
        description = request.data.get("description", "Pago de servicio")

        intent = stripe.PaymentIntent.create(
            amount=int(amount),
            currency=currency,
            description=description,
            automatic_payment_methods={"enabled": True},
        )

        return Response({
            "clientSecret": intent.client_secret
        })

    except Exception as e:
        return Response({"error": str(e)}, status=400)


# Endpoint para Stripe Checkout
@api_view(["POST"])
def crear_checkout_session(request):
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        amount = int(request.data.get("amount"))
        currency = request.data.get("currency", "usd")
        description = request.data.get("description", "Pago de servicio")
        success_url = request.data.get("success_url", "http://localhost:3000/pago-exitoso")
        cancel_url = request.data.get("cancel_url", "http://localhost:3000/pago-cancelado")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": description},
                    "unit_amount": amount,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
        )
        return Response({"checkout_url": session.url})
    except Exception as e:
        return Response({"error": str(e)}, status=400)
