import base64
import hashlib

import ecdsa
import requests
from django.conf import settings


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
            "basketOrder": order.get_mono_basket_info(),
        },
        "webHookUrl": webhook_url,
    }
    r = requests.post(
        "https://api.monobank.ua/api/merchant/invoice/create",
        headers={"X-Token": settings.MONOBANK_API_KEY},
        json=body,
    )
    r.raise_for_status()
    order.invoice_id = r.json()["invoiceId"]
    order.save()
    url = r.json()["pageUrl"]

    return {"order_id": order.id, "pageUrl": url}


def get_mono_token():
    key = requests.get(
        "https://api.monobank.ua/api/merchant/pubkey",
        headers={"X-Token": settings.MONOBANK_API_KEY},
    ).json()["key"]
    return key
