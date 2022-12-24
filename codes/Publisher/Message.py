import json

class Message:
    def __init__(self):
        self.message= dict()
        self.message['From'] = 'Publisher'
        
    def get(self):
        text = json.dumps(self.message)
        return text