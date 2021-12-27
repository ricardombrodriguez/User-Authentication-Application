import json
import flask
from flask.app import Flask
from flask.json import jsonify                   
import requests               

from flask import request                                   

app = Flask(__name__)      

app_dns = 'http://127.0.0.1:5001'

# retornar o DNS do server para a UAP saber | "http://127.0.0.1:5000/uap"
@app.route('/uap', methods=['POST', 'GET'])                                                                 
def redirect_uap():   
    input_json = request.get_json(force=True) 
    print('data: ', input_json)
    
    """ data =  {'dns':app_dns}
    res = requests.post('http://127.0.0.1:5001/dns',json=data)
    print ('response from server:',res.text)
    dictFromServer = res.json()
    return flask.redirect("http://127.0.0.1:5001/dns", code=302 """
    return "porto"

if __name__ == '__main__':                                                    
    app.run(host='127.0.0.1',port=5000 )