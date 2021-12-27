import json
import flask
from flask.app import Flask
from flask.json import jsonify                   
import requests               
from urllib.parse import urlencode
from Crypto import Random
from hashlib import sha256

from flask import request   
                                
import mysql.connector


app = Flask(__name__)  

conn = mysql.connector.connect(user='admin', password='admin',
                              host='localhost',  # name container
                              database='spoton')   

ECHAP_CURRENT = 0
ECHAP_MAX = 50

challenge = None

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

@app.route('/protocol', methods=['POST', 'GET'])                                                                 
def challenge_response():

    data = request.get_json(force=True) 
    data = json.loads(data)
    # data deve ser um dicionário do tipo challenge: 1 | response: 9 | is_first: true/false ...

    pass

def create_challenge():
    challenge = Random.random.choice(100000)
    return challenge

def get_response(challenge):

    response = sha256(challenge.encode('utf-8')).hexdigest()
    return response


# retornar o DNS do server para a UAP saber | "http://127.0.0.1:5000/uap"
@app.route('/uap', methods=['POST', 'GET'])                                                                 
def redirect_uap():    

    if request.method == 'POST':   
        input_json = request.get_json(force=True) 
        mail = input_json["mail"]
        
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM users WHERE email='{mail}'")

        data = cursor.fetchone()
        cursor.close()
        
        print("SQL QUERY FOUND:", data)
        return "porto"
    
    else:
        return "cornisse"    
    
if __name__ == '__main__':                                                    
    app.run(host='127.0.0.1',port=5000 )