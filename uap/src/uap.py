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
api_dns = None      # guarda o url do servidor/api da aplicação
challenge = None    # challenge criado pelo server
response = None     # resposta para o challenge criado pelo server
valid = True        # se o user que estamos a autenticar é valido ou não
is_valid = None     # variavel controlo para autenticar se user valido ou não
password = None     # guarda password introduzida pelo user
email = None        # guarda email introduzido pelo user
redirect_site = False   # variavel que diz se um user pode ser redirecionado para o website
pass_to_encrypt = None  # password de encriptação/decriptação introduzida
token = None            # token recebido do server
invalid_cred = False    # credenciais inválidas para o website

session = requests.Session()

@app.route('/', methods=['POST', 'GET'])                                                                 
def index(): 
    global pass_to_encrypt,invalid_cred

    if request.method == 'GET':
        return render_template('index.html',invalid_cred=invalid_cred)

    # as credenciais de encriptação / decriptação foram introduzidas
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
    global password, email, dns, is_valid, redirect_site, pass_to_encrypt, token, invalid_cred, api_dns

    if request.method == 'GET':

        # fazer autocomplete com as credenciais de credencials.txt
        content, empty = enc.decrypt("credentials.txt", pass_to_encrypt)

        # se não existe conteúdo decriptado e o ficheiro está vazio
        if not content and not empty:
            # credenciais de encriptação inválidas
            invalid_cred = True
            return redirect(url_for("index"))

        credentials = {}
        if not empty:
            
            # transformar conteúdo numa lista com um dicionário
            content = content.decode("utf-8").replace("\'", "\"")
            content = json.loads(content)

            # caso o DNS esteja no ficheiro de credenciais
            if dns in content[0]:
                # para cada credencial guardada para um DNS
                for cred in content[0][dns]:
                    saved_mail = cred["mail"]
                    saved_pass = cred["pass"]
                    credentials[saved_mail] = saved_pass            # guardar no dicionário o email - password
        
            enc.encrypt(str(content), "credentials.txt", pass_to_encrypt)      # guardar o conteúdo atualizado de forma encriptada no ficheiro de credenciais

        return render_template('login.html', dic_mail=credentials, is_valid=is_valid)
    


    elif request.method == 'POST':

        email =  request.form['email']
        password = request.form['pass']
                
        # é enviado apenas o mail para a app (em hash)
        data = {'email': hashlib.md5(email.encode()).hexdigest() }
        data = json.dumps(data)

        # o email vai ser enviado para o endpoint /uap do server, para este verificar as credenciais para esse email e prosseguir
        res = session.post(api_dns+'/uap', json=data)

        # caso a resposta do POST for "", siginifica que as credenciais colocadas não existem
        if res.text == "":
            is_valid = False
            return redirect(url_for('login'))

        # caso tenha luz verde (não receber o ""), prosseguir com o protocolo
        session.post('http://localhost:5002/protocol', json=json.dumps(res.text))

        # o user já foi validado e vai para o DNS onde queria ser autenticado
        if redirect_site:
            
            # redirectionar o user para o DNS com um parâmetro de token no url
            return redirect(dns+"?token=%s" % token)

        # caso este não tenha sido validado, voltar para o /login
        return redirect(url_for('login'))


@app.route('/authentication', methods=['POST', 'GET'])                                                                 
def authentication():
    global is_valid, email, password, dns, valid, challenge, response, redirect_site, pass_to_encrypt, api_dns
    
    # se a uap estiver válida para o server (is_valid) e se o server estiver válido para a uap (valid)
    
    if is_valid and valid:

        exist = False

        content, empty = enc.decrypt("credentials.txt", pass_to_encrypt)

        open("credentials.txt", "r+").close() # apagar dados do ficheiro do credentials.txt

        # atualizar o conteúdo de credentials.txt 
        if not empty:

            # descodificar conteudo para um dicionário
            content = content.decode("utf-8").replace("\'", "\"")
            content = json.loads(content)

            # novas credenciais introduzidas
            new_cred = {"mail":email, "pass": password}

            # se o DNS já está no ficheiro de credenciais
            if dns in content[0]:

                for cont in content[0][dns]:
                    if cont["mail"] == email and cont["pass"] == password:
                        exist = True        # as novas credenciais já estão guardadas no ficheiro
                
                if not exist:
                    # adicionar novas credenciais ao ficheiro, uma vez que ainda não existem
                    content[0][dns].append(new_cred)

            else:
                # o ficheiro ainda não tinha esse DNS guardado, introduzindo-o com as primeiras credenciais
                content[0][dns] = [new_cred]

        else:
            # o ficheiro estava vazio e preenche-o com o DNS e as primeiras credenciais
            content = [ { dns: [{"mail":email, "pass": password}] } ]

        # encriptar o ficheiro com o conteúdo atualizado
        enc.encrypt(str(content), "credentials.txt", pass_to_encrypt)
        
        reset_variables()   # variáveis globais que tem de ser resetadas depois de cada autenticação
        redirect_site = True
        return "redirecting to the website..."
        
    # estou inválido para o server mas o server está válido para mim
    else:
        # não está válido o user, dar redirect para a página de login outra vez
        reset_variables()
        is_valid = False
        redirect_site = False    

        return redirect(url_for('login'))


@app.route('/protocol', methods=['POST', 'GET'])                                                                 
def challenge_response():
    global valid, is_valid, response, challenge, token, api_dns

    # a uap vai deixar de ter o echap current e chega a uma altura em que vai receber a resposta do server a dizer se é valid ou não

    if not valid:
        # se a autenticação não for válida, o protocolo continua a executar, porém a partir de agora com informação random
        data = request.get_json(force=True) 
        data = json.loads(data)
        
        random_response_to_challenge_received = random_response()   # resposta random
        random_response_to_challenge_received = ("".join(f"{ord(i):08b}" for i in random_response_to_challenge_received))[:2]   
        # transforma a resposta para bits e guarda os primeiros 2 bits
        
        create_challenge()
        
        payload = {'response': random_response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        # os dados vão ser enviados para o endpoint /protocol do server com os dados
        res = session.post(api_dns+'/protocol', json=data)

        data = json.loads(res.text)

        # caso receber uma mensagem json com uma key "valid", siginifica que o protocolo terminou e então será redirecionado para a authentication
        if 'valid' in data:
            is_valid = data['valid']
            return redirect(url_for('authentication'))

        session.post('http://localhost:5002/protocol', json=json.dumps(res.text))
        
        return "ok"

    else:
        data = request.get_json(force=True)
        data = json.loads(json.loads(data))


        if "challenge" in data.keys():
            challenge_received = data['challenge']
            response_to_challenge_received = get_response(challenge_received, None)
            
        elif "new_challenge" in data.keys():
            challenge_received = data['new_challenge']
            response_to_challenge_received = get_response(challenge, challenge_received)      # resposta ao challenge que recebemos

            data_received = data['response']
            valid = verify_response(response, data_received)    # vê se a resposta calculada e recebida são iguais, verificando se o server é válido ou não
        

        response_to_challenge_received = ("".join(f"{ord(i):08b}" for i in response_to_challenge_received))[:2]
        # transformar string da resposta em bits e guardar os dois primeiros
        
        create_challenge()
        response = get_response(challenge_received, challenge)

        payload = {'response': response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        res = session.post(api_dns+'/protocol', json=data)

        data = json.loads(res.text)

        # ao receber um 'valid' no data, quer dizer que obtemos os resultados sobre a nossa validação para o server 
        if 'valid' in data:
            is_valid = data['valid']
            # receber o token produzido pelo server
            if 'token' in data:
                token = data['token']
            return redirect(url_for('authentication'))

        session.post('http://localhost:5002/protocol', json=json.dumps(res.text))

        return "ok"
        # data deve ser um dicionário do tipo challenge: 1 | response: 9 | is_first: true/false ...

# dns -> website | api_dns -> url do backend/api do website (pode ser o mesmo ou não)
@app.route('/dns', methods=['POST'])                                                                 
def receive_dns():
    global dns, api_dns

    dns = request.form.get('dns')
    api_dns = request.form.get('api_dns')
    # redirect para o "/"
    return redirect(url_for('index'))


# as variaveis globais voltam aos seus valores iniciais
def reset_variables():
    global challenge, response, valid, is_valid, password, email
    response = None      
    valid = True        
    password = None
    email = None

# verifica se os primeiros 2 bits da resposta coincidem com os 2 primeiros bits da solução correta
def verify_response(response, data_received):
    response = ("".join(f"{ord(i):08b}" for i in response))[:2]

    if response == data_received: return True
    return False

# cria um novo challenge
def create_challenge():
    global challenge
    challenge = str(secrets.randbelow(1000000))


# calcula a resposta de um challenge
def get_response(received_challenge, mychallenge):
    # misturar challenge com password
    global password

    if not mychallenge: mychallenge = ""

    encrypt_pass = hashlib.md5(password.encode()).hexdigest()
    return sha256((received_challenge+encrypt_pass+mychallenge).encode('utf-8')).hexdigest()

# criar uma reposta random
def random_response():
    return sha256((str(secrets.randbelow(1000000))).encode('utf-8')).hexdigest()


if __name__ == '__main__':                                                      
    app.run(host='127.0.0.1',port=5002,debug=True)
    print("[UAP] Running on 127.0.0.1:5002")
