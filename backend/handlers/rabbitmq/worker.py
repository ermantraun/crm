import json
import asyncio
from typing import Optional
import aio_pika
from dishka import AsyncContainer  # removed Scope
from application.lead import dto as lead_dto
from application.lead.interactors import CreateInsightInteractor

class LeadCreatedWorker:
    def __init__(
        self,
        connection: aio_pika.RobustConnection,
        container: AsyncContainer,  # контейнер DI для per-message scope
        *,
        exchange: str = "leads",
        routing_key: str = "lead.created",
        queue_name: str = "lead.created.q",
        prefetch: int = 10,
        durable_queue: bool = True,
        durable_exchange: bool = True,
    ) -> None:
        self._connection = connection
        self._container = container
        self._exchange_name = exchange
        self._routing_key = routing_key
        self._queue_name = queue_name
        self._prefetch = prefetch
        self._durable_queue = durable_queue
        self._durable_exchange = durable_exchange
        self._channel: Optional[aio_pika.RobustChannel] = None
        self._queue: Optional[aio_pika.RobustQueue] = None
        self._exchange: Optional[aio_pika.Exchange] = None
        self._consume_tag: Optional[str] = None
        self._started = False
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        if self._started:
            return
        async with self._lock:
            if self._started:
                return
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=self._prefetch)
            self._exchange = await self._channel.declare_exchange(
                self._exchange_name,
                type=aio_pika.ExchangeType.TOPIC,
                durable=self._durable_exchange,
            )
            self._queue = await self._channel.declare_queue(
                self._queue_name,
                durable=self._durable_queue,
            )
            await self._queue.bind(self._exchange, routing_key=self._routing_key)
            self._consume_tag = await self._queue.consume(self._on_message)
            self._started = True

    async def stop(self) -> None:
        async with self._lock:
            if not self._started:
                return
            if self._queue and self._consume_tag:
                try:
                    await self._queue.cancel(self._consume_tag)
                except Exception:
                    pass
            if self._channel:
                try:
                    await self._channel.close()
                except Exception:
                    pass
            self._channel = None
            self._queue = None
            self._exchange = None
            self._consume_tag = None
            self._started = False

    async def _on_message(self, message: aio_pika.IncomingMessage) -> None:
        async with message.process(requeue=True):
            try:
                payload = json.loads(message.body.decode("utf-8"))
                lead_id = payload["lead_id"]
                content_hash = payload["content_hash"]
                content = payload.get("content", "")
            except Exception:
                message.reject(requeue=False)
                return
            print(content)
            insight_dto = lead_dto.InsighCreateInDto(
                lead_id=lead_id,
                content_hash=content_hash,
                content=content,
            )

            async with self._container() as request_container:
                interactor: CreateInsightInteractor = await request_container.get(CreateInsightInteractor)
                await interactor.create_insight(insight_dto)

__all__ = ["LeadCreatedWorker"]
