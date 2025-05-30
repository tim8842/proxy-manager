import logging
import logging.handlers
import os

# Определяем уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = logging.INFO  # Можно изменить на другой уровень

# Создаем логгер
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# Создаем форматтер
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Создаем обработчик (handler) для записи в файл с ротацией по времени
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "app.log")
# Ротация каждый день, хранить 7 файлов
rotating_file_handler = logging.handlers.TimedRotatingFileHandler(
    log_file,
    when="D",  # "D" - каждый день, "W" - каждую неделю, "M" - каждый месяц и т.д.
    interval=1,  # Интервал ротации (1 - каждый день)
    backupCount=7,  # Хранить 7 последних файлов
)
rotating_file_handler.setFormatter(formatter)

# Создаем обработчик (handler) для вывода в консоль
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(rotating_file_handler)
logger.addHandler(stream_handler)

# Пример использования
if __name__ == "__main__":
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
