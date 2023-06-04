#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.


# Create your objects here.
ev3 = EV3Brick()

# Initialize the motors.
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)

# Define movement functions.
def move_forward(speed, time):
    left_motor.run(speed)
    right_motor.run(speed)
    wait(time)

def move_backward(speed, time):
    left_motor.run(-speed)
    right_motor.run(-speed)
    wait(time)

def turn_left(speed, time):
    left_motor.run(-speed)
    right_motor.run(speed)
    wait(time)

def turn_right(speed, time):
    left_motor.run(speed)
    right_motor.run(-speed)
    wait(time)

def turn_around(speed, time):
    left_motor.run(speed)
    right_motor.run(-speed)
    wait(time)

# Call the movement functions.
#move_forward(200, 500)  # Move forward at speed 500 for 2 seconds
#wait(1000)  # Wait for 1 second
#turn_right(500, 1000)  # Turn right at speed 500 for 1 second
turn_around(300,900)
# Write your program here.
#ev3.speaker.beep()
