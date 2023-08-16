import json
#from gpiozero import CPUTemperature
# import psutil
from StringEncode import StringEncode
from Encryption import Encryption
from datetime import timezone
import datetime

class Message:
    def __init__(self):
        # Timec
        utc_time = datetime.datetime.now(timezone.utc).replace(tzinfo=timezone.utc)
        self.message= dict()
        self.message['From'] = 'Publisher-0001-3A+'
        self.message['UTC-Time'] = utc_time.timestamp()
        
    def get(self):
        # cpu = CPUTemperature()
        string_encode = StringEncode()
        plain_text_message = dict()
        plain_text_message['CPU_Temperature'] = "40 degree"#cpu.temperature
        plain_text_message['CPU_Usage'] = "cpu usage"#psutil.cpu_percent()
        plain_text_message['RAM_Usage'] = "memory usage"#psutil.virtual_memory().percent
        plain_text = json.dumps(plain_text_message)
        
        encryption = Encryption()
        cipher_AES_Key,cipher_text = encryption.encrypt(plain_text)

        self.message['Cipher_AES_Key'] = cipher_AES_Key
        self.message['Cipher_Text'] = cipher_text
        return (json.dumps(self.message),plain_text)