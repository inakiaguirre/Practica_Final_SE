# --------------------------------------------------------------
#    SERVICIO WEB CON FLASK 
#    
#     Starting code para Laboratorio 3
# --------------------------------------------------------------
#   @Laura Arjona
#  @Sistemas Embebidos. 2021
# -----------------------------------
from flask import Flask, render_template, request
from flask import request, redirect
from flask_socketio import SocketIO as socketio
import json
import random
from os import system
import os
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from flask_mqtt import Mqtt


app = Flask(__name__)
app = Flask(__name__, template_folder='./templates')
app.config['TEMPLATES_AUTO_RELOAD'] = True

#Direccion del broker
#El hostname es la direccion IP del broker
#Si el broker esta en la misma maquina que ejecuta este scritp, 
#se puede usar local host como IP. Recordad localhost = 127.0.0.1
app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False


mqtt = Mqtt(app)
socketio = socketio(app)

#Definir el hostname
hostname = 'localhost'

TEMPERATURA1 = 0
HUMEDAD1 = 0

# http://127.0.0.1:5000/home       
@app.route("/home")
def home():
    return render_template('home.html')
#_________________________________________________________________________________

#Topics Subscriptor
topic_sub1 = "dht11/m1"
topic_sub2 = "mState/m1"
topic_sub3 = "cpu_temp/m1"

#Topic Publicador
topic_pub1 = "mAction/m1"

#Subscrimos al topic al inicio del programa.
mqtt.subscribe(topic_sub1)
mqtt.subscribe(topic_sub2)
mqtt.subscribe(topic_sub3)

#_________________________________________________________________________________

# Callback que se llama cuando el cliente recibe el CONNACK del servidor 
#Restult code 0 significa conexion sin errores
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# Callback que se llama "automaticamente" cuando se recibe un mensaje del Publiser.
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):

    global TEMPERATURA1
    global HUMEDAD1

    data = dict(
        topic = message.topic,
        payload = message.payload.decode("utf-8")
    )
    #print("topic:  "+ message.topic)

    if message.topic == topic_sub1:
        rec_values =message.payload.decode("utf-8")
        print("Sensor: " + str(rec_values))

        mensaje_recibido_json =json.loads(data['payload'])
        
        TEMPERATURA1 = mensaje_recibido_json["temp"]
        HUMEDAD1 = mensaje_recibido_json["humi"]

        # Envio los valores medianto socket io
        socketio.emit('TEMPERATURA1', data = data)
        socketio.emit('HUMEDAD1', data = data)

    elif message.topic == topic_sub2:
        estado = message.payload.decode("utf-8")
        print("Estado: " + str(estado))

    elif message.topic == topic_sub3:
        mensaje_recibido_json = json.loads(data["payload"])
        TEMP1 = mensaje_recibido_json["temp1"]
        print("Temperatura CPU: " + str(TEMP1))
        # Envio los valores medianto socket io
        socketio.emit('mqtt_temp_cpu', data = data)

#_________________________________________________________________________________

# Dirección "home" -- registro de usuario
# http://0.0.0.0:5000/

@app.route("/", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        req = request.form
        username = req.get("username")
        password = req.get("password")

        missing = list()

        for k, v in req.items():
            if v == "":
                missing.append(k)

        if missing:
            feedback = f"Missing fields for {', '.join(missing)}"
            return render_template("login.html", feedback=feedback)
        
        if username == "ij" and password == "1":
            #REDIRECCIONAMOS a la página del menu
            return render_template('home.html', temp1 = TEMPERATURA1, hum1 = HUMEDAD1)
        else:
            #REDIRECCIONAMOS A LA route de home (/)
            return redirect(f"/")

    return render_template("login.html")

#_________________________________________________________________________________
# Resto de rutas
# http://127.0.0.1:5000/home/m1

@app.route("/home/<device>", methods = ['GET', 'POST'])
def botonMaquinas(device):

    global TEMP1

    if device == 'm1':
        return render_template('m1.html', temp1 = TEMP1)
    
#_________________________________________________________________________________

@app.route("/home/<device>/<action>")
def botones(device, action):

    if device == 'home':
        
        if action == 'actualizar':
        
            mensaje2 = {
                'action': action
            }
            #Convertimos el mensaje en tipo JSON
            mensaje2_json= json.dumps(mensaje2)
            print(mensaje2_json)
            #Publicamos los valores por MQTT, para que los reciva el servidor FLASK
            publish.single(topic_pub1, mensaje2_json, hostname=hostname)
            return render_template('m1.html', estado = "Encendido", temp1 = TEMP1)

        if action == 'apagar':
            mensaje2 = {
                'action': action
            }
            #Convertimos el mensaje en tipo JSON
            mensaje2_json= json.dumps(mensaje2)
            print(mensaje2_json)
            #Publicamos los valores por MQTT, para que los reciva el servidor FLASK
            publish.single(topic_pub1, mensaje2_json, hostname=hostname)
            return render_template('m1.html', estado = "Apagado", temp1 = TEMP1)

        
        if action == 'index':
            return render_template('index.html', temp1 = TEMPERATURA1, hum1 = HUMEDAD1 )

    return render_template('m1.html', temp1 = TEMP1)
    
    
#_________________________________________________________________________________

if __name__ == "__main__":
   socketio.run(app, host='0.0.0.0', port=5000, debug=True)
   
 