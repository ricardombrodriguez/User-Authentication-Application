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

# variáveis de controlo (importantes)
dns = None          # guarda o url da aplicação que pediu uma autenticação
challenge = None    # challenge criado pelo server
response = None     # resposta para o challenge criado pelo server
first = True        # se é a primeira iteração do ECHAP ou não
valid = True        # se o user que estamos a autenticar é valido ou não
is_valid = None     # variavel controlo para autenticar se user valido ou não
password = None     # guarda password introduzida pelo user
email = None        # guarda email introduzido pelo user
redirect_site = False
pass_to_encrypt = None
token = None
invalid_cred = False

session = requests.Session()

@app.route('/', methods=['POST', 'GET'])                                                                 
def index(): 
    global pass_to_encrypt,invalid_cred

    if request.method == 'GET':
        return render_template('index.html',invalid_cred=invalid_cred)

    elif request.method == 'POST':
        invalid_cred = False
        pass1 = request.form['pass_to_encrypt']
        pass2 = request.form['pass_to_encrypt1']

        # verificar se a password é a mesma em ambas as texbox
        if pass1 != pass2:
            return render_template('index.html', valid=False)

        elif pass1 == pass2:
            pass_to_encrypt = pass1
            return redirect(url_for("login"))


@app.route('/login', methods=['POST', 'GET'])                                                                 
def login():                 
    global password, email, dns, is_valid, first, redirect_site, pass_to_encrypt, token, invalid_cred

    if request.method == 'GET':

        # fazer autocomplete com as credenciais de credencials.txt
        content, empty = enc.decrypt("credentials.txt", pass_to_encrypt)

        if not content and not empty:
            invalid_cred = True
            return redirect(url_for("index"))


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
    

    elif request.method == 'POST':

        email =  request.form['email']
        password = request.form['pass']
                
        # é enviado apenas o mail para a app
        data = {'email': hashlib.md5(email.encode()).hexdigest() }
        data = json.dumps(data)

        res = session.post('http://172.2.0.3:5001/uap', json=data)

        # caso a resposta do POST for "", siginifica que as credenciais colocadas não existem
        if res.text == "":
            is_valid = False
            return redirect(url_for('login'))

        session.post('http://localhost:5002/protocol', json=json.dumps(res.text))

        if redirect_site:
            # fazer um post com um token e o email
            data = {'token_uap':token}

            res = session.post(url="http://172.2.0.2/", data={'token_uap':token})

            return redirect("http://172.2.0.2?token=%s" % token)

        return redirect(url_for('login'))


@app.route('/authentication', methods=['POST', 'GET'])                                                                 
def authentication():
    global is_valid, email, password, dns, valid, first, challenge, response, redirect_site, pass_to_encrypt
    
    # se a uap estiver válida para o server (is_valid) e se o server estiver válido para a uap (valid)
    
    if is_valid and valid:

        exist = False

        content, empty = enc.decrypt("credentials.txt", pass_to_encrypt)

        open("credentials.txt", "r+").close() # apagar dados do ficheiro

        # atualizar o conteúdo de credentials.txt 
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

        # encriptar o ficheiro com o conteúdo atualizado
        enc.encrypt(str(content), "credentials.txt", pass_to_encrypt)
        
        reset_variables()
        redirect_site = True
        return "redirecting to the website..."
        
    else:
        reset_variables()
        is_valid = False
        redirect_site = False    

        return redirect(url_for('login'))


@app.route('/protocol', methods=['POST', 'GET'])                                                                 
def challenge_response():
    global first, valid, is_valid, response, challenge, token

    # a uap vai deixar de ter o echap current e chega a uma altura em que vai receber a resposta do server a dizer se é valid ou não

    if not valid:
        data = request.get_json(force=True) 
        data = json.loads(data)
        
        random_response_to_challenge_received = random_response()   # resposta random
        random_response_to_challenge_received = ("".join(f"{ord(i):08b}" for i in random_response_to_challenge_received))[:2]
        
        create_challenge()
        
        payload = {'response': random_response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        res = session.post('http://172.2.0.3:5001/protocol', json=data)

        data = json.loads(res.text)

        if 'valid' in data:
            is_valid = data['valid']
            return redirect(url_for('authentication'))

        session.post('http://localhost:5002/protocol', json=json.dumps(res.text))
        
        return "ok"

    if first:
        first = False
        data = request.get_json(force=True)
        data = json.loads(json.loads(data))


        # recebido
        challenge_received = data['challenge']
        response_to_challenge_received = get_response(challenge_received, None)
        response_to_challenge_received = ("".join(f"{ord(i):08b}" for i in response_to_challenge_received))[:2]

        create_challenge()
        response = get_response(challenge_received, challenge)

        payload = {'response':  response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        res = session.post('http://172.2.0.3:5001/protocol', json=data)

        session.post('http://localhost:5002/protocol', json=json.dumps(res.text))

        return "ok"
        
    else:
        data = request.get_json(force=True)
        data = json.loads(data)
        data = json.loads(data)

        challenge_received = data['new_challenge']
        response_to_challenge_received = get_response(challenge, challenge_received)      # resposta ao challenge que recebemos
        response_to_challenge_received = ("".join(f"{ord(i):08b}" for i in response_to_challenge_received))[:2]

        data_received = data['response']
        valid = verify_response(response, data_received)
        
        create_challenge()
        response = get_response(challenge_received, challenge)

        payload = {'response': response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        res = session.post('http://172.2.0.3:5001/protocol', json=data)

        data = json.loads(res.text)

        if 'valid' in data:
            is_valid = data['valid']
            if 'token' in data:
                token = data['token']
            return redirect(url_for('authentication'))

        session.post('http://localhost:5002/protocol', json=json.dumps(res.text))

        return "ok"
        # data deve ser um dicionário do tipo challenge: 1 | response: 9 | is_first: true/false ...


# manda os dados com o redirect do /uap
@app.route('/dns', methods=['POST'])                                                                 
def receive_dns():
    global dns

    dns = request.form.get('dns')
    # redirect para o "/"
    return redirect(url_for('index'))





def reset_variables():
    global challenge, response, first, valid, is_valid, password, email
    response = None
    first = True        
    valid = True        
    password = None
    email = None


def verify_response(response, data_received):

    response = ("".join(f"{ord(i):08b}" for i in response))[:2]

    if response == data_received:
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
