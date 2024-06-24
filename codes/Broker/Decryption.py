from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
from charm.schemes.abenc.abenc_dacmacs_yj14 import DACMACS
from charm.core.engine.util import objectToBytes,bytesToObject
# from StringEncode import StringEncode
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

    def outsourcing(self,GPP,CT,AuthoritySecretKeys,UserKey):
        # Load server ip
        setting = self.load_setting()
        # GPP
        del GPP['H']
        GPP = objectToBytes(GPP,PairingGroup('SS512')).decode("utf-8")
        # CT
        CT= objectToBytes(CT,PairingGroup('SS512')).decode("utf-8")
        # AuthoritySecretKeys
        AuthoritySecretKeys= objectToBytes(AuthoritySecretKeys,PairingGroup('SS512')).decode("utf-8")
        # UserKey
        UserKey= objectToBytes(UserKey,PairingGroup('SS512')).decode("utf-8")
        data = {
            'GPP': GPP,
            'CT' : CT,
            'AuthoritySecretKeys' : AuthoritySecretKeys,
            'UserKey' : UserKey
        }
        r = requests.post('http://'+setting['ProxyIP']+':8080/decrypt/', data = data)
        print(r.text)

    def decryption(self,cipher_key:str,cipher_text:str):
        # CPABE
        CT =  bytesToObject(cipher_key,PairingGroup('SS512'))
        dac = DACMACS(PairingGroup('SS512'))
        decryption = Decryption()
        user_key = self.get_subscriber_decrypt_keys()
        GPP,authority = self.get_global_parameter()
        TK1a = dac.generateTK(GPP, CT, user_key['authoritySecretKeys'], user_key['keys'][0])
        # outsourcing
        self.outsourcing(GPP, CT, user_key['authoritySecretKeys'], user_key['keys'][0])
        
        PT1a = dac.decrypt(CT, TK1a, user_key['keys'][1])
        # AES
        AES_key = objectToBytes(PT1a,PairingGroup('SS512')).decode("utf-8")
        result = self.AES_decrypt(cipher_text,AES_key)
        print(result)
        return result

    def outsourcing_decryption(self,GPP, CT, AuthoritySecretKeys, UserKey):
        GPP = bytesToObject(GPP,PairingGroup('SS512'))
        CT = bytesToObject(CT,PairingGroup('SS512'))
        AuthoritySecretKeys = bytesToObject(AuthoritySecretKeys,PairingGroup('SS512'))
        UserKey = bytesToObject(UserKey,PairingGroup('SS512'))
        dac = DACMACS(PairingGroup('SS512'))
        TK1a = dac.generateTK(GPP, CT, AuthoritySecretKeys, UserKey)
        # print(type(TK1a))
        result = objectToBytes(TK1a,PairingGroup('SS512')).decode("utf-8")
        return result
if __name__ == '__main__':
    pass