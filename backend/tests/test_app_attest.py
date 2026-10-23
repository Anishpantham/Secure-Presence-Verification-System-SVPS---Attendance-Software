"""Synthetic certificate-chain tests, NOT Apple-provider or physical-device validation."""
import base64
import hashlib
from datetime import timedelta
from types import SimpleNamespace as Obj
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID, ObjectIdentifier
from app.models.entities import now
from app.services.app_attest import verify_attestation, AttestError
from test_cross_platform import encode


def certificate(subject, issuer, public_key, signing_key, ca, nonce=None):
    builder=x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(public_key).serial_number(x509.random_serial_number()).not_valid_before(now()-timedelta(days=1)).not_valid_after(now()+timedelta(days=2))
    builder=builder.add_extension(x509.BasicConstraints(ca=ca,path_length=1 if ca else None),critical=True)
    builder=builder.add_extension(x509.KeyUsage(digital_signature=not ca,key_encipherment=False,content_commitment=False,data_encipherment=False,key_agreement=False,key_cert_sign=ca,crl_sign=ca,encipher_only=False,decipher_only=False),critical=True)
    if nonce is not None:builder=builder.add_extension(x509.UnrecognizedExtension(ObjectIdentifier('1.2.840.113635.100.8.2'),b'\x30\x24\xa1\x22\x04\x20'+nonce),critical=False)
    return builder.sign(signing_key,hashes.SHA256())


@pytest.fixture
def synthetic_attestation(tmp_path):
    keys=[ec.generate_private_key(ec.SECP256R1()) for _ in range(3)]
    names=[x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,name)]) for name in ['TEST root','TEST intermediate','TEST leaf']]
    root=certificate(names[0],names[0],keys[0].public_key(),keys[0],True)
    intermediate=certificate(names[1],names[0],keys[1].public_key(),keys[0],True)
    root_file=tmp_path/'test-root.pem';root_file.write_bytes(root.public_bytes(serialization.Encoding.PEM))
    settings=Obj(apple_app_id='TEAM.edu.spvs.student',apple_attest_environment='development',apple_attest_root_pem=root_file,apple_attest_root_sha256=root.fingerprint(hashes.SHA256()).hex())
    key=keys[2].public_key();numbers=key.public_numbers();raw=key.public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)
    key_id=hashlib.sha256(raw).digest();client=b'server nonce, device id and key id'
    auth=hashlib.sha256(settings.apple_app_id.encode()).digest()+b'\x40'+bytes(4)+b'appattestdevelop'+b'\x00\x20'+key_id+encode({1:2,3:-7,-1:1,-2:numbers.x.to_bytes(32,'big'),-3:numbers.y.to_bytes(32,'big')})
    leaf=certificate(names[2],names[1],key,keys[1],False,hashlib.sha256(auth+hashlib.sha256(client).digest()).digest())
    obj={'fmt':'apple-appattest','authData':auth,'attStmt':{'x5c':[leaf.public_bytes(serialization.Encoding.DER),intermediate.public_bytes(serialization.Encoding.DER)],'receipt':b'test-only'}}
    token=base64.b64encode(encode(obj)).decode()
    return settings,token,base64.b64encode(key_id).decode(),client,key


def test_synthetic_valid_chain_nonce_and_key_binding(synthetic_attestation):
    settings,token,key_id,client,key=synthetic_attestation
    assert verify_attestation(token,key_id,client,settings)==key.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)


@pytest.mark.parametrize('mutation',['root','nonce','app','environment','key'])
def test_wrong_trust_or_binding_rejected(synthetic_attestation,mutation):
    settings,token,key_id,client,_=synthetic_attestation
    if mutation=='root':settings.apple_attest_root_sha256='0'*64
    if mutation=='nonce':client=b'wrong challenge'
    if mutation=='app':settings.apple_app_id='ATTACKER.edu.spvs.student'
    if mutation=='environment':settings.apple_attest_environment='production'
    if mutation=='key':key_id=base64.b64encode(bytes(32)).decode()
    with pytest.raises(AttestError):verify_attestation(token,key_id,client,settings)
