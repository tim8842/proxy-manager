import pytest

from api.admin import ProxyAdminForm
from api.models import Proxy


@pytest.mark.django_db
def test_proxy_admin_form_valid_url():
    """
    Test that ProxyAdminForm is valid with a unique URL.
    """
    form_data = {"url": "http://test:test@127.0.0.1:8080"}  # Replace with your needs
    form = ProxyAdminForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_proxy_admin_form_invalid_url_unique():
    """
    Test that ProxyAdminForm raises a ValidationError for a duplicate URL.
    """
    # Create a Proxy object with a specific URL
    Proxy.objects.create(url="http://test:test@127.0.0.1:8080")

    # Create a form with the same URL
    form_data = {"url": "http://test:test@127.0.0.1:8080"}
    form = ProxyAdminForm(data=form_data)

    # Validate the form
    assert not form.is_valid()
    print(form.errors)
    assert "Прокси с таким URL уже существует." in form.errors["url"][0]


@pytest.mark.django_db
def test_proxy_admin_form_valid_empty_url():
    """
    Test that ProxyAdminForm is valid with an empty URL.
    """
    form_data = {"url": None}
    form = ProxyAdminForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_proxy_admin_form_valid_none_url():
    """
    Test that ProxyAdminForm is valid with a None URL.
    """
    form_data = {"url": None}
    form = ProxyAdminForm(data=form_data)
    assert form.is_valid()
