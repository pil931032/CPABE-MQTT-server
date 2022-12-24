from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
from charm.schemes.abenc.abenc_dacmacs_yj14 import DACMACS

print("RUN revokedTest")
# 設置群
groupObj = PairingGroup('SS512')
# 實體化物件
dac = DACMACS(groupObj)
# 設置公共參數
GPP, GMK = dac.setup()

users = {} # public user data
authorities = {}

# 建立屬性
authorityAttributes = ["ONE", "TWO", "THREE", "FOUR"]
# 建立授權角色
authority1 = "authority1"

# 設置授權角色
dac.setupAuthority(GPP, authority1, authorityAttributes, authorities)

# 設置使用者
alice = { 'id': 'alice', 'authoritySecretKeys': {}, 'keys': None }
# 設置使用者鑰匙兩把鑰匙
alice['keys'], users[alice['id']] = dac.registerUser(GPP)

# print("Alice 的 Keys",alice['keys'])
# print("Users 中的 Alice",users[alice['id']])

bob = { 'id': 'bob', 'authoritySecretKeys': {}, 'keys': None }
bob['keys'], users[bob['id']] = dac.registerUser(GPP)

# 設置使用者的authority SecretKey 另外一把鑰匙
for attr in authorityAttributes[0:-1]:
    dac.keygen(GPP, authorities[authority1], attr, users[alice['id']], alice['authoritySecretKeys'])
    dac.keygen(GPP, authorities[authority1], attr, users[bob['id']], bob['authoritySecretKeys'])

# 生成明文，其實是一把加密用的 AES Key ，因為該數值只能在GT群中。
k = groupObj.random(GT)

#　制定政策
policy_str = '((ONE or THREE) and (TWO or FOUR))'

# 加密後的 Key
CT = dac.encrypt(GPP, policy_str, k, authorities[authority1])

# Alice 的第一步解密 (位於委外設施)
TK1a = dac.generateTK(GPP, CT, alice['authoritySecretKeys'], alice['keys'][0])
# Alice 的第二步解密 (Alice 本人解密)
PT1a = dac.decrypt(CT, TK1a, alice['keys'][1])
TK1b = dac.generateTK(GPP, CT, bob['authoritySecretKeys'], bob['keys'][0])
PT1b = dac.decrypt(CT, TK1b, bob['keys'][1])

# 檢查 AES Key 解密後，是否與解密前相同。
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