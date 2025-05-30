from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models

from logger import logger

ENCRYPTED_PREFIX = "enc:"


class EncryptedCharField(models.CharField):
    """
    Кастомное поле, которое автоматически шифрует и дешифрует значения,
    с защитой от повторного шифрования и безопасной дешифровкой.
    """

    def get_cipher(self):
        """
        Создаёт объект Fernet на лету.
        """
        return Fernet(settings.CRYPTOGRAPHY_KEY.encode())

    def get_prep_value(self, value):
        """
        Шифрует значение перед сохранением в базу данных.
        """
        value = super().get_prep_value(value)

        if value is None:
            return value

        if isinstance(value, str) and not value.startswith(ENCRYPTED_PREFIX):
            try:
                cipher = self.get_cipher()
                encrypted = cipher.encrypt(value.encode()).decode()
                return f"{ENCRYPTED_PREFIX}{encrypted}"
            except Exception as e:
                logger.error(f"Encryption error in get_prep_value: {e}")
                raise e

        return value

    def from_db_value(self, value, expression, connection):
        """
        Дешифрует значение при извлечении из базы данных.
        """
        if value is None or not isinstance(value, str):
            return value

        if value.startswith(ENCRYPTED_PREFIX):
            encrypted_part = value[len(ENCRYPTED_PREFIX) :]
            try:
                cipher = self.get_cipher()
                return cipher.decrypt(encrypted_part.encode()).decode()
            except InvalidToken:
                logger.error("Invalid token during decryption in from_db_value")
                return "(Decryption Error)"
            except Exception as e:
                logger.error(f"Decryption error in from_db_value: {e}")
                return "(Decryption Error)"
        return value  # Уже дешифровано или незашифровано

    def to_python(self, value):
        """
        Дешифрует значение при использовании в коде Python.
        """
        if value is None or not isinstance(value, str):
            return value

        if value.startswith(ENCRYPTED_PREFIX):
            encrypted_part = value[len(ENCRYPTED_PREFIX) :]
            try:
                cipher = self.get_cipher()
                return cipher.decrypt(encrypted_part.encode()).decode()
            except InvalidToken:
                logger.error("Invalid token during decryption in to_python")
                return "(Decryption Error)"
            except Exception as e:
                logger.error(f"Decryption error in to_python: {e}")
                return "(Decryption Error)"
        return value  # Уже расшифровано или это обычное значение
