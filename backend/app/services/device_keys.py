"""P-256 proof of possession; only public keys cross the native bridge/network."""
import base64
import hashlib
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


def decode_public_key(value):
    raw = base64.b64decode(value, validate=True)
    key = serialization.load_der_public_key(raw)
    if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(key.curve, ec.SECP256R1):
        raise ValueError('P256_KEY_REQUIRED')
    if raw != key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo):
        raise ValueError('CANONICAL_SPKI_REQUIRED')
    return key


def verify_signature(public_key, signature, message):
    try:
        key = decode_public_key(public_key)
        key.verify(base64.b64decode(signature, validate=True), message.encode(), ec.ECDSA(hashes.SHA256()))
        return True
    except (ValueError, TypeError, InvalidSignature):
        return False


def registration_message(nonce, platform, public_key):
    decode_public_key(public_key)
    fingerprint = hashlib.sha256(base64.b64decode(public_key, validate=True)).hexdigest()
    return f'SPVS-REGISTER-v1.{nonce}.{platform}.{fingerprint}'
