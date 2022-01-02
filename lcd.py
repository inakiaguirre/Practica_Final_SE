import time
import smbus
import RPi.GPIO as GPIO
import os

class LCD_DISPLAY():

    #La direcion I2C del display se le pasa como argumento
    def __init__(self,DISPLAY_TEXT_ADDR):
        self.i2c_adress = DISPLAY_TEXT_ADDR
        GPIO.setwarnings(False)
        rev = GPIO.RPI_REVISION
        if rev == 2 or rev == 3:
            self.bus = smbus.SMBus(1)
        else:
            self.bus = smbus.SMBus(0)

#------------------------------------------------------------------

    #FUNCIÓN PARA BORRAR CONTENIDO DEL DISPLAY
    def clear_display(self):
        os.system ("cls")

#------------------------------------------------------------------

    def setText(self,text):
        self.bus.write_byte_data(self.i2c_adress,0x80,0x02) # comando CURSOR RETURN
        time.sleep(.05)
        self.bus.write_byte_data(self.i2c_adress,0x80,0x08 | 0x04)# display on, no cursor
        self.bus.write_byte_data(self.i2c_adress,0x80,0x28) # 2 lineas
        time.sleep(.05)
        count = 0
        row = 0
        while len(text) < 32: 
            text += ' ' #Rellenar (anadir al final) con caracter vacio ' ' hasta llegar al tope que admite de 32 caracteres
        for c in text:
            if c == '\n' or count == 16:
                count = 0
                row += 1
                if row == 2:
                    break
                self.bus.write_byte_data(self.i2c_adress,0x80,0xc0) #cambiar a la segunda linea 
                if c == '\n':
                    continue
            count += 1
            character_unicode = ord(c)
            self.bus.write_byte_data(self.i2c_adress,0x40,character_unicode)
