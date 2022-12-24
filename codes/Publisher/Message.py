import json
from gpiozero import CPUTemperature
import psutil

class Message:
    def __init__(self):
        self.message= dict()
        self.message['From'] = 'Publisher'
        
    def get(self):
        cpu = CPUTemperature()
        plain_text_message = dict()
        plain_text_message['CPU_Temperature'] = cpu.temperature
        plain_text_message['CPU_Usage'] = psutil.cpu_percent()
        plain_text_message['RAM_Usage'] = psutil.virtual_memory().percent
        cipher_text = json.dumps(plain_text_message)
        self.message['Cipher_Text'] = cipher_text        
        return json.dumps(self.message)