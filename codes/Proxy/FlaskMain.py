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

# Send Global Parameter
@app.route("/", methods=['GET', 'POST'])
@cross_origin()
def info():
  # Example curl  --request GET  http://10.1.0.1:443/broker/global-parameters/Alice/abc123
  return {"Info":"This is proxy for decryption"}

# Decrypt
@app.route("/decrypt/", methods=['POST'])
@cross_origin()
def decrypt():
  GPP = request.form.get('GPP')
  CT = request.form.get('CT')
  AuthoritySecretKeys = request.form.get('AuthoritySecretKeys')
  UserKey = request.form.get('UserKey')
  return {"Info":'Test'}