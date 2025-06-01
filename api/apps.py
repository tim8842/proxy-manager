import atexit
import os
import signal

import psutil
from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from django.conf import settings

from logger import logger


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        if settings.TESTING:
            return
        if settings.SCHEDULER_AUTOSTART:  # Включаем автозапуск в settings.py
            self.scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)

            from .tasks import delete_expired_proxies, update_user_statuses

            self.scheduler.add_job(delete_expired_proxies, "cron", id="delete_expired_proxies", hour="*")

            self.scheduler.add_job(
                update_user_statuses,
                "interval",
                id="update_user_statuses",
                minutes=1,
            )

            self.scheduler.start()
            logger.info("Scheduler start")

            def shutdown_scheduler():
                if self.scheduler is not None and self.scheduler.running:
                    logger.info("Stopping scheduler...")
                    self.scheduler.shutdown(wait=False)

                    logger.info("Scheduler stopped.")
                else:
                    logger.info("Scheduler was not started, skipping shutdown.")

            def signal_handler(signum, frame):
                logger.info("Received signal, shutting down...")
                shutdown_scheduler()
                parent_pid = os.getpid()
                parent = psutil.Process(parent_pid)
                for child in parent.children(recursive=True):  # может быть больше одного потомка
                    child.kill()
                parent.kill()  # убиваем основной процесс

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            atexit.register(shutdown_scheduler)
