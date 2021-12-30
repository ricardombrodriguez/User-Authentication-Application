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
challenge = None    # challenge criado pelo server
response = None     # resposta para o challenge criado pelo server
first = True        
valid = True        # o user que estamos a autenticar é valido ou não
is_valid = None     # variavel controlo para autenticar se user valido ou não
password = None
email = None
reset = False
redirect_site = False

@app.route('/', methods=['POST', 'GET'])                                                                 
def index():                 
    global password, email, dns, is_valid, reset, first, redirect_site


    saved_mail = ""
    saved_pass = ""

    #receber o dns
    if request.method == 'GET':
        with open("credentials.json") as credentials:
            data = json.load(credentials)
            
            if data:
                data = data[0]
                
                # Buscar as credenciais
                if dns in data:
                    saved_mail = data[dns]["mail"]
                    saved_pass = data[dns]["pass"]

        return render_template('index.html' , saved_mail=saved_mail, saved_pass=saved_pass, is_valid=is_valid)
    
    # login
    elif request.method == 'POST':

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

        if redirect_site:
            redirect_site = False
            return redirect("http://172.2.0.2")

        return redirect(url_for('index'))


@app.route('/authentication', methods=['POST', 'GET'])                                                                 
def authentication():
    global is_valid, email, password, dns, valid, first, challenge, response, reset, redirect_site
    
    # se a uap estiver válida para o server (is_valid) e se o server estiver válido para a uap (valid)
    if is_valid and valid:

        print("all valid")

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

        reset_variables()

        redirect_site = True
        
    else:
        reset_variables()
        is_valid = False    

        return redirect(url_for('index'))


@app.route('/protocol', methods=['POST', 'GET'])                                                                 
def challenge_response():
    global first, valid, is_valid, response, challenge

    print("protocol")

    # a uap vai deixar de ter o echap current e chega a uma altura em que vai receber a resposta do server a dizer se é valid ou n

    if not valid:
        print("RANDOM")
        data = request.get_json(force=True) 
        data = json.loads(data)
        
        random_response_to_challenge_received = random_response()   # resposta random
        
        create_challenge()
        
        payload = {'response': random_response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        res = requests.post('http://172.2.0.3:5001/protocol', json=data)

        data = json.loads(res.text)

        if 'valid' in data:
            is_valid = data['valid']
            return redirect(url_for('authentication'))

        requests.post('http://localhost:5002/protocol', json=json.dumps(res.text))
        
        return "ok"

    if first:
        first = False
        data = request.get_json(force=True)
        data = json.loads(json.loads(data))
        print("dados recebidos no first:")
        print(data)

        # recebido
        challenge_received = data['challenge']
        response_to_challenge_received = get_response(challenge_received, None)

        create_challenge()
        # print(challenge)
        response = get_response(challenge_received, challenge)

        payload = {'response': response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        print("[UAP] Iteração: ")
        print("challenge received: " + challenge_received)
        print(payload)
        print("response to my challenge ",response)
        print("=============")

        res = requests.post('http://172.2.0.3:5001/protocol', json=data)

        requests.post('http://localhost:5002/protocol', json=json.dumps(res.text))

        return "ok"
        
    else:
        print("else")
        data = request.get_json(force=True) 
        data = json.loads(data)
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

        print("[UAP] Iteração número:")
        print("challenge received: " + challenge_received)
        print(payload)
        print("response to new challenge ",response)
        print("=============")

        res = requests.post('http://172.2.0.3:5001/protocol', json=data)

        data = json.loads(res.text)

        if 'valid' in data:
            is_valid = data['valid']
            print("is valid")
            print(is_valid)
            return redirect(url_for('authentication'))

        requests.post('http://localhost:5002/protocol', json=json.dumps(res.text))

        return "ok"
        # data deve ser um dicionário do tipo challenge: 1 | response: 9 | is_first: true/false ...



# manda os dados com o redirect do /uap
@app.route('/dns')                                                                 
def receive_dns():
    global dns

    print("DNS recebido: ", dns)
    # redirect para o "/"
    return redirect(url_for('index'))


def reset_variables():
    global challenge, response, first, valid, is_valid, password, email
    response = None
    first = True        
    valid = True        
    password = None
    email = None

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
