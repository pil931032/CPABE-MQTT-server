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
        CT =  bytesToObject(cipher_key,PairingGroup('SS512'))
        dac = DACMACS(PairingGroup('SS512'))
        decryption = Decryption()
        user_key = self.get_subscriber_decrypt_keys()
        GPP,authority = self.get_global_parameter()
        TK1a = dac.generateTK(GPP, CT, user_key['authoritySecretKeys'], user_key['keys'][0])
        PT1a = dac.decrypt(CT, TK1a, user_key['keys'][1])
        # AES
        AES_key = objectToBytes(PT1a,PairingGroup('SS512')).decode("utf-8")
        result = self.AES_decrypt(cipher_text,AES_key)
        print(result)
        return result


if __name__ == '__main__':
    pass
    CT = """
    eJylWU2PHDUQ/SujPSXSHmy37SrnhkIiIT6CAoIDQlEIOSBFgAggIZT/TlfVe9U9yYXsHma2p7tt1+erV7X/3jyuN48u/968ePHqzcu3b1+82H/d/PTPn6/f3txe9rt/v3zz12u/+8Oot5eht5da+n4x7aLdXnS/u4r9kNuL7Be69s/+2tz/2pJ8a9raamu73d03kLHfFbu7xftSsb36K/sCtXOq5tf+gtizmufvn+F72MV+vtiT1mIPk8yEET6oHbvY07nf0f1o2UJsk2Xtn7GvloUzl2K/OeJtl7Zv2Md/hTWGfW0hRV+8W+Is0dgzxDM19i3XohZmNAkJ0jy1rDjVLdEldjWFO9eJvW9ymQdqCbns44KaRGZj029hCxPK9TVHwOx2qp3TNVxg92wDuzdomwn5S5zowtkPd34VnG/Spdlck7ql80qYVwYUdPVbxWa12FUrYYnBjVwTe8nfdv+VApuYgLajB5+7w5fZbouRGl8eHQ1BWBp2cmkqpDGjRiTDo7P++G5Pgsft/2aIOx0iC8LRYtMiNmIUQedHuExd00QLDtoibxSO86fhzhYC2mcg09xovmRgDzOTZY3nYuV5zCe/cj8i9xbSNcKpIWrDzA37hy23q/QtEdKR9itkWHIcrzgn0qIOxLfSYStOi42Eigykd0NszzQCEnrkbg2qVeo5Do9tH+sx38WE83SpYd84tDJECAyFoZh51/irh1JuxoEcGESeGZkpyBKtiSAMD9ca4OprJUIh7D/gcQ9cxQZh3Y350mmuEt511AEYAzOBNIFBg/nboaHDxAZ5CrE5slXoKYrjXxEvjAKYUSGRow1BfSDlKfzZY+6wZ0+ffvb4yfOPdl4hRLtt4Z8FaHSRTXWXZ2MdotZjS2UaFRHg0Dhc1PDCAFibfRzrCnzsrqUpwv6TId7DCEIER4y5/jRQha8V9SICUBnx26m2eN5VCtJDbeJzQKWGMBYLDurb4RJT393SWcUGkAoPJyOXYcDktUhxmVf67ftnzz+/i8NIGCajsdIDeoqgBQLgxiMHCGpAMLLF9ulCcxXiAgiGEv5NfDeGhEGEwGiK9+1IO3d55NxE2S/kASVlPWJD4hBlDTLRFX4ylU0dO3hcVbpB3FowyEykYCGqwADbJNM6K5zvIijTru5CPMQNUpZ+nAOvffrkuydfPPv64x3nG1uiORa0U6EhooSF3Dj2pUKHTZT1DeqMcxi4yhbNgvc7652TuBXROlHdzJZKtrcyOyecn6IU5PIgh+yZ6/Z8ZtzZl2dqJcwxbgrcFlQOT+F2kDl/t6KSsywK3WcGcppZDkrg3ks+4GuvcB1w4czr2nFffvLZV9/unzumXJDpLSSKuDuMNcAkkUySsFfHwTD0uNtR5xmxAD7Ev+iphqicEksbF5Goe0JOFlOatSKWhdDcCiM7i1kld4sN2+0VnQTLdaYDnwTag47TsYIclaSMFWE95SRiz6LPI1ROtd3T4SiPDHoHTBQ6z737VDqHrU4KBQbkdH+SQiRdyZYk4EoY8CScjHFpZO0FKzpqtLSjXqE6ApkENC4QbUtg7LGgK1sUGnOgE7FFCg+PfiQP3Ea6O6jSRlhlK+XWFaTNYt931OfseZRpuRGKFiOMlWTCoiaIAlnZuR50q2xXTOWuFU/P0VFRdaQRKjaElKBdCK1JJYIDKCNNTpQ9CsUEKip0LCwqWQZdEiI2+Iqiz5NJuOtcWzcmO8DXXC0AQLNthxCykV2CHZE6TFAu9iABKJP9A1BP2VpoIWAw1zu7GtNjZBfTEsjQMCy0EgKRdX7otftVPNowEP3KH96FCukJOhZLJ0E5CiLJWiKDOm1Yh4GGci4R+qFPQAILczCrKUN4AaSS/gS4YdqhlKGsozkjDGrmTUMvmaniurbCCCC3H4DNTEMYHYhHCzhgIiPR2QgqtgIgTLCeyrBWx8LSrkHznmWv316zi6M2ZMEdtG10QBylELMEc6RFohLcG+ObpHCNw6iGAqrsEw/sQoxrjroS2yq5TMumuOKCaHoCCrjQvV6SklYGgQ42J7lshqQj5zRorIVES1A4lCHCgBzJdltO55iMnUwXfdYcBH5Ollj1vrlP2Vv0n5KngRz07LWEo53OzBD07qxDi4jPxumYS3FK2WG7kWMX4NfRc9BUWs/2A7ZOnKmnFzpmeCybY7DAKPy2kL+TU7Ws7ANNI2eUi5DgujCsPP+JBZhjRaRDAxcr50U0WWezqJNOWx9k3t2qnZLUdaIXncdjlNSLVSe417o9KrO7dJJXJ/fscBFHxxxb9QOI0JvMTMBFHOfMIhAhh388Njps1qm4ZTAobCGVzxaLUMuhwXaCM3Z/yuAVwiYmznOc+icOOCcPHaxzMTCEqsoYsXc7m+cW9nivL79XvVN0p307OpvFaI1midN3xpzbYSAQtR78X9iaCcfklV/B+xp4+CkRsg9wY+RwI8OFVL2Oo6K56zpJ7qlNX0jwwCx2QoMlSrMQJOE66AZzWzECGJPt9/hAFmL3ANQIuFVPCkuWUNAorCxE75GVu5c7rWQKTLYK3skpQIweJqgimx8h5snReKGcgPqtkubbsBj4K+Dr2cVxuq/kq6Do6Pr9nwo5EsSUJ9gVaqCwj/MKzMHsPIYpOT3ucuoPOPDKCMgJ6yCnSaIyOHEPJDgR/5V9C4E2WqmK9iFbJaFS5zr3+29vfnn1jznq7Z9/PHrwAAXv8tsfl4DSh5eXv/58eZD5aU8Ofz98ePPuP4WbVag=
    """
    obj = bytesToObject(CT,PairingGroup('SS512'))
    # ci_text = """
    # {\"nonce\": \"uBYrqHgNgd4=\", \"ciphertext\": \"9RJR17L/4ochq90chxe6+UGNCbOvUUCeY2nC2jCQeIXHbi0VU4EUphhTwIHds2fh8Z5h1oT6GFcj6RgTXU6AOQ==\"}
    # """
    # decryption = Decryption()
    # # decryption.decryption(CT,ci_text)

    # cipher = decryption.AES_encrypt('ABS',"123")
    # print(decryption.AES_decrypt(cipher,"123"))
    # print(type(cipher))