from flask import Flask,request
from flask_cors import CORS, cross_origin
import yaml
import json
from OpenSSL import SSL
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
from abenc_lwh import ABENCLWH
from charm.core.engine.util import objectToBytes,bytesToObject
# from StringEncode import StringEncode
from base64 import b64encode,b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Decryption import Decryption
# OpenSSL
context = SSL.Context(SSL.TLSv1_2_METHOD)
context.use_privatekey_file('ca.key')
context.use_certificate_file('ca.crt') 

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Load keys
def load_keys():
    with open('keys.yaml', 'r') as f:
        return yaml.safe_load(f)

# Load users_passwords
def load_publisher_users_passwords():
    with open('publisher_user_password.yaml', 'r') as f:
        return yaml.safe_load(f)

# Load users_passwords
def load_subscriber_users_passwords():
    with open('subscriber_user_password.yaml', 'r') as f:
        return yaml.safe_load(f)

# Send Global Parameter
@app.route("/broker/global-parameters/<user>/<password>", methods=['GET', 'POST'])
@cross_origin()
def broker_global_parameters(user,password):
  # Example curl  --request GET  http://10.1.0.1:443/broker/global-parameters/Alice/abc123
  # Verify Auth
  user_password = load_publisher_users_passwords()
  try:
    if user_password[user] != password:
      return {'code':0}
  except:
    return {'code':0}
  # Send Global Parameters
  global_parameters = dict()
  keys = load_keys()
  global_parameters['GPP'] = keys['GPP']
  global_parameters['authority'] = keys['authority']
  global_parameters:str = json.dumps(global_parameters)
  return global_parameters

# Send Global Parameter
@app.route("/subscriber/global-parameters/<user>/<password>", methods=['GET', 'POST'])
@cross_origin()
def subscriber_global_parameters(user,password):
  # Example curl  --request GET  http://127.0.0.1:443/subscriber/global-parameters/Tom/ccc123
  # Verify Auth
  user_password = load_subscriber_users_passwords()
  try:
    if user_password[user] != password:
      return {'code':0}
  except:
    return {'code':0}
  # Send Global Parameters
  global_parameters = dict()
  keys = load_keys()
  global_parameters['GPP'] = keys['GPP']
  global_parameters['authority'] = keys['authority']
  global_parameters:str = json.dumps(global_parameters)
  return global_parameters

# Send user decrypt keys
@app.route("/subscriber/decrypt-keys/<user>/<password>", methods=['GET', 'POST'])
@cross_origin()
def subscriber_decrypt_keys(user,password):
  # Example curl  --request GET  http://127.0.0.1:443/subscriber/decrypt-keys/Alice/ccc123
  # Verify Auth
  user_password = load_subscriber_users_passwords()
  try:
    if user_password[user] != password:
      return {'code':0}
  except:
    return {'code':0}
  # Send Global Parameters
  global_parameters = dict()
  keys = load_keys()
  keys = keys[user]
  keys:str = json.dumps({'decrypt-keys':keys})
  return keys


# Load trusted_party_passwords
def load_trusted_party_passwords():
    with open('trusted_party_password.yaml', 'r') as f:
        return yaml.safe_load(f)

@app.route("/trusted_party/decrypt-keys/<user>/<password>", methods=['GET', 'POST'])
@cross_origin()
def trusted_party_decrypt_keys(user,password):
  # Example curl  --request GET  http://127.0.0.1:443/subscriber/decrypt-keys/Alice/ccc123
  # Verify Auth
  user_password = load_trusted_party_passwords()
  try:
    if user_password[user] != password:
      return {'code':0}
  except:
    return {'code':0}
  # Send Global Parameters
  global_parameters = dict()
  keys = load_keys()
  keys = keys[user]
  keys:str = json.dumps({'decrypt-keys':keys})
  return keys


  
# Receive ABE Ciphertext (Cipher AES Key)
@app.route("/Ciphertext/", methods=['GET', 'POST'])
@cross_origin()
def Ciphertext():
  CT = request.form.get('CT')

  with open('brokerCT.yaml', 'w') as f:
    yaml.dump(CT, f)

  return {"result": CT}

# Receive encrypted message
@app.route("/EncMessage/", methods=['GET', 'POST'])
@cross_origin()
def EncMessage():
  EncM = request.form.get('encm')

  with open('brokerEncM.yaml', 'w') as f:
    yaml.dump(EncM, f)

  return {"result": EncM}


# keyword search
@app.route("/SearchingKW/", methods=['GET', 'POST'])
@cross_origin()
def SearchingKW():
  TD = request.form.get('TD')
  dac = ABENCLWH(PairingGroup('SS512'))
  with open("brokerCT.yaml") as stream:
    try:
      cipher_key = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
      print(exc)
  CT =  bytesToObject(cipher_key,PairingGroup('SS512'))
  TrapDoor =  bytesToObject(TD,PairingGroup('SS512'))

  left = pair(CT['C2'], TrapDoor['T1'])
  rho3 = dac.group.random()
  right_tmp = rho3 - rho3
  for i, j in zip(CT['I_hat'], TrapDoor['T5']):
    right_tmp = right_tmp + i * j  
    right = CT['E'] ** (TrapDoor['T3'] * right_tmp)

  print("left:  ", left)
  print("right: ", right)
  if left == right:
    rslt = "keywords match"
  else:
    rslt = "no match"

  return {"result": rslt}

# Subscribe Emulation: subscribe(tobic, trapdoor)
@app.route("/SubscriberEmu/", methods=['GET', 'POST'])
@cross_origin()
def SubscriberEmu():
  TD = request.form.get('TD')
  dac = ABENCLWH(PairingGroup('SS512'))
  with open("brokerCT.yaml") as stream:
    try:
      cipher_key = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
      print(exc)
  
  with open("brokerEncM.yaml") as stream:
    try:
      cipher_text = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
      print(exc)


  CT =  bytesToObject(cipher_key,PairingGroup('SS512'))
  TrapDoor =  bytesToObject(TD,PairingGroup('SS512'))

  left = pair(CT['C2'], TrapDoor['T1'])
  rho3 = dac.group.random()
  right_tmp = rho3 - rho3
  for i, j in zip(CT['I_hat'], TrapDoor['T5']):
    right_tmp = right_tmp + i * j  
    right = CT['E'] ** (TrapDoor['T3'] * right_tmp)

  # print("left:  ", left)
  # print("right: ", right)
  if left == right:
    print("true")
    rslt1 = cipher_key
    rslt2 = cipher_text
  else:
    print("false")
    rslt1 = "no match"
    rslt2 = "no match"
  # print(type(cipher_text))

  return {"result1": rslt1,"result2": rslt2}

# Receive Policy Update keys
@app.route("/PolicyUpdateKey/", methods=['GET', 'POST'])
@cross_origin()
def PolicyUpdateKey():
  puk = request.form.get('puk')
  with open('PolicyUpdateKey.yaml', 'w') as f:
    yaml.dump(puk, f)
  return {"result": puk}

# receive CTUCK from TrustedParty and check update 
@app.route("/UpdateCheck/", methods=['GET', 'POST'])
@cross_origin()
def UpdateCheck():
  GPP = request.form.get('GPP')
  AuthoritySecretKeys = request.form.get('AuthoritySecretKeys')
  UserKey = request.form.get('UserKey')
  with open("brokerCT.yaml") as stream:
    try:
      CT = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
      print(exc)
  decryption = Decryption()
  TK1a = decryption.outsourcing_decryption(GPP, CT, AuthoritySecretKeys, UserKey)
  # print(type(TK1a))
  # print(TK1a)
  # TK = objectToBytes(TK1a, PairingGroup('SS512')).decode("utf-8")
  with open('verificationToken.yaml','w') as f:
    yaml.dump(TK1a, f)
  return {"result": "CTUCK has been sent and verification token generated"}

# request VTK for verification by publisher
@app.route("/requestVTK/", methods=['GET', 'POST'])
@cross_origin()
def requestVTK():
  with open("verificationToken.yaml") as stream:
    try:
      VTK = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
      print(exc)
  # print(VTK)
  return {"result": VTK}