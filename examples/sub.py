import logging
import asyncio

from amqtt.client import MQTTClient, ClientException
from amqtt.mqtt.constants import QOS_0,QOS_1, QOS_2

logger = logging.getLogger(__name__)

async def uptime_coro():
    C = MQTTClient()
    await C.connect('mqtt://127.0.0.1/')
    await C.subscribe([
            ('message/public', QOS_2),
        ])
    try:
        for i in range(1, 100):
            message = await C.deliver_message()
            packet = message.publish_packet
            print("%d:  %s => %s" % (i, packet.variable_header.topic_name, str(packet.payload.data,encoding='utf-8')))
        await C.unsubscribe(['message/public'])
        await C.disconnect()
    except ClientException as ce:
        logger.error("Client exception: %s" % ce)

if __name__ == '__main__':
    formatter = "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    # logging.basicConfig(level=logging.DEBUG, format=formatter)
    asyncio.get_event_loop().run_until_complete(uptime_coro())