# import logging
import asyncio
import yaml
import time
from Message import Message
from amqtt.client import MQTTClient
from amqtt.mqtt.constants import QOS_0, QOS_1, QOS_2
from Render import Render
import json
from gpiozero import CPUTemperature
import psutil

# logger = logging.getLogger(__name__)

# Load Setting
def load_setting():
    with open('setting.yaml', 'r') as f:
        return yaml.safe_load(f)

# Main loop
async def main_loop(setting):
    # MQTT send
    MQTT_client = MQTTClient()
    await MQTT_client.connect('mqtt://'+setting['BrockerIP']+'/')
    while True:
        try:
            message = Message()
            message_text,plain_text = message.get()
            message_object = json.loads(message_text)
            # Rende Table
            cpu = CPUTemperature()
            render = Render()
            render.table(
                CPU_Temperature = str(cpu.temperature),
                CPU_Usage = str(psutil.cpu_percent()),
                RAM_Usage = str(psutil.virtual_memory().percent),
                Plain_text = plain_text,
                Cipher_Key = message_object['Cipher_AES_Key'],
                Cipher_Text = message_object['Cipher_Text'],
                Policy = setting['Policy'],
                Brocker_IP = setting['BrockerIP'],
                Topic = '/message/public'
            )
            tasks = [
                asyncio.ensure_future(MQTT_client.publish('message/public', message_text.encode(encoding='utf-8'), qos=QOS_2)),
            ]
            time.sleep(int(setting['IntervelTimeSecond']))
        except:
            pass
    await asyncio.wait(tasks)
    await MQTT_client.disconnect()

# Main function
if __name__ == '__main__':
    setting = load_setting()
    asyncio.get_event_loop().run_until_complete(main_loop(setting))