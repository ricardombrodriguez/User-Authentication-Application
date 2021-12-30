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
from requests.sessions import session   

app = Flask(__name__)

dns = "http://localhost:5000"
ECHAP_CURRENT = 0
ECHAP_MAX = 10
challenge = None    # challenge criado pelo server
response = None     # resposta para o challenge criado pelo server
first = True        
valid = True        # o user que estamos a autenticar é valido ou não
is_valid = True     # variavel controlo para autenticar se user valido ou não
password = None
email = None

@app.route('/', methods=['POST', 'GET'])                                                                 
def index():                 
    global password, email, dns
    #receber o dns

    # login
    if request.method == 'POST':

        print("post")
        email =  hashlib.md5(request.form['email'].encode()).hexdigest()
        password = hashlib.md5(request.form['pass'].encode()).hexdigest()
        
        # ALTERAR AQUI !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        email = request.form['email']
        
        # é enviado apenas o mail para a app
        data = {'email': email}
        data = json.dumps(data)

        # encripar email????

        res = requests.post('http://172.2.0.3:5001/uap', json=data)

        requests.post('http://localhost:5002/protocol', json=json.dumps(res.text))

        return "login sent"

    # verificar se existe ou não credenciais para o dns
    else:

        saved_mail = ""
        saved_pass = ""

        with open("credentials.json") as credentials:
            data = json.load(credentials)
            
            if data:
                data = data[0]
                
                # Buscar as credenciais
                if dns in data:
                    saved_mail = data[dns]["mail"]
                    saved_pass = data[dns]["pass"]
                
            
        return render_template('index.html' , saved_mail=saved_mail, saved_pass=saved_pass)

@app.route('/authentication', methods=['POST', 'GET'])                                                                 
def authentication():
    global is_valid, email, password, dns
    
    if is_valid:
        valid = "VALIDO"
        with open("credentials.json", "w+") as credentials:
            lines = credentials.readlines()
            if lines != []:
                data = json.load(credentials)
                data = data[0]
                print(data)
                # Buscar as credenciais
                # TODO encriptar e isso...
                if dns in data:
                    data[dns]["mail"] = email
                    data[dns]["pass"] = password
                
                else:
                    list(data).append( json.dumps(f"{{'{dns}': {{'mail': '{email}', 'pass': '{password}'}} }}"))
                    credentials.write(json.dumps(data))
            else:
                data = json.dumps(f"{{'{dns}': {{'mail': '{email}', 'pass': '{password}'}} }}")
                credentials.write(json.dumps(data))
            
    else:
        valid = "INVALIDO"
    print(valid)
    # data = json.dumps(data)
    # res = requests.post('http:/172.2.0.3:5000/authentication', json=data)
    
    #print(f'Response from UAP: {res.text}')
    # do outro lado vamos receber a confirmação se o user é válido ou não
    return "Ok"

@app.route('/protocol', methods=['POST', 'GET'])                                                                 
def challenge_response():
    global first, valid, is_valid, response, challenge, ECHAP_CURRENT, ECHAP_MAX

    print("protocol")

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

        res = requests.post('http:/172.2.0.3:5001/protocol', json=data)

        requests.post('http://localhost:5002/protocol', json=json.dumps(res))
        
        return "ok"

    if first:
        first = False
        data = request.get_json(force=True)
        data = json.loads(data)
        data = json.loads(data)

        print("dados recebidos no first:")
        print(type(data))
        print(data)

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

        res = requests.post('http:/172.2.0.3:5001/protocol', json=data)

        requests.post('http://localhost:5002/protocol', json=json.dumps(res))

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

        res = requests.post('http:/172.2.0.3:5001/protocol', json=data)

        requests.post('http://localhost:5002/protocol', json=json.dumps(res))

        return "ok"
        # data deve ser um dicionário do tipo challenge: 1 | response: 9 | is_first: true/false ...



# manda os dados com o redirect do /uap
@app.route('/dns')                                                                 
def receive_dns():
    global dns

    print("DNS recebido: ", dns)
    # redirect para o "/"
    return redirect(url_for('index'))


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
    app.run(host='127.0.0.1',port=5002)
    print("[UAP] Running on 127.0.0.1:5002")
