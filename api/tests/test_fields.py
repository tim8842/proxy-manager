import pytest
from cryptography.fernet import Fernet
from django.conf import settings

from api.fields import ENCRYPTED_PREFIX, EncryptedCharField


@pytest.fixture
def encrypted_char_field():
    """
    Fixture to create an instance of EncryptedCharField for testing.
    """
    return EncryptedCharField(max_length=255)


@pytest.mark.django_db
def test_encrypted_char_field_encryption(encrypted_char_field):
    """
    Test that the field encrypts values correctly before saving to the database.
    """
    plain_text = "Sensitive data"
    encrypted_value = encrypted_char_field.get_prep_value(plain_text)
    assert encrypted_value.startswith(ENCRYPTED_PREFIX)
    # Try to decrypt it back to verify (without touching database)
    cipher = Fernet(settings.CRYPTOGRAPHY_KEY.encode())
    decrypted_text = cipher.decrypt(encrypted_value[len(ENCRYPTED_PREFIX) :].encode()).decode()
    assert decrypted_text == plain_text


@pytest.mark.django_db
def test_encrypted_char_field_decryption_from_db(encrypted_char_field):
    """
    Test that the field decrypts values correctly when retrieving from the database.
    """
    plain_text = "Secret message"
    encrypted_value = encrypted_char_field.get_prep_value(plain_text)
    decrypted_value = encrypted_char_field.from_db_value(
        encrypted_value, None, None
    )  # expression and connection aren't important in that case
    assert decrypted_value == plain_text


@pytest.mark.django_db
def test_encrypted_char_field_decryption_to_python(encrypted_char_field):
    """
    Test that the field decrypts values correctly in to_python method.
    """
    plain_text = "Private information"
    encrypted_value = encrypted_char_field.get_prep_value(plain_text)
    decrypted_value = encrypted_char_field.to_python(encrypted_value)
    assert decrypted_value == plain_text


@pytest.mark.django_db
def test_encrypted_char_field_none_value(encrypted_char_field):
    """
    Test that the field handles None values correctly.
    """
    assert encrypted_char_field.get_prep_value(None) is None
    assert encrypted_char_field.from_db_value(None, None, None) is None
    assert encrypted_char_field.to_python(None) is None


@pytest.mark.django_db
def test_encrypted_char_field_invalid_token(encrypted_char_field):
    """
    Test that the field handles InvalidToken during decryption.
    """
    invalid_encrypted_value = "enc:invalid_token"
    decrypted_value_from_db = encrypted_char_field.from_db_value(invalid_encrypted_value, None, None)
    assert decrypted_value_from_db == "(Decryption Error)"
    decrypted_value_to_python = encrypted_char_field.to_python(invalid_encrypted_value)
    assert decrypted_value_to_python == "(Decryption Error)"


@pytest.mark.django_db
def test_encrypted_char_field_encryption_failure(encrypted_char_field, monkeypatch):
    """
    Test that the field handles encryption failures gracefully.
    """

    class FakeCipher:
        def encrypt(self, value):
            raise Exception("Encryption failed")

    monkeypatch.setattr(encrypted_char_field, "get_cipher", lambda: FakeCipher())

    with pytest.raises(Exception, match="Encryption failed"):
        encrypted_char_field.get_prep_value("test")


@pytest.mark.django_db
def test_encrypted_char_field_incorrect_key(encrypted_char_field, monkeypatch):
    """
    Test that the field raises an error if settings.CRYPTOGRAPHY_KEY is not defined.
    """
    monkeypatch.delattr(settings, "CRYPTOGRAPHY_KEY", raising=True)
    with pytest.raises(AttributeError):
        encrypted_char_field.get_cipher()
