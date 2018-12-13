#!flask/bin/python
from flask import Flask
import json

app = Flask(__name__)

from flask import Flask
from flask import request
from flask_cors import CORS
from flask import render_template

CORS(app)

from clausiverificacio import Punt
import clausiverificacio as cv

class Usuari:
    def __init__(self, name, clauPrivada):
        self.name = name
        self.clauPrivada = clauPrivada
        self.clauPublica = cv.GeneraClauPublica(clauPrivada)

registres = []

usuaris = {}


@app.route('/', methods=['GET'])
def mainGet():
    return render_template('index.html')

@app.route('/document', methods=['GET'])
def documentGet():
    return render_template('document.html')

@app.route('/registres', methods=['GET'])
def registresGet():
    return json.dumps(registres, indent=4, sort_keys=True)

@app.route('/registre', methods=['GET'])
def registreGet():
    if request.args.get('emisor') and request.args.get('receptor') and request.args.get('amount'):
        emisor = request.args.get('emisor')
        receptor = request.args.get('receptor')
        amount = request.args.get('amount')
        if (emisor in usuaris and receptor in usuaris):
            reg = "04" + str(hex(usuaris[emisor].clauPublica.x)[2:]).zfill(64)+ str(hex(usuaris[emisor].clauPublica.y)[2:]).zfill(64)+":04"+str(hex(usuaris[receptor].clauPublica.x)[2:]).zfill(64)+str(hex(usuaris[receptor].clauPublica.y)[2:]).zfill(64)+":"+str(hex(int(amount)))[2:].zfill(30)
            registres.append(reg)
            return "1"
    return "0"

@app.route('/login', methods=['GET'])
def loginGet():
    content = request.get_json()
    name = request.args.get('name')
    if name in usuaris:
        return json.dumps([usuaris[name].clauPrivada, usuaris[name].clauPublica.x])
    else:
        usuaris[name] = Usuari(name, len(usuaris)+1)
        return json.dumps([usuaris[name].clauPrivada, usuaris[name].clauPublica.x])

@app.route('/quantitat', methods=['GET'])
def quantitatGet():
    name = request.args.get('name')
    count = 0
    if name in usuaris:
        usuari = usuaris[name]
        clauPublica = "04" + str(hex(usuari.clauPublica.x)[2:]).zfill(64) + str(hex(usuari.clauPublica.y)[2:]).zfill(64)
        for reg in registres:
            spl = reg.split(":")
            if (spl[0] == clauPublica):
                count -= int(spl[2], 16)
            if (spl[1] == clauPublica):
                count += int(spl[2], 16)
    return str(count)

@app.route('/usuaris', methods=['GET'])
def usuarisGet():
    users = []
    for u in usuaris:
        users.append(u)
    return json.dumps(users)

@app.route('/claupublica', methods=['GET'])
def claupublicaGet():
    if request.args.get('name'):
        name = request.args.get('name')
        if name in usuaris:
            return str(usuaris[name].clauPublica.x)
    return "0"

app.run(host='127.0.0.1', port=5000)
