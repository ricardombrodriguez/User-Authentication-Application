import json
from logging import disable
import flask
from flask.app import Flask
import requests               
from hashlib import sha256
from flask import request   
from flask import redirect, url_for
import secrets, hashlib
import mysql.connector
import uuid

app = Flask(__name__)  

conn = mysql.connector.connect(user='admin', 
                               password='admin',
                               host='mysql',
                               port=3306,
                               database='spoton',
                               use_pure=True
                              )   

dns = None
ECHAP_CURRENT = 0
ECHAP_MAX = 10
challenge = None    # challenge criado pelo server
response = None     # resposta do user para o challenge criado pelo server    
valid = True        # o user que estamos a autenticar é valido ou não
is_valid = True     # variavel controlo para autenticar se user valido ou não
password = None
controlo = False
mail = None

@app.route('/protocol', methods=['POST', 'GET'])                                                                 
def challenge_response():
    global response, challenge, ECHAP_CURRENT, ECHAP_MAX, valid, is_valid, password, controlo, mail
    ECHAP_CURRENT += 1

    # final, diz se o user está autenticado ou não
    if ECHAP_CURRENT == ECHAP_MAX:

        print("[SERVER] VALID: " + str(valid))
        token = str(uuid.uuid4())
        # enviar para o index.php?

        requests.post('http://172.2.0.2', json=json.dumps({"token_server":token,"mail":mail}))

        data = {"valid":True, "token": token} if valid else {"valid":False}
        print(data)        
        controlo = valid
        ECHAP_CURRENT = 0
        challenge = None    
        response = None       
        valid = True        
        is_valid = True    
        password = None

        return json.dumps(data)
    
    if not valid:
        data = request.get_json(force=True) 
        data = json.loads(data)

        random_response_to_challenge_received = random_response()   # resposta random
        
        create_challenge()
        
        payload = {'response': random_response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)
        
        return data

    else:
        print("else")
        data = request.get_json(force=True) 
        data = json.loads(data)

        challenge_received = data['new_challenge']
        response_to_challenge_received = get_response(challenge,challenge_received)    # resposta ao challenge que recebemos

        data_received = data['response']
        valid = verify_response(response, data_received)
        
        # old_challenge = challenge
        
        create_challenge()
        # response = get_response(challenge_received, old_challenge)
        response = get_response(challenge_received, challenge)
        
        payload = {'response': response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)
        
        return data


def verify_response(response, data_received):

    if data_received == response:
        return True
    else:
        return False


def create_challenge():

    global challenge
    challenge = str(secrets.randbelow(1000000))

def get_response(received_challenge, mychallenge):

    global password

    if not mychallenge:
        mychallenge = ""

    response = sha256((received_challenge+password+mychallenge).encode('utf-8')).hexdigest()
    return response

def random_response():

    response = sha256((str(secrets.randbelow(1000000))).encode('utf-8')).hexdigest()
    return response

@app.route('/uap', methods=['POST', 'GET'])                                                                 
def redirect_uap():    
    global password, challenge, response, ECHAP_CURRENT, mail

    if request.method == 'POST':   
        data = request.get_json(force=True) 
        input_json = json.loads(data)
        mail = input_json["email"]
        
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE email='{mail}'")
        data = cursor.fetchone()
        cursor.close()
        
        password = data[3]     # atualiza a password

        ECHAP_CURRENT += 1
        create_challenge()
        data = {"challenge": challenge}
        data = json.dumps(data)
        response = get_response(challenge, None)

        return data  
