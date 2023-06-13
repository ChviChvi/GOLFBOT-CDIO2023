from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait
from pybricks.robotics import DriveBase
import math
import time

class Robot:
    def __init__(self):
        self.brick = EV3Brick()
        self.left_motor = Motor(Port.B) # need check
        self.right_motor = Motor(Port.C) # need check
        self.wheel_diameter = 70 # need check
        self.axle_track = 160 # need check
        self.wheels = DriveBase(self.left_motor, self.right_motor, wheel_diameter=self.wheel_diameter, axle_track=self.axle_track)
        self.field_width = 1800 # need check
        self.field_height = 1200 # need check
        self.x = 0 # need to def (based of IR?)
        self.y = 0 # need to def (based of IR?)
        self.angle = 0 # need to def (based of IR?)
        self.left_motor.reset_angle(0) # need to be def
        self.right_motor.reset_angle(0) # need to be def
        self.left_last_angle = 0 # need to be def
        self.right_last_angle = 0 # need to be def

    def move_to_point(self, x, y):
        left_angle = self.left_motor.angle()
        right_angle = self.right_motor.angle()
        left_distance = (left_angle - self.left_last_angle) * self.wheel_diameter * 0.5 / 360
        right_distance = (right_angle - self.right_last_angle) * self.wheel_diameter * 0.5 / 360
        distance = (left_distance + right_distance) * 0.5
        heading = self.angle + degrees((right_distance - left_distance) / self.axle_track)
        self.x += distance * cos(radians(heading))
        self.y += distance * sin(radians(heading))
        self.angle = heading
        dx = x - self.x
        dy = y - self.y
        target_angle = degrees(atan2(dy, dx))
        delta_angle = target_angle - self.angle
        if delta_angle > 180:
            delta_angle -= 360

        elif delta_angle < -180:
            delta_angle += 360

        self.wheels.turn(delta_angle)
        distance = sqrt(dx ** 2 + dy ** 2)
        self.wheels.straight(distance)
        self.left_last_angle = left_angle
        self.right_last_angle = right_angle

    def get_wheels(self):
        return self.wheels

robot = Robot()

wait = 7.0
turn = 180


robot.move_to_avoid(1200, 1000)
time.sleep(wait)