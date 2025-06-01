import hashlib

from django.db import models

from .fields import EncryptedCharField


def hash_url(url: str) -> str:
    if url:
        return hashlib.sha256(url.encode()).hexdigest()
    else:
        return None


class Proxy(models.Model):
    """
    Модель для хранения информации о прокси-сервере.
    """

    url = EncryptedCharField(
        max_length=255,
        unique=True,
        help_text="URL прокси-сервера (e.g., http://user:pass@host:port)",
        null=True,
        blank=True,
    )
    url_hash = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        help_text="SHA-256 хеш URL для уникальности",
    )
    expire_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Дата и время истечения срока действия прокси (опционально)",
    )

    def save(self, *args, **kwargs):
        if self.url:
            self.url_hash = hash_url(self.url)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.url:
            return self.url
        else:
            return "(No URL)"


class UserAgent(models.Model):
    """
    Модель для хранения информации о User-Agent.
    """

    agent = models.TextField(unique=True, help_text="Строка User-Agent")

    def __str__(self):
        return self.agent


class User(models.Model):
    """
    Модель для связи прокси и User-Agent.  Также фиксирует статус использования.
    """

    user_agent = models.ForeignKey(
        UserAgent,
        on_delete=models.CASCADE,
        related_name="users",
        help_text="User-Agent, используемый для запросов",
    )
    proxy = models.ForeignKey(
        Proxy,
        on_delete=models.CASCADE,
        related_name="users",
        help_text="Прокси-сервер, используемый для запросов",
    )
    status = models.IntegerField(default=200, help_text="Статус использования прокси и User-agent")
    updated_at = models.DateTimeField(auto_now=True, help_text="Дата и время последнего обновления записи")

    class Meta:
        unique_together = ("user_agent", "proxy")

    def __str__(self):
        return f"User: {self.user_agent.agent[:20]}... | Proxy: {self.proxy.url}"
