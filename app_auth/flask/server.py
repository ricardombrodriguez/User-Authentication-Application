import json
import os
from flask.app import Flask
import requests               
from hashlib import sha256
from flask import request, session
import secrets
import mysql.connector
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)



conn = mysql.connector.connect( user='admin', password='admin', host='mysql', port=3306, database='spoton', use_pure=True )   

@app.route('/protocol', methods=['POST', 'GET'])                                                                 
def challenge_response():

    print("/protocol")
    
    session['ECHAP_CURRENT'] += 1
    ECHAP_MAX = 10

    # final, diz se o user está autenticado ou não
    if session['ECHAP_CURRENT'] == ECHAP_MAX:

        print("[SERVER] VALID: " + str(session['valid']))
        token = str(uuid.uuid4())

        dic={'token_server':token,'mail': session['mail']}
        print(dic)
        res = requests.post(url="http://172.2.0.2/", data=dic)

        data = {"valid":True, "token": token} if session['valid'] else {"valid":False}
        print(data)        
        session['ECHAP_CURRENT']  = 0
        session['challenge'] = None    
        session['response'] = None       
        session['valid'] = True        
        session['is_valid'] = True    
        session['password'] = None

        return json.dumps(data)
    
    if not session['valid']:
        data = request.get_json(force=True) 
        data = json.loads(data)

        random_response_to_challenge_received = random_response()   # resposta random
        
        create_challenge()
        
        payload = {'response': random_response_to_challenge_received[:3], 'new_challenge': session['challenge'] }
        data = json.dumps(payload)
        
        return data

    else:
        print("else")
        data = request.get_json(force=True) 
        data = json.loads(data)

        challenge_received = data['new_challenge']
        response_to_challenge_received = get_response(session['challenge'],challenge_received)    # resposta ao challenge que recebemos

        data_received = data['response']
        session['valid'] = verify_response(session['response'], data_received)
        
        create_challenge()

        session['response'] = get_response(challenge_received, session['challenge'])
        
        payload = {'response': response_to_challenge_received[:3], 'new_challenge': session['challenge']  }
        data = json.dumps(payload)
        
        return data


@app.route('/uap', methods=['POST', 'GET'])                                                                 
def redirect_uap():    

    print("/uap")

    session['ECHAP_CURRENT'] = 0
    session['challenge'] = None
    session['response'] = None
    session['is_valid'] =  True
    session['password'] = None
    session['valid'] = True
    session['mail'] = None
    session['dns'] = None

    if request.method == 'POST':   

        data = request.get_json(force=True) 
        input_json = json.loads(data)
        session['mail'] = input_json["email"]
        
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE email='{session['mail']}'")
        data = cursor.fetchone()
        cursor.close()
        
        password = data[3]     # atualiza a password
        session['password'] = password

        session['ECHAP_CURRENT'] += 1
        create_challenge()
        data = {"challenge": session['challenge'] }
        data = json.dumps(data)
        session['response'] = get_response(session['challenge'] , None)

        return data  


def verify_response(response, data_received):

    if response.startswith(data_received):
        print("resposta igual")
        return True
    else:
        return False


def create_challenge():
    session['challenge']  = str(secrets.randbelow(1000000))

def get_response(received_challenge, mychallenge):
    if not mychallenge: mychallenge = ""
    return sha256((received_challenge+ session['password']+mychallenge).encode('utf-8')).hexdigest()

def random_response():
    return sha256((str(secrets.randbelow(1000000))).encode('utf-8')).hexdigest()
