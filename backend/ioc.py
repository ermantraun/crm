from dishka import Provider, provide, Scope, from_context, AnyOf
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from config import Config
from infrastructure.db.database import new_session_maker
from typing import AsyncIterable
from infrastructure.db import repositories as db_repositories
from infrastructure.queue.rabbitmq_broker import RabbitMQMessageBroker
from aio_pika import RobustConnection, connect_robust
from application.lead.interactors import (
    CreateLeadInteractor,
    GetLeadInteractor,
    CreateInsightInteractor,
)
from infrastructure.context import ContextProvider as InfraContextProvider
from infrastructure.generator import InsightGenerator as InfraInsightGenerator
from application.lead import interfaces as lead_interfaces
from application.common_interfaces import DBSession
class ConfigProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

class DBProviders(Provider):
    @provide(scope=Scope.APP)
    async def get_session_maker(self, config: Config) -> async_sessionmaker[AsyncSession]:
        async_session_maker = await new_session_maker(config.postgres)
        return async_session_maker

    @provide(scope=Scope.REQUEST)
    async def get_async_session(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> AnyOf[AsyncIterable[AsyncSession], AsyncIterable[DBSession]]:
        async with async_sessionmaker() as session:
            yield session

    lead_repository = provide(
        db_repositories.LeadRepository,
        scope=Scope.REQUEST,
        provides=lead_interfaces.LeadRepository,
    )
    keys_repository = provide(
        db_repositories.KeysRepository,
        scope=Scope.REQUEST,
        provides=lead_interfaces.KeysRepository,
    )
    insight_repository = provide(
        db_repositories.InsightRepository,
        scope=Scope.REQUEST,
        provides=lead_interfaces.InsightRepository,
    )

class FastApiProviders(Provider):
    context_provider = provide(
        InfraContextProvider,
        scope=Scope.REQUEST,
        provides=lead_interfaces.ContextProvider,
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
    message_broker = provide(
        RabbitMQMessageBroker,
        scope=Scope.APP,
        provides=lead_interfaces.MessageBroker,
    )

class RabbitMQProviders(Provider):
    @provide(scope=Scope.APP)
    async def rabbit_connection(self, config: Config) -> RobustConnection:
        return await connect_robust(
            host=config.rabbitmq.host,
            port=config.rabbitmq.port,
            login=config.rabbitmq.user,
            password=config.rabbitmq.password,
            virtualhost=config.rabbitmq.virtual_host,
        )

    insight_generator = provide(
        InfraInsightGenerator,
        scope=Scope.APP,
        provides=lead_interfaces.InsightGenerator,
    )
    create_insight_interactor = provide(
        CreateInsightInteractor,
        scope=Scope.REQUEST,
        provides=CreateInsightInteractor,
    )