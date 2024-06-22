from flask import Flask,request
from flask_cors import CORS, cross_origin
import yaml
import json
from OpenSSL import SSL

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