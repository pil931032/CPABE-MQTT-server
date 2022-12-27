import logging
import asyncio
import yaml
import time
from Message import Message
from amqtt.client import MQTTClient
from amqtt.mqtt.constants import QOS_0, QOS_1, QOS_2

# logger = logging.getLogger(__name__)

# Load Setting
def load_setting():
    with open('setting.yaml', 'r') as f:
        return yaml.safe_load(f)

# Main loop
async def main_loop(setting):
    counter = 0
    while True:
        counter += 1
        message = Message()
        message_text = message.get()
        print(message_text)
        MQTT_client = MQTTClient()
        await MQTT_client.connect('mqtt://'+setting['BrockerIP']+'/')
        tasks = [
            asyncio.ensure_future(MQTT_client.publish('message/public', message_text.encode(encoding='utf-8'), qos=QOS_2)),
        ]
        await asyncio.wait(tasks)
        await MQTT_client.disconnect()
        time.sleep(int(setting['IntervelTimeSecond']))

# Main function
if __name__ == '__main__':
    setting:dict = load_setting()
    asyncio.get_event_loop().run_until_complete(main_loop(setting))