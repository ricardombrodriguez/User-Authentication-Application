import json
import os
from flask.app import Flask
import requests               
from hashlib import sha256
from flask import request, session
import secrets
import mysql.connector
import uuid

from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)

conn = mysql.connector.connect( user='admin', password='admin', host='mysql', port=3306, database='spoton', use_pure=True )   


@app.route('/protocol', methods=['POST', 'GET'])                                                                 
def challenge_response():
    
    # ECHAP_CURRENT: iteração atual do protocolo
    session['ECHAP_CURRENT'] += 1

    # ECHAP_MAX: iteração máxima do protocolo
    ECHAP_MAX = 10

    # final, diz se o user está autenticado ou não
    if session['ECHAP_CURRENT'] == ECHAP_MAX:

        # envia mensagem com o token no caso de ter verificado a validez da uap
        if session['valid']:
            token = str(uuid.uuid4())

            cursor = conn.cursor()
            cursor.execute(f"UPDATE users SET token='{token}' WHERE email='{session['mail']}'")
            conn.commit()

            cursor.execute(f"UPDATE users SET expire_time='{datetime.now() + timedelta(minutes=5)}' WHERE email='{session['mail']}'")
            conn.commit()

        data = {"valid":True, "token": token} if session['valid'] else {"valid":False}

        # reset das variáveis de sessão
        session['ECHAP_CURRENT']  = 0
        session['challenge'] = None    
        session['response'] = None       
        session['valid'] = True        
        session['is_valid'] = True    
        session['password'] = None

        return json.dumps(data)
    
    # se a resposta recebida não é valida continua a mandar challenges e respostas random 
    if not session['valid']:
        data = request.get_json(force=True) 
        data = json.loads(data)

        random_response_to_challenge_received = random_response()   # resposta random
        random_response_to_challenge_received = ("".join(f"{ord(i):08b}" for i in random_response_to_challenge_received))[:2]
        
        create_challenge()
        
        payload = {'response': random_response_to_challenge_received, 'new_challenge': session['challenge'] }
        data = json.dumps(payload)
        
        return data

    #recebe o challenge, resolve-o e cria um novo para enviar
    else:
        data = request.get_json(force=True) 
        data = json.loads(data)

        challenge_received = data['new_challenge']
        response_to_challenge_received = get_response(session['challenge'],challenge_received)    # resposta ao challenge que recebemos
        response_to_challenge_received = ("".join(f"{ord(i):08b}" for i in response_to_challenge_received))[:2]

        data_received = data['response']
        session['valid'] = verify_response(session['response'], data_received)
        
        create_challenge()

        session['response'] = get_response(challenge_received, session['challenge'])
        
        payload = {'response': response_to_challenge_received, 'new_challenge': session['challenge']  }
        data = json.dumps(payload)
        
        return data


@app.route('/uap', methods=['POST', 'GET'])                                                                 
def redirect_uap():    

    # reset das variáveis de sessão
    session['ECHAP_CURRENT'] = 0
    session['challenge'] = None
    session['response'] = None
    session['is_valid'] =  True
    session['password'] = None
    session['valid'] = True
    session['mail'] = None
    session['dns'] = None

    if request.method == 'POST':   

        data = request.get_json(force=True) 
        input_json = json.loads(data)
        session['mail'] = input_json["email"]
        

        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE email='{session['mail']}'")
        data = cursor.fetchone()
        cursor.close()
        
        # no caso de o mail existir na base de dados, guarda a password associada numa variável de sessão
        if data:
            password = data[3]     # atualiza a password
            session['password'] = password
            
            # começa o protocolo: cria um challenge que envia para a uap e resolve-o para comparar com a resposta que irá receber
            session['ECHAP_CURRENT'] += 1
            create_challenge()
            data = {"challenge": session['challenge'] }
            data = json.dumps(data)
            session['response'] = get_response(session['challenge'] , None)

            return data  
        
        return ""


# verifica se os primeiros 2 bits da resposta coincidem com os 2 primeiros bits da solução correta
def verify_response(response, data_received):
    response = ("".join(f"{ord(i):08b}" for i in response))[:2]

    if response == data_received: return True
    return False

# cria um novo challenge
def create_challenge():
    session['challenge']  = str(secrets.randbelow(1000000))

# resolução de um challenge
def get_response(received_challenge, mychallenge):
    if not mychallenge: mychallenge = ""
    return sha256((received_challenge+ session['password']+mychallenge).encode('utf-8')).hexdigest()

# criação de uma resposta random
def random_response():
    return sha256((str(secrets.randbelow(1000000))).encode('utf-8')).hexdigest()
