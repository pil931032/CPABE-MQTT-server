import logging
import asyncio

from amqtt.client import MQTTClient
from amqtt.mqtt.constants import QOS_0, QOS_1, QOS_2

logger = logging.getLogger(__name__)

async def test_coro():
    text = input('Please in put text: ')
    C = MQTTClient()
    await C.connect('mqtt://127.0.0.1/')
    tasks = [
        asyncio.ensure_future(C.publish('message/public', text.encode(encoding='utf-8'), qos=QOS_2)),
    ]
    await asyncio.wait(tasks)
    logger.info("messages published")
    await C.disconnect()

if __name__ == '__main__':
    formatter = "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=formatter)
    asyncio.get_event_loop().run_until_complete(test_coro())