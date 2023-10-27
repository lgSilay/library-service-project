from rest_framework.request import Request
import stripe
from django.conf import settings
from rest_framework.reverse import reverse

from borrowing_service.models import Borrowing
from payments_service.models import Payment


stripe.api_key = settings.STRIPE_SECRET


def create_stripe_session(
    request: Request,
    borrowing: Borrowing,
    money_to_pay: float,
    type="payment",
) -> str:
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
    Payment.objects.create(
        type=type,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=money_to_pay,
    )
    return session.url
