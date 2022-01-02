from hashlib import sha256
from random import SystemRandom
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template     
import secrets             
import tempfile                        
from flask import redirect, url_for
import enc

import json, os,hashlib

import requests
from requests.sessions import session   

app = Flask(__name__)

dns = "http://172.2.0.2"
challenge = None    # challenge criado pelo server
response = None     # resposta para o challenge criado pelo server
first = True        
valid = True        # o user que estamos a autenticar é valido ou não
is_valid = None     # variavel controlo para autenticar se user valido ou não
password = None
email = None
reset = False
redirect_site = False
pass_to_encrypt = None
key_to_decrypt = None
token = None

@app.route('/', methods=['POST', 'GET'])                                                                 
def index(): 
    global pass_to_encrypt

    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        pass1 = request.form['pass_to_encrypt']
        pass2 = request.form['pass_to_encrypt1']

        if pass1 != pass2:
            return render_template('index.html', valid=False)

        elif pass1 == pass2:
            pass_to_encrypt = pass1
            return redirect(url_for("login"))


@app.route('/login', methods=['POST', 'GET'])                                                                 
def login():                 
    global password, email, dns, is_valid, reset, first, redirect_site, pass_to_encrypt, token

    #receber o dns
    if request.method == 'GET':

        print("/login")

        content, empty = enc.decrypt("credentials.txt", pass_to_encrypt)

        credentials = {}
        if not empty:
            
            content = content.decode("utf-8").replace("\'", "\"")
            content = json.loads(content)

            if dns in content[0]:
                for cred in content[0][dns]:
                    saved_mail = cred["mail"]
                    saved_pass = cred["pass"]
                    credentials[saved_mail] = saved_pass
        
        enc.encrypt(str(content), "credentials.txt", pass_to_encrypt)

        return render_template('login.html', dic_mail=credentials, is_valid=is_valid)
    
    # login
    elif request.method == 'POST':

        email =  request.form['email']
        password = request.form['pass']
                
        # é enviado apenas o mail para a app
        data = {'email': email}
        data = json.dumps(data)

        # encripar email????

        res = requests.post('http://172.2.0.3:5001/uap', json=data)

        requests.post('http://localhost:5002/protocol', json=json.dumps(res.text))

        if redirect_site:

            # fazer um post com um token e o email

            data = {'token_uap':token}

            requests.post('http://172.2.0.2:80/', json=json.dumps(data))

            return redirect("http://172.2.0.2")

        return redirect(url_for('login'))


@app.route('/authentication', methods=['POST', 'GET'])                                                                 
def authentication():
    global is_valid, email, password, dns, valid, first, challenge, response, reset, redirect_site, pass_to_encrypt, key_to_decrypt
    
    # se a uap estiver válida para o server (is_valid) e se o server estiver válido para a uap (valid)
    if is_valid and valid:

        print("all valid")

        content, empty = enc.decrypt("credentials.txt", pass_to_encrypt)

        open("credentials.txt", "r+").close() # apagar dados do ficheiro

        if not empty:

            content = content.decode("utf-8").replace("\'", "\"")
            content = json.loads(content)

            new_cred = {"mail":email, "pass": password}

            if dns in content[0]:

                for cont in content[0][dns]:
                    if cont["mail"] == email and cont["pass"] == password:
                        exist = True
                
                if not exist:
                    content[0][dns].append(new_cred)

            else:
                content[0][dns] = [new_cred]

        else:
            content = [ { dns: [{"mail":email, "pass": password}] } ]

        # encriptar o ficheiro
        enc.encrypt(str(content), "credentials.txt", pass_to_encrypt)
        
        print(">> DONE")
        
        reset_variables()
        redirect_site = True
        return "redirecting to the website..."
        
    else:
        reset_variables()
        is_valid = False    

        return redirect(url_for('login'))


@app.route('/protocol', methods=['POST', 'GET'])                                                                 
def challenge_response():
    global first, valid, is_valid, response, challenge, token

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

        res = requests.post('http://172.2.0.3:5001/protocol', json=data)

        requests.post('http://localhost:5002/protocol', json=json.dumps(res.text))

        return "ok"
        
    else:
        data = request.get_json(force=True) 
        data = json.loads(data)
        data = json.loads(data)
        
        challenge_received = data['new_challenge']
        response_to_challenge_received = get_response(challenge, challenge_received)      # resposta ao challenge que recebemos

        data_received = data['response']
        valid = verify_response(response, data_received)
        
        
        create_challenge()
        response = get_response(challenge_received, challenge)

        payload = {'response': response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        res = requests.post('http://172.2.0.3:5001/protocol', json=data)

        data = json.loads(res.text)

        if 'valid' in data:
            is_valid = data['valid']
            if 'token' in data:
                token = data['token']
            return redirect(url_for('authentication'))

        requests.post('http://localhost:5002/protocol', json=json.dumps(res.text))

        return "ok"
        # data deve ser um dicionário do tipo challenge: 1 | response: 9 | is_first: true/false ...



# manda os dados com o redirect do /uap
@app.route('/dns')                                                                 
def receive_dns():
    global dns

    dns = request.args.get('referer')
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

    encrypt_pass = hashlib.md5(password.encode()).hexdigest()
    response = sha256((received_challenge+encrypt_pass+mychallenge).encode('utf-8')).hexdigest()
    return response

def random_response():
    response = sha256((str(secrets.randbelow(1000000))).encode('utf-8')).hexdigest()
    return response

if __name__ == '__main__':                                                      
    app.run(host='127.0.0.1',port=5002,debug=True)
    print("[UAP] Running on 127.0.0.1:5002")
