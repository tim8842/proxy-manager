from django.utils import timezone

from api.models import Proxy, User
from logger import logger


def delete_expired_proxies():
    now = timezone.now()
    expired_proxies = Proxy.objects.filter(expire_at__lte=now)
    count = expired_proxies.count()
    expired_proxies.delete()
    logger.info(f"Удалено {count} прокси, у которых истек срок действия.")


def update_user_statuses():
    now = timezone.now()
    one_minute_ago = now - timezone.timedelta(minutes=1)
    users_to_update = User.objects.filter(updated_at__lte=one_minute_ago, status=429)
    count = users_to_update.count()
    users_to_update.update(status=200)
    logger.info(f"Обновлено {count} статусов пользователей на '200'.")
