# --------------------------------------------------------------
#    SERVICIO WEB CON FLASK + MQTT + SOCKET-IO
#
#    Ejemplo para realizar para Laboratorio 3. Parte 2

# Ejemplo de uso de librerías flask_mqtt y  flask_socketio
# --------------------------------------------------------------
#   @Laura Arjona
#  @Sistemas Embebidos. 2021
# -----------------------------------

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

import json
import time
import time
import dht_config
from gpiozero import CPUTemperature

import RPi.GPIO as GPIO
GPIO.setwarnings(False)

# Definimos que va a ser de tipo BCM.
GPIO.setmode(GPIO.BCM)

# Definimos los pines de entrada de los dispositivos. 
pin_sensor = 16 
pin_luz = 18
pin_boton = 19

# Definimos de que tipo son los dispositivos. 
GPIO.setup(pin_luz, GPIO.OUT)
GPIO.setup(pin_boton, GPIO.IN)


# Direccion del broker.
hostname = 'localhost'

# Definimos los topics para MQTT

# Topics que publicamos.
tp_temp_hum = "t_temp_hum"
tp_maquina = "t_maquina"
tp_cpu = "t_cpu"

# Topics que nos subscribimos.
ts_on_off = "t_on_off"


# Callback que se llama cuando el cliente recibe el CONNACK del servidor
# Restult code 0 significa conexion sin errores
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Nos subscribirmos al topic
    client.subscribe(ts_on_off)

# Callback que se llama "automaticamente" cuando se recibe un mensaje del Publiser.
def on_message(client, userdata, message):
    rec_values = message.payload.decode("utf-8")
    rec_values_json = json.loads(rec_values)

    if message.topic == ts_on_off:
        if rec_values_json["estadoLed"] == 'encender':
            GPIO.output(pin_luz, 1)

        elif rec_values_json["estadoLed"] == 'apagar':
            GPIO.output(pin_luz, 0)


# Creamos un cliente MQTT
client = mqtt.Client()

# Definimos los callbacks para conectarnos y subscribirnos al topic
client.on_connect = on_connect
client.on_message = on_message

# Conectamos al hosntame que se debe definir arriva
client.connect(hostname, 1883, 60)

# Inicialmos el loop de la siguiente manera:
client.loop_start()


def changeLed(channel):

    inputValue = GPIO.input(pin_luz)

    #Cambiamos el estado del Led. 
    if inputValue == 1:
        GPIO.output(pin_luz, 0)
        inputValue = "Maquina Apagada"
    else:
        GPIO.output(pin_luz, 1)
        inputValue = "Maquina Encendida"

    mensaje_estado_led = {
        'estadoBoton': inputValue
    }

    # Convertimos el mensaje en tipo JSON
    men_json_maquina = json.dumps(mensaje_estado_led)
    # Publicamos el mensaje con el topic correspondiente.
    publish.single(tp_maquina, men_json_maquina, hostname=hostname)

# Evento que se activa cuando se acciona el boton. 
GPIO.add_event_detect(pin_boton, GPIO.RISING, callback = changeLed, bouncetime = 200)

# -----------------------------------------------
while True:
    # Declaramos el sensor, para acceder a sus funciones. 
    sensor = dht_config.DHT(pin_sensor)
    # Obtenemos el valores de la humedad y la temperatura y lo guardamos en dos variables. 
    humi, temp = sensor.read()  

    # Creamos un diccionario con el valor de la humedad y temperatura.
    mensaje_temp_humi = {
        "humi": humi,
        "temp": temp,
    }

    # Creamos un diccionario con la temperatura de la CPU. 
    mensaje_temp_CPU = {
        "temCPU": CPUTemperature().temperature
    }

    # Convertimos los mensaje en tipo JSON
    mensaje_json_temp_humi = json.dumps(mensaje_temp_humi)
    
    mensaje_json_temp_CPU = json.dumps(mensaje_temp_CPU)

    # Publicamos los valores por MQTT, los dos a la vez en una misma publicacion. 
    publish.multiple([[tp_temp_hum, mensaje_json_temp_humi], [tp_cpu, mensaje_json_temp_CPU]], hostname=hostname)

    # Paramos el bucle cada 3 segundos. EL envio de datos se hace cada x tiempo. 
    time.sleep(3)
