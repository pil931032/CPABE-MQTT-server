from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
from charm.schemes.abenc.abenc_dacmacs_yj14 import DACMACS

print("RUN revokedTest")
groupObj = PairingGroup('SS512')
dac = DACMACS(groupObj)
GPP, GMK = dac.setup()

print(GPP)
print(GMK)

users = {} # public user data
authorities = {}

authorityAttributes = ["ONE", "TWO", "THREE", "FOUR"]
authority1 = "authority1"

dac.setupAuthority(GPP, authority1, authorityAttributes, authorities)

alice = { 'id': 'alice', 'authoritySecretKeys': {}, 'keys': None }
alice['keys'], users[alice['id']] = dac.registerUser(GPP)

# print("Alice 的 Keys",alice['keys'])
# print("Users 中的 Alice",users[alice['id']])

bob = { 'id': 'bob', 'authoritySecretKeys': {}, 'keys': None }
bob['keys'], users[bob['id']] = dac.registerUser(GPP)

for attr in authorityAttributes[0:-1]:
    dac.keygen(GPP, authorities[authority1], attr, users[alice['id']], alice['authoritySecretKeys'])
    dac.keygen(GPP, authorities[authority1], attr, users[bob['id']], bob['authoritySecretKeys'])

k = groupObj.random(GT)

policy_str = '((ONE or THREE) and (TWO or FOUR))'

CT = dac.encrypt(GPP, policy_str, k, authorities[authority1])

TK1a = dac.generateTK(GPP, CT, alice['authoritySecretKeys'], alice['keys'][0])
PT1a = dac.decrypt(CT, TK1a, alice['keys'][1])
TK1b = dac.generateTK(GPP, CT, bob['authoritySecretKeys'], bob['keys'][0])
PT1b = dac.decrypt(CT, TK1b, bob['keys'][1])

assert k == PT1a, 'FAILED DECRYPTION (1a)!'
assert k == PT1b, 'FAILED DECRYPTION (1b)!'
print('SUCCESSFUL DECRYPTION 1')

# revoke bob on "ONE"
attribute = "ONE"
UK = dac.ukeygen(GPP, authorities[authority1], attribute, users[alice['id']])
dac.skupdate(alice['authoritySecretKeys'], attribute, UK['KUK'])
dac.ctupdate(GPP, CT, attribute, UK['CUK'])

TK2a = dac.generateTK(GPP, CT, alice['authoritySecretKeys'], alice['keys'][0])
PT2a = dac.decrypt(CT, TK2a, alice['keys'][1])
TK2b = dac.generateTK(GPP, CT, bob['authoritySecretKeys'], bob['keys'][0])
PT2b = dac.decrypt(CT, TK2b, bob['keys'][1])

assert k == PT2a, 'FAILED DECRYPTION (2a)!'
assert k != PT2b, 'SUCCESSFUL DECRYPTION (2b)!'
print('SUCCESSFUL DECRYPTION 2')