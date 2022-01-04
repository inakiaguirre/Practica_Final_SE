#@Laura Arjona
#@Sistemas Embebidos. 2021


#Ejemplo de uso del sensor DHT111
#Se ayuda del módulo dht_config.py
#  donde realmente se hace la lectura
#de los datos del sensor, teniendo en cuenta las estrictas restricciones temporales 
#https://files.seeedstudio.com/wiki/Grove-TemperatureAndHumidity_Sensor/res/DHT11.pdf


import time
import dht_config
import RPi.GPIO as GPIO

def main():
     
    GPIO.setmode(GPIO.BCM) #numeración de pines basada en números GPIOs

    gpio_pin_sensor = 16 #GPIO 16   conectamos el pin SIG del sensor
    sensor = dht_config.DHT(gpio_pin_sensor) #Pasar por argumento el número del GPIO
    
    while True:
        humi, temp = sensor.read()
        print('Humedad {0:.1f}%, Temperatura {1:.1f}'.format( humi, temp))
   
        time.sleep(1)
 
if __name__ == '__main__':
    main()