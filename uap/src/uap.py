from hashlib import sha256
from random import SystemRandom
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template     
import secrets                                     
from flask import redirect, url_for

import json, os,hashlib

import requests   

app = Flask(__name__)

dns = None
ECHAP_CURRENT = 0
ECHAP_MAX = 10
challenge = None    # challenge criado pelo server
response = None     # resposta para o challenge criado pelo server
first = True        
valid = True        # o user que estamos a autenticar é valido ou não
is_valid = True     # variavel controlo para autenticar se user valido ou não
password = None

@app.route('/', methods=['POST', 'GET'])                                                                 
def index():                 
    global password
    #receber o dns

    # login
    if request.method == 'POST':
        print("post")
        mail = request.form['email']
        password = hashlib.md5(request.form['pass'].encode()).hexdigest()
        print("pass ", password)

        # guardar credenciais no ficheiro json
        
        # é enviado apenas o mail para a app
        data = {'email': hashlib.md5(mail.encode())}
        data = json.dumps(data)

        # encripar email????

        requests.post('http://127.0.0.1:5000/uap', json=data)
        return "Porto 3 - 0 Benfica"

    # verificar se existe ou não credenciais para o dns
    else:

        saved_mail = ""
        saved_pass = ""

        with open("credentials.json") as credentials:
            data = json.load(credentials)
            data = data[0]
            dns = 'http://127.0.0.1:5000'
            # Buscar as credenciais
            if dns in data:
                saved_mail = data[dns]["mail"]
                saved_pass = data[dns]["pass"]

                #desencriptar e isso...
            
        return render_template('index.html' , saved_mail=saved_mail, saved_pass=saved_pass)

@app.route('/authentication', methods=['POST', 'GET'])                                                                 
def authentication():
    global is_valid
    
    if is_valid:
        data = "VALIDO"
    else:
        data = "INVALIDO"
    print(data)
    # data = json.dumps(data)
    # res = requests.post('http://127.0.0.1:5000/authentication', json=data)
    
    #print(f'Response from UAP: {res.text}')
    # do outro lado vamos receber a confirmação se o user é válido ou não
    return "Ok"

@app.route('/protocol', methods=['POST', 'GET'])                                                                 
def challenge_response():
    global first, valid, is_valid, response, challenge, ECHAP_CURRENT, ECHAP_MAX

    ECHAP_CURRENT += 1
    
    if ECHAP_CURRENT == ECHAP_MAX:
        print("[UAP] VALID: " + str(valid))
        first = True
        is_valid = valid
        valid = True
        ECHAP_CURRENT = int(0)
        return redirect(url_for('authentication'))

    if not valid:
        print("RANDOM")
        data = request.get_json(force=True) 
        data = json.loads(data)
        
        random_response_to_challenge_received = random_response()   # resposta random
        
        create_challenge()
        
        payload = {'response': random_response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        requests.post('http://127.0.0.1:5000/protocol', json=data)
        
        return "ok"

    if first:
        first = False
        data = request.get_json(force=True) 
        data = json.loads(data)

        # recebido
        challenge_received = data['challenge']
        response_to_challenge_received = get_response(challenge_received, None)

        create_challenge()
        # print(challenge)
        response = get_response(challenge_received, challenge)

        payload = {'response': response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        print("[UAP] Iteração número " + str(ECHAP_CURRENT) + ":")
        print("challenge received: " + challenge_received)
        print(payload)
        print("response to my challenge ",response)
        print("=============")

        requests.post('http://127.0.0.1:5000/protocol', json=data)
        return "ok"
        
    else:
        print("else")
        data = request.get_json(force=True) 
        data = json.loads(data)

        challenge_received = data['new_challenge']
        # response_to_challenge_received = get_response(challenge_received, challenge)    # resposta ao challenge que recebemos
        response_to_challenge_received = get_response(challenge, challenge_received)      # resposta ao challenge que recebemos

        data_received = data['response']
        valid = verify_response(response, data_received)
        
        # old_challenge = challenge
        
        create_challenge()
        # response = get_response(challenge_received, old_challenge)
        response = get_response(challenge_received, challenge)

        payload = {'response': response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        print("[UAP] Iteração número " + str(ECHAP_CURRENT) + ":")
        print("challenge received: " + challenge_received)
        print(payload)
        print("response to new challenge ",response)
        print("=============")

        requests.post('http://127.0.0.1:5000/protocol', json=data)
        return "ok"
        # data deve ser um dicionário do tipo challenge: 1 | response: 9 | is_first: true/false ...



# manda os dados com o redirect do /uap
@app.route('/dns', methods=['POST'])                                                                 
def receive_dns():

    data = request.get_json(force=True) 
    data = json.loads(data)
    print(data)
    print("DNS recebido: ", data)
    # redirect para o "/"
    return redirect(url_for('/'))


def verify_response(response_received, data_received):
    # global password
    if data_received == response_received:
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

if __name__ == '__main__':                                                      
    app.run(host='127.0.0.1',port=5001)
