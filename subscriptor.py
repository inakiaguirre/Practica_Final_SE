from re import template
import eventlet
import json
from flask import Flask, render_template, request
from flask import request, redirect
from flask_mqtt import Mqtt
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from flask_socketio import SocketIO, send
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

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

# Direccion del broker.
hostname = 'localhost'

# http://127.0.0.1:5000/home
@app.route("/home")
def home():
    return render_template('home.html')

#_________________________________________________________________

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
        
        if username == "ij" and password == "1":
            #REDIRECCIONAMOS a la página del menu
            return redirect(f"/home")
        else:
            #REDIRECCIONAMOS A LA route de home (/)
            return redirect(f"/")

    return render_template("sign_up.html")
#_________________________________________________________________

@socketio.on('message')
def handleMessage(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True)

# Definimos los topics para MQTT
# Topics que nos subscribimos.
ts_temp_hum = "t_temp_hum"
ts_lumi = "t_lumi"
ts_servo = "t_servo"
ts_luz = "t_luz"

# Nos subscribimos al topic.
mqtt.subscribe(ts_temp_hum)
mqtt.subscribe(ts_lumi)
mqtt.subscribe(ts_servo)
mqtt.subscribe(ts_luz)

#_________________________________________________________________

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

#_________________________________________________________________

@mqtt.on_message()
def recibirMensajes(client, userdata, message):

    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
        )

    rec_values = message.payload.decode("utf-8")
    mensaje_recibido_json = json.loads(rec_values)

    # En caso de que el topic sea "t_temp_hum".

    if message.topic == "t_temp_hum":

        humi = mensaje_recibido_json["humi"]
        temp = mensaje_recibido_json["temp"]

        socketio.emit('mqtt_message_example', data=data)

    # En caso de que el topic sea "t_lumi".

    elif message.topic == "t_lumi":
        
        lumi = mensaje_recibido_json["lumi"]

        socketio.emit('mqtt_message_temperatura_cpu', data=lumi)

    # En caso de que el topic sea "t_servo".

    elif message.topic == "t_servo":
        servo = mensaje_recibido_json["servo"]
        socketio.emit('mqtt_message_estado', data=servo)

#_________________________________________________________________

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
