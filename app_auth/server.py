import json
from os import urandom
import flask
from flask.app import Flask
from flask.json import jsonify                   
import requests               
from urllib.parse import urlencode
from hashlib import sha256
from random import SystemRandom
from flask import request   
from flask import redirect, url_for
import secrets
import mysql.connector
from requests.api import get


app = Flask(__name__)  

conn = mysql.connector.connect(user='admin', password='admin',
                              host='localhost',  # name container
                              database='spoton')   

ECHAP_CURRENT = 0
ECHAP_MAX = 10

challenge = None    # challenge criado pelo server
response = None     # resposta para o challenge criado pelo server
first = True        # re
valid = True
password = "seguranca"

# Primeiro passo do protocolo. O Server envia o DNS do site onde o user quer ser autenticado.
@app.route('/login', methods=['POST', 'GET'])                                                                 
def login():

    redirect_link = 'http://127.0.0.1:5001/dns'
    dns = 'http://127.0.0.1:5000'
    
    data = dns
    data = json.dumps(data)
    res = requests.post(redirect_link, json=data)
    print(f'Response from UAP: {res.text}')
    
    return flask.redirect(redirect_link)


@app.route('/authentication', methods=['POST', 'GET'])                                                                 
def authentication():
    global valid
    print("autenticaçãoooooooooooooooooooooooooo")
    if valid:
        data = "VALIDO"
    else:
        data = "INVALIDO"
    print(data)
    data = json.dumps(data)
    res = requests.post('http://127.0.0.1:5001/authentication', json=data)
    #print(f'Response from UAP: {res.text}')
    # do outro lado vamos receber a confirmação se o user é válido ou não
    return "Ok"

@app.route('/protocol', methods=['POST', 'GET'])                                                                 
def challenge_response():
    global first, response, challenge, ECHAP_CURRENT, ECHAP_MAX, valid

    ECHAP_CURRENT += 1

    if ECHAP_CURRENT == ECHAP_MAX:
        print("[SERVER] VALID: " + str(valid))
        return redirect(url_for('authentication'))
    
    if first:
        first = False
        create_challenge()
        data = {"challenge": challenge}
        data = json.dumps(data)
        response = get_response(challenge, None)

        print("[SERVER] Iteração número " + str(ECHAP_CURRENT) + ":")
        print(data)
        print("response to my challenge ",response)
        print("=============")

        requests.post('http://127.0.0.1:5001/protocol', json=data)
        return "Ok"
        
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
        
        payload = {'challenge': challenge_received, 'response': response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        print("[SERVER] Iteração número " + str(ECHAP_CURRENT) + ":")
        print(payload)
        print("response to new challenge ",response)
        print("=============")

        requests.post('http://127.0.0.1:5001/protocol', json=data)
        return "ok"
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

    """ print("===")
    print(received_challenge)
    print(password)
    print(mychallenge)
    print("===")
    """
    if not mychallenge:
        mychallenge = ""

    response = sha256((received_challenge+password+mychallenge).encode('utf-8')).hexdigest()
    return response


# retornar o DNS do server para a UAP saber | "http://127.0.0.1:5000/uap"
@app.route('/uap', methods=['POST', 'GET'])                                                                 
def redirect_uap():    

    if request.method == 'POST':   
        input_json = request.get_json(force=True) 
        mail = input_json["email"]
        
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM users WHERE email='{mail}'")

        data = cursor.fetchone()
        print("SQL QUERY FOUND:", data)
        cursor.close()

        password = None #recebe a password
        
        return redirect(url_for('/protocol'))
    
    else:
        return "cornisse"    
    
if __name__ == '__main__':                                                    
    app.run(host='0.0.0.0',port=5000)