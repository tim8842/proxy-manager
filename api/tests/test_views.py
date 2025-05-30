import pytest
from django.urls import reverse
from django.utils import timezone

from api.models import Proxy, User, UserAgent
from api.serializers import UserSerializer

# Create your tests here.


def add_base_user_agents():
    ua1 = UserAgent.objects.create(
        agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        + " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    ua2 = UserAgent.objects.create(
        agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15"
        + " (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
    )
    return (ua1, ua2)


def add_base_proxy():
    p1 = Proxy.objects.create(url=None, expire_at=None)
    p2 = Proxy.objects.create(url="https://192121@pass@login", expire_at=timezone.now())
    return (p1, p2)


@pytest.fixture
def users():
    ua = add_base_user_agents()
    p = add_base_proxy()
    uo = []
    for ui in ua:
        for pi in p:
            uo.append(
                UserSerializer(
                    User.objects.create(user_agent=ui, proxy=pi, status=200)
                ).data
            )
    return uo


@pytest.mark.django_db
def test_get_random_user(client, users):
    uo = users
    url = reverse("random-user")
    response = client.get(url)
    assert response.status_code == 200
    assert response["content-type"] == "application/json"
    data = response.json()
    assert data in uo


@pytest.mark.django_db
def test_get_empty_random_user(client):
    url = reverse("random-user")
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_update_status(client, users):
    uo = users
    user = uo[0]
    url = reverse("user-status-update", args=[user["id"]])
    response = client.patch(url, {"status": 409}, content_type="application/json")
    assert response.status_code == 200
    assert response["content-type"] == "application/json"
    data = response.json()
    assert data["status"] == 409


@pytest.mark.django_db
def test_update_bad_id_status(client):
    url = reverse("user-status-update", args=[12])
    response = client.patch(url, {"status": 409}, content_type="application/json")
    assert response.status_code == 404
