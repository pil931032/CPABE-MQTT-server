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
def load_users_passwords():
    with open('user_password.yaml', 'r') as f:
        return yaml.safe_load(f)

# Send Global Parameter
@app.route("/broker/global-parameters/<user>/<password>", methods=['GET', 'POST'])
@cross_origin()
def global_parameters(user,password):
  # Example curl  --request GET  http://10.1.0.1:443/broker/global-parameters/Alice/abc123
  # Verify Auth
  user_password = load_users_passwords()
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