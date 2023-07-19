import base64
import hashlib

import ecdsa
import requests
from django.conf import settings

from order.models import Order, OrderItem


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
