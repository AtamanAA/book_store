import base64
import hashlib

import ecdsa
import requests
from django.conf import settings

from book.models import Book
from .models import OrderItem


def verify_signature(pub_key_base64, x_sign_base64, body_bytes):
    try:
        pub_key_bytes = base64.b64decode(pub_key_base64)
        signature_bytes = base64.b64decode(x_sign_base64)
        pub_key = ecdsa.VerifyingKey.from_pem(pub_key_bytes.decode())
        check = pub_key.verify(
            signature_bytes,
            body_bytes,
            sigdecode=ecdsa.util.sigdecode_der,
            hashfunc=hashlib.sha256,
        )
    except Exception:
        return False
    if check:
        return True
    else:
        return False


def create_mono_order(order, webhook_url):
    body = {
        "amount": order.full_price,
        "merchantPaymInfo": {
            "reference": str(order.id),
            "basketOrder": fill_mono_basket(order.id),
        },
        "webHookUrl": webhook_url,
    }
    r = requests.post(
        "https://api.monobank.ua/api/merchant/invoice/create",
        headers={"X-Token": settings.MONOBANK_API_KEY},
        json=body,
    )
    r.raise_for_status()
    url = r.json()["pageUrl"]
    order.pay_url = url
    order.invoice_id = r.json()["invoiceId"]
    order.save()
    return {"order_id": order.id, "pageUrl": url}


def fill_mono_basket(order_id):
    basket = []
    for item in OrderItem.objects.filter(order_id=order_id):
        book = Book.objects.get(pk=item.book_id)
        basket.append(
            {
                "name": book.name,
                "qty": item.quantity,
                "sum": book.price * item.quantity,
                "unit": "шт.",
            }
        )
    return basket


def get_mono_token():
    key = requests.get(
        "https://api.monobank.ua/api/merchant/pubkey",
        headers={"X-Token": settings.MONOBANK_API_KEY},
    ).json()["key"]
    return key
