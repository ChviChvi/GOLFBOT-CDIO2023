from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.led import Leds

# Create a MoveTank instance
tank = MoveTank(OUTPUT_B, OUTPUT_C)

# Turn on the motors at speed 50
tank.on(50, 50)

# Stop the motors
tank.off()

# Change the color of the LEDs
leds = Leds()
leds.set_color("LEFT", "GREEN")

