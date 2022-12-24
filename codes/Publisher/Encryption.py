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

class Encryption:

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

    def encrypt(self,message:str):
        string_encode = StringEncode()
        message_int:int = string_encode.string_to_integer(message)

        dac = DACMACS(PairingGroup('SS512'))
        GPP, GMK = dac.setup()

        users = {} # public user data
        authorities = {}

        authorityAttributes = ["ONE", "TWO", "THREE", "FOUR"]
        authority1 = "authority1"
        policy_str = '((ONE or THREE) and (TWO or FOUR))'

        dac.setupAuthority(GPP, authority1, authorityAttributes, authorities)

        alice = { 'id': 'alice', 'authoritySecretKeys': {}, 'keys': None }
        alice['keys'], users[alice['id']] = dac.registerUser(GPP)

        bob = { 'id': 'bob', 'authoritySecretKeys': {}, 'keys': None }
        bob['keys'], users[bob['id']] = dac.registerUser(GPP)

        for attr in authorityAttributes[0:-1]:
            dac.keygen(GPP, authorities[authority1], attr, users[alice['id']], alice['authoritySecretKeys'])
            dac.keygen(GPP, authorities[authority1], attr, users[bob['id']], bob['authoritySecretKeys'])

        # Generate A String for AES Key
        AES_key_before_serialization  = PairingGroup('SS512').random(GT)
        CT = dac.encrypt(GPP, policy_str, AES_key_before_serialization, authorities[authority1])
        cipher_AES_key = objectToBytes(CT, PairingGroup('SS512')).decode("utf-8")

        return cipher_AES_key

if __name__ == '__main__':
    encryption = Encryption()
    cipher = encryption.AES_encrypt('咕咕雞','馬克思直呼內行')
    print(cipher)
    result = encryption.AES_decrypt(cipher,'馬克思直呼內行')
    print("解密後",result)