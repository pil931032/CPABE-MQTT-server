from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
from charm.schemes.abenc.abenc_dacmacs_yj14 import DACMACS
from charm.core.engine.util import objectToBytes,bytesToObject
from StringEncode import StringEncode
from base64 import b64encode,b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import json
import hashlib
import yaml
import requests

class Decryption:
    def load_setting(self):
        with open('setting.yaml', 'r') as f:
            return yaml.safe_load(f)

    def load_subscriber_user_password(self):
        with open('subscriber_user_password.yaml', 'r') as f:
            return yaml.safe_load(f)

    def AES_encrypt(self,message:str,key:str):
        message = message.encode("utf-8")
        key = key.encode("utf-8")

        shavalue = hashlib.sha256()
        shavalue.update(key)
        key= shavalue.digest()

        cipher = AES.new(key, AES.MODE_CTR)
        ct_bytes = cipher.encrypt(message)
        nonce = b64encode(cipher.nonce).decode('utf-8')
        ct = b64encode(ct_bytes).decode('utf-8')
        result = json.dumps({'nonce':nonce, 'ciphertext':ct})
        return result 

    def AES_decrypt(self,cipher_text:str,key:str):
        key = key.encode("utf-8")
        shavalue = hashlib.sha256()
        shavalue.update(key)
        key= shavalue.digest()
        try:
            b64 = json.loads(cipher_text)
            nonce = b64decode(b64['nonce'])
            ct = b64decode(b64['ciphertext'])
            cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
            pt = cipher.decrypt(ct)
            return pt.decode('utf-8')
        except (ValueError, KeyError):
            print("Incorrect decryption")

    def get_global_parameter(self):
        """
        return GPP, authority
        """
        # Load server ip
        setting = self.load_setting()
        user_password = self.load_subscriber_user_password()
        # Receice global parameters
        r = requests.get('http://'+setting['BrockerIP']+':443/subscriber/global-parameters/'+user_password['user']+'/'+user_password['password'])
        json_obj = json.loads(r.text)
        GPP = bytesToObject(json_obj['GPP'], PairingGroup('SS512'))
        authority = bytesToObject(json_obj['authority'], PairingGroup('SS512'))
        # Create GPP H function
        groupObj = PairingGroup('SS512')
        dac = DACMACS(groupObj)
        temp_GPP, temp_GMK = dac.setup()
        GPP['H']= temp_GPP['H']
        # Retrun
        return (GPP,tuple(authority))

    def get_subscriber_decrypt_keys(self):
        # Load server ip
        setting = self.load_setting()
        user_password = self.load_subscriber_user_password()
        # Receice global parameters
        r = requests.get('http://'+setting['BrockerIP']+':443/subscriber/decrypt-keys/'+user_password['user']+'/'+user_password['password'])
        obj = json.loads(r.text)
        keys = obj['decrypt-keys']
        keys = bytesToObject(keys,PairingGroup('SS512'))
        return keys

    def decryption(self,cipher_key:str,cipher_text:str):
        # CPABE
        CT =  bytesToObject(cipher_text,PairingGroup('SS512'))
        dac = DACMACS(PairingGroup('SS512'))
        decryption = Decryption()
        user_key = self.get_subscriber_decrypt_keys()
        GPP,authority = self.get_global_parameter()
        TK1a = dac.generateTK(GPP, CT, user_key['authoritySecretKeys'], user_key['keys'][0])
        PT1a = dac.decrypt(CT, TK1a, user_key['keys'][1])
        # AES
        AES_key = objectToBytes(PT1a).decode("utf-8")
        result = self.AES_decrypt(cipher_text,AES_key)
        return result


if __name__ == '__main__':
    pass
    # CT = """
    # eJytWMmOFEcQ/ZXWnEDqQ2ZVLpHcLAwS8oKFLftgWaMx5mAJGYvBlhDi310R8V5kNicPw6F7eqpyifXFi/hw9ThfPTp9uLq+fvn65vb2+vr47+r39+9e3V6dT8fTf29e//PKnv5a8/lU5XyS46/s51NO7Xxq/Xzq3R/mvOnToV/H+2I/RJ8fC/O2YYs968k/tjIn/a8en+N1Lfpgi+OOL7v5eCXHErED7evYJF2XVD0+45y8HV9t+C5d3QW32w9dLHb6joN0rZisx81N/BpbVxPWddtwvJZCdUzD4/YheFXsR8cOtUc//taNRjApVf/eIK7KU0wB1W/3N2rZWv3/YfdXt03Oqo+aHB+zT6su/Bg4Irm0Kro6oOeQir/0lZ6sFjUbVf/0HZqoB7p5obsFJeGNPlWFR/ebTZWUVxVts+CVyq7KmG3MQ5mamLV1ca04vPG2Ct38DTyohhSIYH/50pykNxfGQucTOxFOsCDtCBu/fIdgFjVqmT7oz+qXqhdb/u3jkQqPt/+bJ2p2zRM3IaNZVVUnWVZkekuYOYmhUhh2jN7hsptFVBmBhwdXFXrXI3CjSRpDsSJMOlxqnlA5GmzkLlShLE8ktmuQa5i0ulh09MVcGpDqDg1Iycyd8M/uPwTxUvbFabpFlfDrxOUP0FCt+kVkmaEcGCi/QGwzOSTQdKbP9jv7LMIOUCPEtoQrTKdGU3qo8YfaVbHFo6q7eo3KJD9as9XQoQRYNne+ruywmGrBNGqVSRHxidUC6FLx9WI7dwAkHRF3Qo9jZkYmQco2mNmAM2EQeqSYfJlg3yODfUWKdMrI5YbYHEAiREmho3ogZoM5VcDVZeax50+fPnv85MVdvafB2OEeLyN7SAiJJM+YNQ+YWYj8lmy7rxj4rUqrTr6aiVCQCB4SrIoIYmJgRdGx4MhtqQYaCH4gUNAAfaPJKo2z0W5tybvCHO4BnzuTjYG2O7ab2zzBWEsQCFRkMIIbDOjGIFIKa7D5uCFkzLheVcaF+355/uKbu/utsx7Yl5l2uGZ64WA9r/Coh6HMImtal6Vwm3pWoKIEJg+8NUIdEHdPIXNN5l7nC2QTbuzkbtDdRhkSMqbP3FOzqyf1ueH7uERJO9bkyiA78CLLuEXJwOkeW/SiS5J4o6C8AZRVfLu1gy7VWa2XyvtJtn395Ocn3z7/4e4eG7BrEQZ1hxw75U5rFIGOOXhiTwPDUlXMDqz7wYmaTEPowcGaJKDN4q9z81gfR7KZ9VvUNMqzw2+DED5g5FirBzckkJaugqyqxDwJdE2MBhQ1UjmLGtbFzFLWN8YDISkt1awT7xPudLfVcNt3Xz37/qfjc3e/OYxviETHGKSZwC0V6W900MxXplsL3dwWHIddSWsH8dbALTRaMinD4lYyNp4EIOhID2G98loc9hBYarsgB76oM+ZwVk30L7c7weIar0s7LnLBtwWPJoxyjReSDHUKoNlMMxZRZ16gZBszgQct8+5V5xBYEhScLYETOZaGqH4bc88DjkYzT8L9DvJbDqOzXBmUsoErYOODRT0xNclNhAGm1w3aBN0fjyLjaCQz0ZZFEoZMBXW4RTdA69vrAWBHECKXaoQMGRE7zH0BK6fdtIhqICRlnSEpIGOWpZf08vOKnaFLDtrApsXRP9jtTpBje2kL6T2ZfVddasFsuDt2Dfa2ecwyV1CzBd1ZjbhGAenA7sCe0Seq2V8wU78x4Z5GTjNWBRoOr4HSDS7wTqAzfokRxnMMnvbQZ6IndS0MffItRq5HI5FNdWv9Mv/uU/gYiYW0LglL2wYyIqgrlcyLeed+ZH+QwRnoIkHD4zmDaBsXNJNUL2DJ8ggOC97a4RPcuS+NtLBwacaUADcW3sGci3mHl/ExO/WIHRB5zhuM7qJcRVPk2ce5Q0e4twBKakseKvXCUl+08gmBJcj4RaL5SKjR/GyNrLHprPhhkA6Eh3rSZuvlSGdFDy1GY5gWwEhFmjUkDG0nkRgJ6eRMCLMEdjYDqduEwc5yVeDVRp7T+tL1xHBOQb6CgMYYxcCgI6lsbEDQyexEGruDSrDZyMSnQSu7+gUrLeN+vE/FoxIzmSooOds2lPg8W+YR844YJiWwMWuRCBqkiIi8xCLRznOKFiiJ/iQGX2XynJ2YbMOs4fbi9Kum6Tz63sdjgEVhO88+O7EZ3LBgQx5VyGD5m9iMFWwvvsP6HICpgNsUNvOG6xs5aMxaZax08751zm4UyM7KNOiOjgmbNXgYvCwMJlIOJWq2sJzLxoxF7VJjBEafh1Gss0IjFMHe4FtBqPQwY3AVTs4qY8G5xRI8zlB2wubcnifdcCDYcK05BooG9ZnjdHYbJGLsTtgsCkmDvyWLlrz0xl+iuZtDS8OLguagR8vMgOkcGGWUqrqE55zuZ2bPZFh19sujL50SKk3nmHHjzC/4f4xAOVa2ps+aTFbGCVpgq9HigWuuxaWjkwmqWuuUZZCheXJvgPrxyXAh7XOSWYhFMTM1WRoYU4nhaQxW6MzFdZ9f5qwcsbNEZRA4krSuJ8pBCp7CrUEfx0UfFdO6Dcb2NhpAM1hbPQyZvBnFnrmtvwcx1kfBGFZzTlpjvCaTdM4RY8Oos2CQIzHqGUu/6lWeAzZ1dozKbfHoa3Flj1QrEzUtDWBrc07hrNobmSXUJMYQS3v395vXf758r+66fff20YMHKHunN29PjqYPTzd//XF6EDmqb6bXHz68+vgfcqNWSQ==
    # """
    # ci_text = """
    # {\"nonce\": \"uBYrqHgNgd4=\", \"ciphertext\": \"9RJR17L/4ochq90chxe6+UGNCbOvUUCeY2nC2jCQeIXHbi0VU4EUphhTwIHds2fh8Z5h1oT6GFcj6RgTXU6AOQ==\"}
    # """
    # decryption = Decryption()
    # # decryption.decryption(CT,ci_text)

    # cipher = decryption.AES_encrypt('ABS',"123")
    # print(decryption.AES_decrypt(cipher,"123"))
    # print(type(cipher))