

import asyncio
import json
from typing import Optional
import aio_pika
from aio_pika import ExchangeType
from application.lead import interfaces

class RabbitMQMessageBroker(interfaces.MessageBroker):
    """
    Брокер RabbitMQ.
    DI передаёт уже установленное aio_pika.RobustConnection.
    Аргументы:
        connection: готовое RobustConnection
        exchange: имя exchange (по умолчанию 'leads')
        routing_key: routing key (по умолчанию 'lead.created')
        exchange_type: тип (по умолчанию ExchangeType.TOPIC)
    publish(dict) — fire-and-forget (фоновая задача).
    """
    def __init__(
        self,
        connection: aio_pika.RobustConnection,
    ) -> None:
        self._connection = connection
        self._exchange_name = "leads"
        self._routing_key = "lead.created"
        self._exchange_type = ExchangeType.TOPIC
        self._durable = True

        self._channel: Optional[aio_pika.RobustChannel] = None
        self._exchange: Optional[aio_pika.Exchange] = None
        self._lock = asyncio.Lock()

    async def _ensure(self) -> None:
        if self._exchange:
            return
        async with self._lock:
            if self._exchange:
                return
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                self._exchange_name,
                type=self._exchange_type,
                durable=self._durable,
            )

    async def _publish_async(self, message: dict) -> None:
        if True:
            await self._ensure()
            assert self._exchange is not None
            body = json.dumps(
            message,
            ensure_ascii=False,
            separators=(",", ":"),
            default=str,
            ).encode()
            msg = aio_pika.Message(
                body=body,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            await self._exchange.publish(msg, routing_key=self._routing_key)



    def publish(self, message: dict) -> None:
        loop = asyncio.get_running_loop()
        loop.create_task(self._publish_async(message))

    async def close(self) -> None:
        if self._channel:
            await self._channel.close()
        self._channel = None
        self._exchange = None
