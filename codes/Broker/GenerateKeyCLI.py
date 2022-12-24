from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
from charm.schemes.abenc.abenc_dacmacs_yj14 import DACMACS
from charm.core.engine.util import objectToBytes,bytesToObject
import yaml

# Load attributes
def load_attributes():
    with open('attribute.yaml', 'r') as f:
        return yaml.safe_load(f)

# Load users
def load_users():
    with open('user.yaml', 'r') as f:
        return yaml.safe_load(f)

#Main
if __name__ == '__main__':
    authorityAttributes:list = load_attributes()
    users_list:list = load_users()
    authority = "authority"
    groupObj = PairingGroup('SS512')
    dac = DACMACS(groupObj)
    GPP, GMK = dac.setup()

    users = {}
    authorities = {}
    user_key_dictionary = dict()

    dac.setupAuthority(GPP, authority, authorityAttributes, authorities)

    for user_id in users_list:
        user = { 'id': user_id, 'authoritySecretKeys': {}, 'keys': None }
        user['keys'], users[user['id']] = dac.registerUser(GPP)    
        user_key_dictionary[user_id] = user

    for user_id in users_list:
        for attr in users_list[user_id]:
            dac.keygen(GPP, authorities[authority], attr, users[user_key_dictionary[user_id]['id']], user_key_dictionary[user_id]['authoritySecretKeys'])

    result = dict()
    result['authority'] = objectToBytes(authorities[authority], groupObj).decode('utf-8')
    del GPP['H']
    result['GPP'] = objectToBytes(GPP, groupObj).decode('utf-8')
    
    for user_key in user_key_dictionary:
        encode = objectToBytes(user_key_dictionary[user_key],groupObj).decode('utf-8')
        user_key_dictionary[user_key] = encode
    
    result.update(user_key_dictionary)

    with open('keys.yaml', 'w') as f:
        yaml.dump(result, f)

        # dac.keygen(GPP, authorities[authority], attr, users[alice['id']], alice['authoritySecretKeys'])
        # dac.keygen(GPP, authorities[authority], attr, users[bob['id']], bob['authoritySecretKeys'])
