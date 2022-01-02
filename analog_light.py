import time
from grove.adc import ADC

import RPi.GPIO as GPIO
 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.IN)
GPIO.setup(5, GPIO.OUT, initial=1)

__all__ = ["GroveLightSensor"]

class GroveLightSensor(object):

    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()

    @property
    def light(self):
        value = self.adc.read(self.channel)
        return value

Grove = GroveLightSensor


def main():
    from grove.helper import SlotHelper
    sh = SlotHelper(SlotHelper.ADC)
    pin = sh.argv2pin()

    sensor = GroveLightSensor(pin)

    print('Detectando luz...')
    while True:
        print('Valor de luminosidad en el ambiente: {0}'.format(sensor.light))
        if sensor.light < 600:
            GPIO.output(5, GPIO.HIGH)
            print("Luz encendida")
        elif sensor.light >= 600:
            GPIO.output(5, GPIO.LOW)
            print("Luz apagada")
        
        time.sleep(2)

if __name__ == '__main__':
    main()
