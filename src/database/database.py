import asyncio
import threading
import time
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Callable, Generator, Optional, cast

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.logger.logger import logger

Base = declarative_base()


class Database:
    """
    Production-grade Database manager with:
    - Sync/async session detection from URI
    - Multi-DB support
    - Lazy engine/session creation
    - Context-managed sessions with auto commit/rollback
    - Connection pooling with automatic recycling and idle timeout
    - Query-level statement timeout
    - Retry logic for transient DB failures
    - Health check method
    """

    _lock = threading.Lock()
    _sync_engines: dict[str, create_engine] = {}
    _async_engines: dict[str, AsyncEngine] = {}
    _SyncSessions: dict[str, sessionmaker[Session]] = {}
    _AsyncSessions: dict[str, sessionmaker[AsyncSession]] = {}

    DEFAULT_POOL_SIZE = 5
    DEFAULT_MAX_OVERFLOW = 10
    DEFAULT_POOL_TIMEOUT = 30  # seconds
    DEFAULT_POOL_RECYCLE = 1800  # recycle connections every 30 minutes
    DEFAULT_STATEMENT_TIMEOUT = 30  # seconds per query
    RETRY_COUNT = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self, uri: str, engine_kwargs: Optional[dict] = None):
        self.uri = uri
        self.engine_kwargs = engine_kwargs or {}
        self._engine: Optional[create_engine | AsyncEngine] = None
        self._sessionmaker: Optional[sessionmaker] = None

    # -----------------------------
    # Internal: detect sync/async from URI
    # -----------------------------
    @property
    def _is_async(self) -> bool:
        return self.uri.startswith("postgresql+asyncpg") or self.uri.startswith(
            "mysql+asyncmy"
        )

    # -----------------------------
    # Sync session property
    # -----------------------------
    @property
    def get_sync(self) -> Callable[[], Generator[Session, None, None]]:
        if self._is_async:
            raise RuntimeError("URI requires async engine. Use get_async instead.")

        def _ensure_engine():
            with self._lock:
                if self.uri not in self._sync_engines:
                    defaults = {
                        "pool_size": self.DEFAULT_POOL_SIZE,
                        "max_overflow": self.DEFAULT_MAX_OVERFLOW,
                        "pool_timeout": self.DEFAULT_POOL_TIMEOUT,
                        "pool_recycle": self.DEFAULT_POOL_RECYCLE,
                        "echo": False,
                    }
                    defaults.update(self.engine_kwargs)
                    engine = create_engine(self.uri, future=True, **defaults)
                    self._sync_engines[self.uri] = engine
                    self._SyncSessions[self.uri] = sessionmaker(
                        bind=engine, expire_on_commit=False
                    )
                self._engine = self._sync_engines[self.uri]
                self._sessionmaker = self._SyncSessions[self.uri]

        _ensure_engine()

        @contextmanager
        def _session() -> Generator[Session, None, None]:
            attempt = 0
            while attempt < self.RETRY_COUNT:
                session: Session = self._sessionmaker()
                try:
                    session.execute(
                        text(
                            f"SET statement_timeout = {self.DEFAULT_STATEMENT_TIMEOUT * 1000}"
                        )
                    )
                    yield session
                    session.commit()
                    break
                except OperationalError as e:
                    session.rollback()
                    attempt += 1
                    logger.warning(
                        f"DB OperationalError, retry {attempt}/{self.RETRY_COUNT}: {e}"
                    )
                    time.sleep(self.RETRY_DELAY)
                    if attempt >= self.RETRY_COUNT:
                        raise
                except Exception:
                    session.rollback()
                    raise
                finally:
                    session.close()

        return _session

    # -----------------------------
    # Async session property
    # -----------------------------
    @property
    def get_async(self) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
        if not self._is_async:
            raise RuntimeError("URI does not support async. Use get_sync instead.")

        def _ensure_engine():
            with self._lock:
                if self.uri not in self._async_engines:
                    defaults = {
                        "pool_size": self.DEFAULT_POOL_SIZE,
                        "max_overflow": self.DEFAULT_MAX_OVERFLOW,
                        "pool_timeout": self.DEFAULT_POOL_TIMEOUT,
                        "pool_recycle": self.DEFAULT_POOL_RECYCLE,
                        "echo": False,
                    }
                    defaults.update(self.engine_kwargs)
                    engine = create_async_engine(self.uri, future=True, **defaults)
                    self._async_engines[self.uri] = engine
                    self._AsyncSessions[self.uri] = cast(
                        sessionmaker[AsyncSession],
                        sessionmaker(
                            bind=engine, class_=AsyncSession, expire_on_commit=False
                        ),
                    )
                self._engine = self._async_engines[self.uri]
                self._sessionmaker = self._AsyncSessions[self.uri]

        _ensure_engine()

        @asynccontextmanager
        async def _session() -> AsyncGenerator[AsyncSession, None]:
            attempt = 0
            while attempt < self.RETRY_COUNT:
                async with self._sessionmaker() as session:
                    try:
                        await session.execute(
                            text(
                                f"SET statement_timeout = {self.DEFAULT_STATEMENT_TIMEOUT * 1000}"
                            )
                        )
                        yield session
                        await session.commit()
                        break
                    except OperationalError as e:
                        await session.rollback()
                        attempt += 1
                        logger.warning(
                            f"Async DB OperationalError, retry {attempt}/{self.RETRY_COUNT}: {e}"
                        )
                        await asyncio.sleep(self.RETRY_DELAY)
                        if attempt >= self.RETRY_COUNT:
                            raise
                    except Exception:
                        await session.rollback()
                        raise

        return _session

    # -----------------------------
    # Optional: create tables (sync only)
    # -----------------------------
    def create_tables(self) -> None:
        if self._is_async:
            raise RuntimeError("Cannot create tables in async mode")
        Base.metadata.create_all(self._engine)

    # -----------------------------
    # Optional: drop tables (sync only)
    # -----------------------------
    def drop_tables(self) -> None:
        if self._is_async:
            raise RuntimeError("Cannot drop tables in async mode")
        Base.metadata.drop_all(self._engine)

    # -----------------------------
    # Health check
    # -----------------------------
    def health_check(self) -> bool:
        try:
            if self._is_async:
                raise RuntimeError("Use async health check for async engine")
            with self.get_sync() as session:
                session.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def health_check_async(self) -> bool:
        if not self._is_async:
            raise RuntimeError("Use sync health check for sync engine")
        try:
            async with self.get_async() as session:
                await session.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            logger.error(f"Async health check failed: {e}")
            return False
