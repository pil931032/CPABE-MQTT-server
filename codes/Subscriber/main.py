import logging
import asyncio
import yaml
import json
from Decryption import Decryption
from Render import Render
from amqtt.client import MQTTClient, ClientException
from amqtt.mqtt.constants import QOS_0,QOS_1, QOS_2
import datetime

logger = logging.getLogger(__name__)

def load_setting():
    with open('setting.yaml', 'r') as f:
        return yaml.safe_load(f)

def load_subscriber_user_password():
    with open('subscriber_user_password.yaml', 'r') as f:
        return yaml.safe_load(f)

async def uptime_coro():
    setting = load_setting()
    user_password = load_subscriber_user_password()
    C = MQTTClient()
    await C.connect('mqtt://'+setting['BrockerIP']+'/')
    await C.subscribe([('message/public', QOS_2),])
    while True:
        try:
            message = await C.deliver_message()
            packet = message.publish_packet
            message_text = str(packet.payload.data,encoding='utf-8')
            # print("%d:  %s => %s" % (i, packet.variable_header.topic_name, message_text))
            message_obj = json.loads(message_text)
            # Cipher Text
            Cipher_AES_Key = message_obj['Cipher_AES_Key']
            Cipher_Text = message_obj['Cipher_Text']
            decryption = Decryption()
            plain_text, user_attribute= decryption.decryption(Cipher_AES_Key,Cipher_Text)
            # Time-consuming calculation
            start_time = datetime.datetime.fromtimestamp(message_obj['UTC-Time'])
            receive_time = datetime.datetime.now()
            time_consuming_string = str((receive_time - start_time).total_seconds())
            # Render
            result = json.loads(plain_text)
            render = Render()
            render.table(
                CPU_Temperature=str(result['CPU_Temperature']),
                CPU_Usage=str(result['CPU_Usage']),
                RAM_Usage=str(result['RAM_Usage']),
                Decrypted_text = json.dumps(result),
                Cipher_Key = Cipher_AES_Key,
                Cipher_Text = Cipher_Text,
                Brocker_IP = setting['BrockerIP'],
                Proxy_IP = setting['ProxyIP'],
                User = user_password['user'],
                User_ATTRIBUTE = user_attribute,
                Decryption_Time = time_consuming_string
            )
        except KeyboardInterrupt:
            await C.unsubscribe(['message/public'])
            await C.disconnect()
            break


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(uptime_coro())