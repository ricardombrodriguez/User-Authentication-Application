# TODO
# (DONE) - Já conseguimos comunicar entre o server e a UAP, por isso no inicio, quando o user clica no login, este vai correr o server.py no endpoint /dns e temos de enviar uma mensagem para a UAP com o DNS (aka o ip do site para ele depois poder saber onde é que queremos fazer a autenticação). Além deste request temos de fazer o redirect para a página da uap
# - Na página da uap, procuramos se já existem credenciais para esse website (dns). Existe -> Completar os inputs do formulário com as credenciais para esse website. Não existe -> Esperar que o user coloque as credenciais
# - Quando o user coloca as credenciais para esse website, temos de guardar na base de dados (o ficheiro json tem de estar encriptado!)
# - Quando o user clica no login, o email é enviado para o server
# - O server procura na sua base de dados se existe algum user com esse email e guarda a password. Caso não exista nenhum user, não dizemos ao utilizador que não existe porque isso é uma vulnerabilidade
# - A partir de agora, começa o protocolo:
# - O server começa a mandar o 1º challenge e calcula a resposta válida para esse challenge.
# - A UAP recebe o 1º challenge, calcula a 1º resposta e depois manda-a para o server. Ao mesmo tempo, envia o 2º challenge para o server.
# - O server recebe a resposta do 1º challenge e recebe o 2º challenge da uap. Ele verifica se a resposta do 1º challenge recebida pela UAP é igual à que ele calculou para verificar a autenticidade.
# - Agora, é a vez de o server calcular a resposta do 2º challenge enviado pela uap para depois a uap verificar se está tudo bem
# - Caso o server ou a uap receber uma resposta inválida, estes continuam a mandar challenge e respostas, mas desta vez com challenges diferentes do suposto para confundir o atacante.
# - Isto vai continuar N vezes por causa do E-CHAP
# - No final, caso o server perceber que o user é valido, este envia uma mensagem HTTP 200 (maybe) para dizer que o user pode prosseguir



from hashlib import sha256
from random import SystemRandom
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template     
import secrets                                     
from flask import redirect, url_for

import json, os

import requests   

app = Flask(__name__)

dns = None
ECHAP_CURRENT = 0
ECHAP_MAX = 10
challenge = None    # challenge criado pelo server
response = None     # resposta para o challenge criado pelo server
first = True        
valid = True        # o user que estamos a autenticar é valido ou não
password = "seguranca"

@app.route('/', methods=['POST', 'GET'])                                                                 
def index():                 

    #receber o dns

    # login
    if request.method == 'POST':
        print("post")
        mail = request.form['email']
        password = request.form['pass']

        # guardar credenciais no ficheiro json
        
        # é enviado apenas o mail para a app
        data = {'email': mail}
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



@app.route('/protocol', methods=['POST', 'GET'])                                                                 
def challenge_response():
    global first, valid, response, challenge, ECHAP_CURRENT, ECHAP_MAX

    ECHAP_CURRENT += 1

    if ECHAP_CURRENT == ECHAP_MAX:
        print("[UAP] VALID: " + valid)
        return redirect(url_for('/authentication'))

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

        payload = {'challenge': challenge_received, 'response': response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        print("[UAP] Iteração número " + str(ECHAP_CURRENT) + ":")
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

        payload = {'challenge': challenge_received, 'response': response_to_challenge_received, 'new_challenge': challenge }
        data = json.dumps(payload)

        print("[UAP] Iteração número " + str(ECHAP_CURRENT) + ":")
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

    """ print("===")
    print(received_challenge)
    print(password)
    print(mychallenge)
    print("===") """

    if not mychallenge:
        mychallenge = ""

    response = sha256((received_challenge+password+mychallenge).encode('utf-8')).hexdigest()
    return response



if __name__ == '__main__':                                                      
    app.run(host='127.0.0.1',port=5001)
