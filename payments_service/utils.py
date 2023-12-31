from rest_framework.request import Request
import stripe
from django.conf import settings
from rest_framework.reverse import reverse

from borrowing_service.models import Borrowing


stripe.api_key = settings.STRIPE_SECRET


def create_stripe_session(
    request: Request,
    borrowing: Borrowing,
    money_to_pay: float,
):
    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": int(money_to_pay * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=reverse("payments:payment-order-success", request=request)
        + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=reverse("payments:payment-order-cancel", request=request),
    )
    return session
