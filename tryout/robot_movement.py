from ev3dev.ev3 import *

class RobotMovement:
    def __init__(self):
        # Initialize the motors.
        self.left_motor = LargeMotor('outB')  # Change 'outB' and 'outC' to the ports your motors are connected to
        self.right_motor = LargeMotor('outC')

    def move_forward(self, speed, time):
        self.left_motor.run_timed(time_sp=time, speed_sp=speed)
        self.right_motor.run_timed(time_sp=time, speed_sp=speed)
        wait(time)

    def move_backward(self, speed, time):
        self.left_motor.run_timed(time_sp=time, speed_sp=-speed)
        self.right_motor.run_timed(time_sp=time, speed_sp=-speed)
        wait(time)

    def turn_left(self, speed, time):
        self.left_motor.run_timed(time_sp=time, speed_sp=-speed)
        self.right_motor.run_timed(time_sp=time, speed_sp=speed)
        wait(time)

    def turn_right(self, speed, time):
        self.left_motor.run_timed(time_sp=time, speed_sp=speed)
        self.right_motor.run_timed(time_sp=time, speed_sp=-speed)
        wait(time)

    def turn_around(self, speed, time):
        self.left_motor.run_timed(time_sp=time, speed_sp=speed)
        self.right_motor.run_timed(time_sp=time, speed_sp=-speed)
        wait(time)


# #!/usr/bin/env pybricks-micropython
# from pybricks.hubs import EV3Brick
# from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, InfraredSensor, UltrasonicSensor, GyroSensor)
# from pybricks.parameters import Port, Stop, Direction, Button, Color
# from pybricks.tools import wait, StopWatch, DataLog
# from pybricks.robotics import DriveBase
# from pybricks.media.ev3dev import SoundFile, ImageFile

# class RobotMovement:
#     def __init__(self):
#         # Create your objects here.
#         self.ev3 = EV3Brick()

#         # Initialize the motors.
#         self.left_motor = Motor(Port.B)
#         self.right_motor = Motor(Port.C)

#     # Define movement functions.
#     def move_forward(self, speed, time):
#         self.left_motor.run(speed)
#         self.right_motor.run(speed)
#         wait(time)

#     def move_backward(self, speed, time):
#         self.left_motor.run(-speed)
#         self.right_motor.run(-speed)
#         wait(time)

#     def turn_left(self, speed, time):
#         self.left_motor.run(-speed)
#         self.right_motor.run(speed)
#         wait(time)

#     def turn_right(self, speed, time):
#         self.left_motor.run(speed)
#         self.right_motor.run(-speed)
#         wait(time)

#     def turn_around(self, speed, time):
#         self.left_motor.run(speed)
#         self.right_motor.run(-speed)
#         wait(time)
