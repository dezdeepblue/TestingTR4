from machine import Pin
import utime
from usr.led import LED
from usr.buzzer import Buzzer

TouchLED = LED(Pin.GPIO18, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)
B3_LED   = LED(Pin.GPIO3, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)
B2_LED   = LED(Pin.GPIO4, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)
B1_LED   = LED(Pin.GPIO2, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)
B0_LED   = LED(Pin.GPIO1, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)
Band_LED = LED(Pin.GPIO19, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)
Charger_LED = LED(Pin.GPIO9, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0) 
Vibre = Buzzer(Pin.GPIO23, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0)


run = True
if __name__ == "__main__":
        Vibre.start_flicker(100,100,3)
        # TouchLED.start_flicker(1000,1000,20)
        # B3_LED.start_flicker(1000,1000,20)
        # B2_LED.start_flicker(1000,1000,20)  
        # B1_LED.start_flicker(1000,1000,20)
        # B0_LED.start_flicker(1000,1000,20)
        Band_LED.start_flicker(1000,1000,20)
        # Charger_LED.start_flicker(1000,1000,20)
