import logging
import asyncio
import yaml

from amqtt.client import MQTTClient, ClientException
from amqtt.mqtt.constants import QOS_0,QOS_1, QOS_2

logger = logging.getLogger(__name__)

def load_setting():
    with open('setting.yaml', 'r') as f:
        return yaml.safe_load(f)

async def uptime_coro():
    setting = load_setting()
    C = MQTTClient()
    try:
        i = 0
        while True:
            await C.connect('mqtt://'+setting['BrockerIP']+'/')
            await C.subscribe([('message/public', QOS_2),])
            message = await C.deliver_message()
            packet = message.publish_packet
            print("%d:  %s => %s" % (i, packet.variable_header.topic_name, str(packet.payload.data,encoding='utf-8')))
            i+=1
            await C.unsubscribe(['message/public'])
            await C.disconnect()
    except ClientException as ce:
        logger.error("Client exception: %s" % ce)

if __name__ == '__main__':
    formatter = "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    # logging.basicConfig(level=logging.DEBUG, format=formatter)
    asyncio.get_event_loop().run_until_complete(uptime_coro())