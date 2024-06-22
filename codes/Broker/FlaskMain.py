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


  
# Receive Ciphertext
@app.route("/Ciphertext/", methods=['GET', 'POST'])
@cross_origin()
def Ciphertext():
  CT = request.form.get('CT')

  with open('brokerCT.yaml', 'w') as f:
    yaml.dump(CT, f)

  return {"result": CT}


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
    rlt = "left = right"
  else:
    rlt = "false"
    
  return {"result": rlt}