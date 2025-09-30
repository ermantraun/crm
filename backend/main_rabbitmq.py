import asyncio
import signal
from contextlib import suppress
from config import Config
from dishka import make_async_container
from aio_pika import RobustConnection
from handlers.rabbitmq.worker import LeadCreatedWorker
from ioc import ConfigProvider, DBProviders, RabbitMQProviders

config = Config()
container = make_async_container(
    ConfigProvider(),
    DBProviders(),
    RabbitMQProviders(),
    context={Config: config},
)

async def build_worker():
    connection: RobustConnection = await container.get(RobustConnection)
    worker = LeadCreatedWorker(connection=connection, container=container)
    return worker, container, connection

async def run_worker():
    worker, container, connection = await build_worker()
    await worker.start()
    stop_event = asyncio.Event()

    def _handle_stop(*_):
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(sig, _handle_stop)

    await stop_event.wait()

    with suppress(Exception):
        await worker.stop()
    with suppress(Exception):
        await connection.close()
    with suppress(Exception):
        await container.close()

def main():
    asyncio.run(run_worker())

if __name__ == "__main__":
    main()