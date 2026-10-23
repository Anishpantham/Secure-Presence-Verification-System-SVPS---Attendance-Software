"""Apple App Attest verifier. No trust roots or app identity are accepted from clients.

CBOR uses a bounded definite-length decoder for the small App Attest/COSE subset.
Production rollout still requires Apple configuration and real-device validation.
"""
import base64
import hashlib
import hmac
import io
from datetime import datetime, timezone
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ObjectIdentifier


class AttestError(ValueError):
    pass


def cbor(raw):
    if len(raw) > 24000:
        raise AttestError('CBOR_TOO_LARGE')
    stream = io.BytesIO(raw)
    def take(n):
        value = stream.read(n)
        if len(value) != n:
            raise AttestError('CBOR_TRUNCATED')
        return value
    def read(depth=0):
        if depth > 8:
            raise AttestError('CBOR_DEPTH')
        head = take(1)[0]; major, additional = head >> 5, head & 31
        if additional < 24:
            size = additional
        elif additional in (24, 25, 26, 27):
            size = int.from_bytes(take(1 << (additional - 24)), 'big')
        else:
            raise AttestError('CBOR_INDEFINITE_OR_RESERVED')
        if major == 0: return size
        if major == 1: return -1-size
        if size > 24000: raise AttestError('CBOR_SIZE')
        if major == 2: return take(size)
        if major == 3: return take(size).decode('utf-8')
        if major == 4: return [read(depth+1) for _ in range(size)]
        if major == 5:
            result = {}
            for _ in range(size):
                key = read(depth+1)
                if not isinstance(key, (str, int, bytes)) or key in result:
                    raise AttestError('CBOR_MAP_KEY')
                result[key] = read(depth+1)
            return result
        raise AttestError('CBOR_TYPE')
    value = read()
    if stream.read(1): raise AttestError('CBOR_TRAILING_DATA')
    return value


def configured(settings):
    return bool(settings.apple_app_id and settings.apple_attest_root_pem and settings.apple_attest_root_sha256
                and settings.apple_attest_environment in ('production', 'development'))


def app_hash(settings):
    if not configured(settings): raise AttestError('APP_ATTEST_NOT_CONFIGURED')
    return hashlib.sha256(settings.apple_app_id.encode()).digest()


def verify_chain(chain, settings):
    if not isinstance(chain, list) or len(chain) != 2:
        raise AttestError('APP_ATTEST_CERTIFICATE_CHAIN')
    root = x509.load_pem_x509_certificate(settings.apple_attest_root_pem.read_bytes())
    if not hmac.compare_digest(root.fingerprint(hashes.SHA256()).hex(), settings.apple_attest_root_sha256.lower().replace(':','')):
        raise AttestError('APP_ATTEST_ROOT_PIN')
    certs = [x509.load_der_x509_certificate(value) for value in chain] + [root]
    current = datetime.now(timezone.utc)
    for index, cert in enumerate(certs):
        if not cert.not_valid_before_utc <= current <= cert.not_valid_after_utc:
            raise AttestError('APP_ATTEST_CERTIFICATE_EXPIRED')
        constraints = cert.extensions.get_extension_for_class(x509.BasicConstraints).value
        if constraints.ca != (index > 0): raise AttestError('APP_ATTEST_CA_CONSTRAINT')
        if index > 0:
            if constraints.path_length is not None and constraints.path_length < index-1:
                raise AttestError('APP_ATTEST_PATH_LENGTH')
            if not cert.extensions.get_extension_for_class(x509.KeyUsage).value.key_cert_sign:
                raise AttestError('APP_ATTEST_KEY_USAGE')
        elif not cert.extensions.get_extension_for_class(x509.KeyUsage).value.digital_signature:
            raise AttestError('APP_ATTEST_KEY_USAGE')
        # Unknown critical extensions must not be silently trusted.
        for extension in cert.extensions:
            if extension.critical and extension.oid not in (x509.ExtensionOID.BASIC_CONSTRAINTS, x509.ExtensionOID.KEY_USAGE):
                raise AttestError('APP_ATTEST_CRITICAL_EXTENSION')
        cert.verify_directly_issued_by(certs[min(index+1, len(certs)-1)])
    key = certs[0].public_key()
    if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(key.curve, ec.SECP256R1):
        raise AttestError('APP_ATTEST_KEY_TYPE')
    return certs[0], key


def verify_attestation(encoded, key_id, client_data, settings):
    rp = app_hash(settings)
    obj = cbor(base64.b64decode(encoded, validate=True))
    if not isinstance(obj, dict) or not isinstance(obj.get('attStmt'), dict): raise AttestError('APP_ATTEST_OBJECT')
    if obj['fmt'] != 'apple-appattest': raise AttestError('APP_ATTEST_FORMAT')
    auth = obj['authData']
    if not isinstance(auth, bytes) or len(auth) < 87: raise AttestError('APP_ATTEST_AUTH_DATA')
    leaf, key = verify_chain(obj['attStmt']['x5c'], settings)
    expected_nonce = hashlib.sha256(auth + hashlib.sha256(client_data).digest()).digest()
    extension = leaf.extensions.get_extension_for_oid(ObjectIdentifier('1.2.840.113635.100.8.2')).value.value
    if not hmac.compare_digest(extension, b'\x30\x24\xa1\x22\x04\x20' + expected_nonce):
        raise AttestError('APP_ATTEST_NONCE')
    if not hmac.compare_digest(auth[:32], rp) or auth[32] not in (0x40, 0x41) or auth[33:37] != bytes(4):
        raise AttestError('APP_ATTEST_RP_FLAGS_COUNTER')
    aaguid = b'appattest' + bytes(7) if settings.apple_attest_environment == 'production' else b'appattestdevelop'
    # Production AAGUID is 16 bytes: "appattest" (9 bytes) + seven NULs.
    if auth[37:53] != aaguid: raise AttestError('APP_ATTEST_ENVIRONMENT')
    length = int.from_bytes(auth[53:55], 'big')
    identifier = base64.b64decode(key_id, validate=True)
    raw_key = key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    if length != 32 or not hmac.compare_digest(identifier, hashlib.sha256(raw_key).digest()) or auth[55:87] != identifier:
        raise AttestError('APP_ATTEST_KEY_ID')
    cose = cbor(auth[87:])
    numbers = key.public_numbers()
    if not isinstance(cose, dict): raise AttestError('APP_ATTEST_COSE_KEY')
    if cose.get(1) != 2 or cose.get(3) != -7 or cose.get(-1) != 1 or cose.get(-2) != numbers.x.to_bytes(32,'big') or cose.get(-3) != numbers.y.to_bytes(32,'big'):
        raise AttestError('APP_ATTEST_COSE_KEY')
    return key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)


def verify_assertion(encoded, client_data, key_der, previous_counter, settings):
    rp = app_hash(settings)
    obj = cbor(base64.b64decode(encoded, validate=True))
    if not isinstance(obj, dict) or not isinstance(obj.get('authenticatorData'), bytes) or not isinstance(obj.get('signature'), bytes): raise AttestError('APP_ATTEST_ASSERTION_OBJECT')
    auth = obj['authenticatorData']
    if len(auth) != 37 or not hmac.compare_digest(auth[:32], rp) or auth[32] not in (0, 1):
        raise AttestError('APP_ATTEST_ASSERTION_DATA')
    counter = int.from_bytes(auth[33:37], 'big')
    if counter <= previous_counter: raise AttestError('APP_ATTEST_COUNTER_REPLAY')
    key = serialization.load_der_public_key(key_der)
    if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(key.curve, ec.SECP256R1):
        raise AttestError('APP_ATTEST_KEY_TYPE')
    key.verify(obj['signature'], auth + hashlib.sha256(client_data).digest(), ec.ECDSA(hashes.SHA256()))
    return counter
