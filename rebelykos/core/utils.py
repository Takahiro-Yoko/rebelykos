from base64 import b64decode
from termcolor import colored
import datetime
import logging
import netifaces
import os
import random
import string
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes

import rebelykos

class CmdError(Exception):
    def __init__(self, msg):
        logging.error(msg)
        super().__init__(msg)

def gen_random_string(length: int = 10):
    return "".join([random.choice(string.ascii_letters + string.digits)
                    for _ in range(length)])

def get_data_folder():
    return os.path.expanduser("~/.rl")

def get_path_in_data_folder(path):
    return os.path.join(get_data_folder(), path.lstrip("/"))

def get_path_in_package(path):
    return os.path.join(os.path.dirname(rebelykos.__file__), path.lstrip("/"))

def decode_auth_header(req_headers):
    auth_header = req_headers["Authorization"]
    auth_header = b64decode(auth_header)
    username, password_digest = auth_header.decode().split(":")
    return username, password_digest

def get_ips():
    ips = []
    for iface in netifaces.interfaces():
        try:
            netif = netifaces.ifaddresses(iface)
            if netif[netifaces.AF_INET][0]["addr"] == "127.0.0.1":
                continue
            ips.append(netif[netifaces.AF_INET][0]["addr"])
        except (ValueError, KeyError):
            continue

    return ips

def create_self_signed_cert(
    key_file: str = get_path_in_data_folder("key.pem"),
    cert_file: str = get_path_in_data_folder("cert.pem"),
    chain_file: str = get_path_in_data_folder("chain.pem")):
    logging.info("Creating self-signed certificate")
    key = rsa.generate_private_key(public_exponent=65537,
                                   key_size=4096,
                                   backend=default_backend())
    with open(chain_file, "wb") as ch:
        with open(key_file, "wb") as k:
            privkey_bytes = key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            ch.write(privkey_bytes)
            k.write(privkey_bytes)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"JP"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Tokyo"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Shibuya"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"rebelykos"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"rebelykos.com")
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=9999)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
        critical=False
    ).sign(key, hashes.SHA256(), default_backend())

    with open(chain_file, "ab") as ch:
        with open(cert_file, "wb") as crt:
            pubkey_bytes = cert.public_bytes(serialization.Encoding.PEM)
            ch.write(pubkey_bytes)
            crt.write(pubkey_bytes)

    logging.info(f"Self-signed certificate written to {key_file}, {cert_file}"
                 f" and {chain_file}")

def print_good(msg):
    print(f"{colored('[+]', 'green')} {msg}")

def print_bad(msg):
    print(f"{colored('[-]', 'red')} {msg}")

def print_info(msg):
    print(f"{colored('[*]', 'blue')} {msg}")
