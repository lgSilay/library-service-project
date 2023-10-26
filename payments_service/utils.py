import stripe
from django.conf import settings

from borrowing_service.models import Borrowing
from payments_service.models import Payment


stripe.api_key = settings.STRIPE_SECRET


def create_stripe_session(
    borrowing: Borrowing, money_to_pay: float, type="payment"
) -> str:
    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": money_to_pay * 100,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:8080/api/payments/payment/success",
        cancel_url="http://localhost:8080/api/payments/payments/cancel",
    )
    Payment.objects.create(
        type=type,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=money_to_pay,
    )
    return session.url
