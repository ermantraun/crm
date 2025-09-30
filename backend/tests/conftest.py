import asyncio
import os
import uuid
from pathlib import Path
from typing import AsyncIterator

import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text
from alembic.config import Config as AlembicConfig
from alembic import command
from fastapi import FastAPI, Request
from httpx import AsyncClient
from dishka import Provider, provide, Scope, make_async_container
from dishka.integrations.fastapi import setup_dishka, DishkaRoute

from config import PostgresConfig, Config, FastApiConfig, RabbitMqConfig
from application.lead.interactors import (
    CreateLeadInteractor,
    GetLeadInteractor,
)
from application.lead import interfaces
from infrastructure.db.repositories import (
    LeadRepository,
    KeysRepository,
)
from infrastructure.db import models
from application.common_interfaces import DBSession
from handlers.api.v1 import leads as leads_router

# --- Тестовый брокер (stub) ---
class TestMessageBroker(interfaces.MessageBroker):
    def __init__(self):
        self.messages: list[dict] = []

    def publish(self, message: dict) -> None:
        self.messages.append(message)

# --- Тестовый провайдер контекста ---
class TestContextProvider(interfaces.ContextProvider):
    def __init__(self, request: Request):
        self._request = request

    def get_idempotency_key(self) -> str:
        return self._request.headers.get("Idempotency-Key", "") or str(uuid.uuid4())

# --- Провайдеры для Dishka (только нужное) ---
class TestProviders(Provider):
    @provide(scope=Scope.REQUEST)
    async def context_provider(self, request: Request) -> interfaces.ContextProvider:
        return TestContextProvider(request)

    message_broker = provide(
        TestMessageBroker,
        scope=Scope.APP,
        provides=interfaces.MessageBroker,
    )

    lead_repository = provide(
        LeadRepository,
        scope=Scope.REQUEST,
        provides=interfaces.LeadRepository,
    )
    keys_repository = provide(
        KeysRepository,
        scope=Scope.REQUEST,
        provides=interfaces.KeysRepository,
    )

    create_lead_interactor = provide(
        CreateLeadInteractor,
        scope=Scope.REQUEST,
        provides=CreateLeadInteractor,
    )
    get_lead_interactor = provide(
        GetLeadInteractor,
        scope=Scope.REQUEST,
        provides=GetLeadInteractor,
    )

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# --- Postgres testcontainer + alembic миграции ---
@pytest.fixture(scope="session")
def postgres_container() -> AsyncIterator[PostgresContainer]: # type: ignore
    image = os.environ.get("TEST_PG_IMAGE", "postgres:16-alpine")
    with PostgresContainer(image) as pg:
        pg.start()
        yield pg

def _run_migrations_sync(db_url: str) -> None:
    backend_dir = Path(__file__).parent.parent  
    alembic_ini = backend_dir / "alembic.ini"
    if not alembic_ini.exists():
        raise RuntimeError("Не найден alembic.ini для миграций")
    cfg = AlembicConfig(str(alembic_ini))
    cfg.set_main_option("script_location", str(backend_dir / "migrations"))
    cfg.set_main_option("sqlalchemy.url", db_url.replace("+asyncpg", ""))  
    command.upgrade(cfg, "head")

@pytest.fixture(scope="session")
def test_db_config(postgres_container: PostgresContainer) -> PostgresConfig:
    url = postgres_container.get_connection_url()
    async_url = url.replace("postgresql://", "postgresql+asyncpg://")

    _, rest = async_url.split("://", 1)
    creds, host_part = rest.split("@", 1)
    user, password = creds.split(":", 1)
    host_port, database = host_part.rsplit("/", 1)
    host, port = host_port.split(":", 1)
    cfg = PostgresConfig(
        POSTGRES_HOST=host,
        POSTGRES_PORT=int(port),
        POSTGRES_USER=user,
        POSTGRES_PASSWORD=password,
        POSTGRES_DB=database,
    )
    _run_migrations_sync(async_url)
    return cfg

@pytest.fixture(scope="session")
def async_engine(test_db_config: PostgresConfig):
    url = "postgresql+asyncpg://{login}:{password}@{host}:{port}/{database}".format(
        login=test_db_config.login,
        password=test_db_config.password,
        host=test_db_config.host,
        port=test_db_config.port,
        database=test_db_config.database,
    )
    engine = create_async_engine(url)
    return engine

@pytest.fixture(scope="session")
async def session_maker(async_engine):
    return async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

@pytest.fixture(scope="function")
async def db_session(session_maker) -> AsyncIterator[AsyncSession]:
    async with session_maker() as session:
        for table in reversed(models.Base.metadata.sorted_tables):
            await session.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))
        await session.commit()
        yield session
        await session.rollback()

# --- Фабрики интеракторов для интеграционных тестов ---
class DummyMessageBroker(interfaces.MessageBroker):
    def __init__(self):
        self.messages: list[dict] = []
    def publish(self, message: dict) -> None:
        self.messages.append(message)

class StaticContext(interfaces.ContextProvider):
    def __init__(self, key: str):
        self._key = key
    def get_idempotency_key(self) -> str:
        return self._key

@pytest.fixture
def message_broker():
    return DummyMessageBroker()

@pytest.fixture
def lead_repo(db_session: AsyncSession):
    return LeadRepository(db_session)

@pytest.fixture
def keys_repo(db_session: AsyncSession):
    return KeysRepository(db_session)

@pytest.fixture
def create_lead_interactor(lead_repo, keys_repo, message_broker, db_session):
    def _factory(idempotency_key: str):
        context = StaticContext(idempotency_key)
        return CreateLeadInteractor(
            lead_repo=lead_repo,
            keys_repo=keys_repo,
            message_broker=message_broker,
            session=db_session,  # DBSession протокол
            context=context,
        )
    return _factory

@pytest.fixture
def get_lead_interactor(lead_repo):
    return GetLeadInteractor(lead_repo)

# --- FastAPI приложение для e2e ---
@pytest.fixture(scope="session")
def test_config(test_db_config: PostgresConfig) -> Config:
    return Config(
        postgres=test_db_config,
        fastapi=FastApiConfig(),
        rabbitmq=RabbitMqConfig(),  # не используется
    )

@pytest.fixture(scope="session")
async def app(test_config: Config, session_maker):
    # Локальный провайдер сессии вместо полноценного DBProviders
    class DBProvider(Provider):
        @provide(scope=Scope.REQUEST)
        async def get_async_session(self) -> AsyncIterator[DBSession]:
            async with session_maker() as s:
                yield s
    container = make_async_container(
        DBProvider(),
        TestProviders(),
        context={Config: test_config},
    )
    app = FastAPI(title="test")
    app.router.route_class = DishkaRoute
    app.include_router(leads_router.router)
    setup_dishka(container, app)
    return app

@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
