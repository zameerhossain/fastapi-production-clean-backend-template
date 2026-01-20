import logging
from threading import Lock
from typing import Optional


class _Logger:
    """
    Thread-safe Singleton Logger.
    Single instance across project.
    Supports dynamic log level changes.
    Prevents duplicate handlers.
    """

    _instance: Optional["_Logger"] = None
    _lock: Lock = Lock()

    def __new__(cls, name: str = "app") -> "_Logger":
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instance = instance
            return cls._instance

    def __init__(self, name: str = "app") -> None:
        # Prevent re-initialization in singleton
        if self._initialized:
            return

        self._initialized: bool = True
        self.logger: logging.Logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Prevent duplicate handlers
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
            handler.setFormatter(formatter)

            self.logger.addHandler(handler)
            self.logger.propagate = False

    def get_logger(self) -> logging.Logger:
        return self.logger

    def set_level(self, level: int) -> None:
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)


# ------------------------
# Single importable logger
# ------------------------

logger: logging.Logger = _Logger().get_logger()
