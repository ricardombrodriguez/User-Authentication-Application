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
import ssl


app = Flask(__name__)  

conn = mysql.connector.connect(user='admin', 
                                password='admin',
                                host='mysql',  # name container
                                port=3306,
                                database='spoton',
                                use_pure=True
                              )   

if conn.is_connected():
    print("connected")


dns = None
ECHAP_CURRENT = 0
ECHAP_MAX = 10
challenge = None    # challenge criado pelo server
response = None     # resposta para o challenge criado pelo server    
valid = True        # o user que estamos a autenticar é valido ou não
is_valid = True     # variavel controlo para autenticar se user valido ou não
password = None

# Primeiro passo do protocolo. O Server envia o DNS do site onde o user quer ser autenticado.
@app.route('/login', methods=['POST', 'GET'])                                                                 
def login():

    print("entrou!")

    redirect_link = 'http://localhost:5002/dns'
    dns = 'http://localhost:5000'
    
    # data = {"dns": dns}
    # data = json.dumps(data)
    # res = requests.post(redirect_link, json=data)
    # print(f'Response from UAP: {res.text}')
    
    return flask.redirect(redirect_link)


@app.route('/authentication', methods=['POST', 'GET'])                                                                 
def authentication():
    global is_valid

    if is_valid:
        data = "VALIDO"
    else:
        data = "INVALIDO"
    print(data)
    """ data = json.dumps(data)
    res = requests.post('http://localhost:5002/authentication', json=data) """
    #print(f'Response from UAP: {res.text}')
    # do outro lado vamos receber a confirmação se o user é válido ou não
    return "Ok"

@app.route('/protocol', methods=['POST', 'GET'])                                                                 
def challenge_response():
    global response, challenge, ECHAP_CURRENT, ECHAP_MAX, valid, is_valid

    ECHAP_CURRENT += 1
    
    if not valid:
        print("RANDOM")
        data = request.get_json(force=True) 
        data = json.loads(data)

        random_response_to_challenge_received = random_response()   # resposta random
        
        create_challenge()
        
        payload = {'response': random_response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)
        
        if ECHAP_CURRENT == ECHAP_MAX:
            print("[SERVER] VALID: " + str(valid))
            is_valid = valid
            valid = True
            ECHAP_CURRENT = int(0)
            return redirect(url_for('authentication'))
        
        return data
    
    # if first:
    #     first = False
    #     create_challenge()
    #     data = {"challenge": challenge}
    #     data = json.dumps(data)
    #     response = get_response(challenge, None)

    #     print("[SERVER] Iteração número " + str(ECHAP_CURRENT) + ":")
    #     print(data)
    #     print("response to my challenge ",response)
    #     print("=============")

    #     # requests.post('http://localhost:5002/protocol', json=data)
    #     return data
        
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

        print("[SERVER] Iteração número " + str(ECHAP_CURRENT) + ":")
        print("challenge received: " + challenge_received)
        print(payload)
        print("response to new challenge ",response)
        print("=============")

        # requests.post('http://localhost:5002/protocol', json=data)
        
        if ECHAP_CURRENT == ECHAP_MAX:
            print("[SERVER] VALID: " + str(valid))
            is_valid = valid
            valid = True
            ECHAP_CURRENT = int(0)
            return redirect(url_for('authentication'))
        
        return data
        # data deve ser um dicionário do tipo challenge: 1 | response: 9 | is_first: true/false ...

def verify_response(response, data_received):
    if data_received == response:
        return True
    else:
        return False


def create_challenge():

    global challenge
    challenge = str(secrets.randbelow(1000000))

def get_response(received_challenge, mychallenge):
    # misturar challenge com password
    global password

    if not mychallenge:
        mychallenge = ""

    response = sha256((received_challenge+password+mychallenge).encode('utf-8')).hexdigest()
    return response

def random_response():
    response = sha256((str(secrets.randbelow(1000000))).encode('utf-8')).hexdigest()
    return response

# retornar o DNS do server para a UAP saber | "http://localhost:5000/uap"
@app.route('/uap', methods=['POST', 'GET'])                                                                 
def redirect_uap():    
    global password, challenge, response, ECHAP_CURRENT

    if request.method == 'POST':   
        data = request.get_json(force=True) 
        input_json = json.loads(data)
        mail = input_json["email"]
        print(mail)
        
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE email='{mail}'")
        data = cursor.fetchone()
        print("data", data)
        cursor.close()
        
        password = data[3]     # atualiza a password

        ECHAP_CURRENT += 1
        create_challenge()
        data = {"challenge": challenge}
        data = json.dumps(data)
        response = get_response(challenge, None)
        print("[SERVER] Iteração número " + str(ECHAP_CURRENT) + ":")
        print(data)
        print("response to my challenge ",response)
        print("=============")

        return data
            
    else:
        return "get"    
