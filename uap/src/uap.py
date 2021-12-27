from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template                                                   
import requests                                                  

app = Flask(__name__)        

@app.route('/')                                                                 
def index():                          
    if request.method == 'POST':
        pass
    return render_template('index.html') 

# manda os dados com o redirect do /uap
@app.route('/dns', methods=['GET'])                                                                 
def send_dns():          
    input_json = request.get_json(force=True) 
    print('data: ', input_json)
    dictToReturn = {'answer':42}
    return jsonify(dictToReturn)

if __name__ == '__main__':                                                      
    app.run(host='127.0.0.1',port=5001)
