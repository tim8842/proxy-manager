import base64
import getpass
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv, set_key


def generate_key(password: str) -> str:
    password = password.encode()
    salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key.decode()


password = getpass.getpass("Enter password to generate key: ")
key = generate_key(password)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path)

set_key(dotenv_path, "CRYPTOGRAPHY_KEY", key)

print("Key generated and saved to .env file!")
