from ev3dev2.auto import *

try:
    m = LargeMotor(OUTPUT_C)
    print("Connected to the robot")
except Exception as e:
    print("Could not connect to the robot:", e)
