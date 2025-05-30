import pytest
from django.db import IntegrityError
from django.utils import timezone

from api.models import Proxy, User, UserAgent, hash_url


@pytest.mark.django_db
def test_proxy_creation():
    """
    Test that a Proxy object can be created successfully.
    """
    proxy = Proxy.objects.create(url="http://user:pass@host:port")
    assert proxy.url == "http://user:pass@host:port"
    assert proxy.url_hash == hash_url("http://user:pass@host:port")
    assert str(proxy) == "http://user:pass@host:port"  # Test __str__ method


@pytest.mark.django_db
def test_proxy_url_hash_uniqueness():
    """
    Test that Proxy objects with the same URL hash cannot be created.
    """
    Proxy.objects.create(url="http://user:pass@host:port")
    with pytest.raises(IntegrityError):
        Proxy.objects.create(url="http://user:pass@host:port")


@pytest.mark.django_db
def test_proxy_blank_url():
    """
    Test that a Proxy object can be created with a blank URL.
    """
    proxy = Proxy.objects.create(url=None)  # Allow blank=True/null=True
    assert proxy.url is None
    assert proxy.url_hash == ""  # or None, depending on what hash_url does with None
    assert str(proxy) == "(No URL)"  # Test __str__


@pytest.mark.django_db
def test_user_agent_creation():
    """
    Test that a UserAgent object can be created successfully.
    """
    user_agent = UserAgent.objects.create(
        agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        + " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    assert (
        user_agent.agent
        == "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        + " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    assert str(user_agent) == user_agent.agent  # Test __str__


@pytest.mark.django_db
def test_user_creation(base_user_agents, base_proxy):
    """
    Test that a User object can be created successfully.
    """
    user_agent1, user_agent2 = base_user_agents
    proxy1, proxy2 = base_proxy

    user = User.objects.create(user_agent=user_agent1, proxy=proxy1, status=200)
    assert user.user_agent == user_agent1
    assert user.proxy == proxy1
    assert user.status == 200
    assert "User:" in str(user)  # Test __str__ method


@pytest.mark.django_db
def test_unique_together_user(base_user_agents, base_proxy):
    """
    Test that unique_together constraint on User model works.
    """
    user_agent1, user_agent2 = base_user_agents
    proxy1, proxy2 = base_proxy

    User.objects.create(user_agent=user_agent1, proxy=proxy1, status=200)
    with pytest.raises(IntegrityError):
        User.objects.create(user_agent=user_agent1, proxy=proxy1, status=300)


@pytest.fixture
def base_user_agents():
    ua1 = UserAgent.objects.create(
        agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        + " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    ua2 = UserAgent.objects.create(
        agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15"
        + " (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
    )
    return ua1, ua2


@pytest.fixture
def base_proxy():
    p1 = Proxy.objects.create(url=None, expire_at=None)
    p2 = Proxy.objects.create(url="https://192121@pass@login", expire_at=timezone.now())
    return p1, p2
