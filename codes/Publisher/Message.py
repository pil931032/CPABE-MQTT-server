import json
from gpiozero import CPUTemperature
import psutil
from StringEncode import StringEncode
from Encryption import Encryption

class Message:
    def __init__(self):
        self.message= dict()
        self.message['From'] = 'Publisher-0001-3A+'
        
    def get(self):
        cpu = CPUTemperature()
        string_encode = StringEncode()
        plain_text_message = dict()
        plain_text_message['CPU_Temperature'] = cpu.temperature
        plain_text_message['CPU_Usage'] = psutil.cpu_percent()
        plain_text_message['RAM_Usage'] = psutil.virtual_memory().percent
        plain_text = json.dumps(plain_text_message)
        
        encryption = Encryption()
        cipher_AES_Key = encryption.encrypt(plain_text)

        self.message['Cipher_AES_Key'] = cipher_AES_Key
        return json.dumps(self.message)