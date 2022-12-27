import logging
import asyncio
import yaml
import json
from Decryption import Decryption
from Render import Render
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
            message_text = str(packet.payload.data,encoding='utf-8')
            # print("%d:  %s => %s" % (i, packet.variable_header.topic_name, message_text))
            message_obj = json.loads(message_text)
            Cipher_AES_Key = message_obj['Cipher_AES_Key']
            Cipher_Text = message_obj['Cipher_Text']
            decryption = Decryption()
            result = json.loads(decryption.decryption(Cipher_AES_Key,Cipher_Text))
            render = Render()
            render.table(
                CPU_Temperature=str(result['CPU_Temperature']),
                CPU_Usage=str(result['CPU_Usage']),
                RAM_Usage=str(result['RAM_Usage']),
                Decrypted_text = json.dumps(result),
                Cipher_Key = Cipher_AES_Key,
                Cipher_Text = Cipher_Text,
                Brocker_IP = setting['BrockerIP'],
                Proxy_IP = setting['ProxyIP']
            )
        await C.unsubscribe(['message/public'])
        await C.disconnect()
    except Exception as e:
        print(e)
        await C.unsubscribe(['message/public'])
        await C.disconnect()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(uptime_coro())