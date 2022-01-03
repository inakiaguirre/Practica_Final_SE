# --------------------------------------------------------------
#    SERVICIO WEB CON FLASK + MQTT + SOCKET-IO
#
#    Ejemplo para realizar para Laboratorio 3. Parte 2

# Ejemplo de uso de librerías flask_mqtt y  flask_socketio
# --------------------------------------------------------------


import eventlet
import json
from flask import Flask, render_template, request
from flask import request, redirect
from flask_mqtt import Mqtt
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from flask_socketio import SocketIO, send
import random
from gpiozero import CPUTemperature

import RPi.GPIO as GPIO
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

LUZ = 18
BOTON_MARCHA_PARO = 19

GPIO.setup(LUZ, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(BOTON_MARCHA_PARO, GPIO.IN)

eventlet.monkey_patch()
app = Flask(__name__)
app = Flask(__name__, template_folder='./templates')


app.config['TEMPLATES_AUTO_RELOAD'] = True
# Direccion del broker
# El hostname es la direccion IP del broker
# Si el broker esta en la misma maquina que ejecuta este scritp,
# se puede usar local host como IP. Recordad localhost = 127.0.0.1
app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
app.config['SECRET_KEY'] = 'secret'

mqtt = Mqtt(app)
socketio = SocketIO(app)


@socketio.on('message')
def handleMessage(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True)


# Direccion del broker.
hostname = 'localhost'

# Definimos los topics para MQTT

# Topics que publicamos.
tp_on_off = "t_on_off"
# Topics que nos subscribimos.
ts_temp_hum = "t_temp_hum"
ts_maquina = "t_maquina"
ts_cpu = "t_cpu"

# Nos subscribimos al topic.
mqtt.subscribe(ts_temp_hum)
mqtt.subscribe(ts_maquina)
mqtt.subscribe(ts_cpu)


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("Conectado, ready to rock :D ")


# --------------------------------------------------------------
#  Dirección "home" -- registro de usuario
# http://0.0.0.1:5000/
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
            return render_template("sign_up.html", feedback=feedback)

        if username == "iker":
            # REDIRECCIONAMOS a la página del menu
            return redirect(f"/home")
        else:
            # REDIRECCIONAMOS A LA route de home (/)
            return redirect(f"/")

    return render_template("sign_up.html")
# --------------------------------------------------------------

# http://127.0.0.1:5000/home

@app.route("/home")
def home():
    return render_template('home.html')
# ------------------------------------------------------------

# http://127.0.0.1:5000/<maquina>
@app.route("/home/<maquina>")
def m1(maquina):
    estado = 'Maquina Apagada'
    return render_template('m.html', maquina=maquina, estado=estado)

# -----------------------------------------------

# ruta ejemplo: direccion_IP_flask:5000/home/log_ejemplo
# @app.route("/home/<maquina>/<cualquier_cosa>")

def mSelect(maquina):
    templateData = {
        'maquina': maquina
        }
    return render_template('log_example.html', **templateData)

# ------------------------------------------------------------
# @app.route("/home/<device>/<action>")

def estadoMaquina(maquina, encenderApagar):

    mensaje_estado_led = {
        "estadoLed": encenderApagar
    }

    mensaje_json_estado_led = json.dumps(mensaje_estado_led)
    publish.single(tp_on_off, mensaje_json_estado_led ,hostname=hostname)

    if encenderApagar == "encender":
        estado = 'Maquina Encendida'
        return render_template('m.html', maquina=maquina, estado=estado)
    elif encenderApagar == "apagar":
        estado = 'Maquina Apagada'
        return render_template('m.html', maquina=maquina,  estado=estado)

@app.route("/home/<maquina>/<action>")
def checkRoute(maquina, action):
    if action == "encender" or action == "apagar":
        return estadoMaquina(maquina, action)
    elif action == "log-ejemplo":
        return mSelect(maquina)
    else:
        return render_template('404.html')


# -------------------------------------------------------------------
# Función que se ejecuta automáticamente (recordar los callbacks) cuando se recibe un mensaje por MQTT
# -------------------------------------------------------------------
@mqtt.on_message()

def recibirMensajes(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode())

    rec_values = message.payload.decode("utf-8")
    mensaje_recibido_json = json.loads(rec_values)

    # En caso de que el topic sea "t_temp_hum".

    if message.topic == "t_temp_hum":

        humi = mensaje_recibido_json["humi"]
        temp = mensaje_recibido_json["temp"]

        socketio.emit('mqtt_message_example', data=data)

        if ecuacion(humi, temp) > 0.6:
            GPIO.output(LUZ, 0)
            socketio.emit('mqtt_message_estado', data="Maquina Apagada")

    # En caso de que el topic sea "t_cpu".

    elif message.topic == "t_cpu":
        
        tempCPU = mensaje_recibido_json["temCPU"]

        socketio.emit('mqtt_message_temperatura_cpu', data=tempCPU)

    # En caso de que el topic sea "t_maquina".

    elif message.topic == "t_maquina":
        estado = mensaje_recibido_json["estadoBoton"]
        socketio.emit('mqtt_message_estado', data=estado)


def ecuacion(humi, temp):

    resultado = 0.07 * temp + 0.03 * humi

    return resultado


# export FLASK_APP=flaskqt
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
