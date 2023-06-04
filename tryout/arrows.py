from pynput import keyboard
from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank
import time

# Set up EV3
motor_left = LargeMotor(OUTPUT_B)
motor_right = LargeMotor(OUTPUT_C)

# Control speed
speed = 50  # Set to your preferred speed (SpeedPercent ranges from -100 to 100)

if not motor_left.connected:
    print("Motor on port B is not connected")
    exit(1)

if not motor_right.connected:
    print("Motor on port C is not connected")
    exit(1)

# Define functions to be called on key press
def on_press(key):
    try:
        if key == keyboard.Key.up:
            motor_left.run_forever(speed_sp=speed)
            motor_right.run_forever(speed_sp=speed)
        elif key == keyboard.Key.down:
            motor_left.run_forever(speed_sp=-speed)
            motor_right.run_forever(speed_sp=-speed)
        elif key == keyboard.Key.left:
            motor_left.run_forever(speed_sp=-speed)
            motor_right.run_forever(speed_sp=speed)
        elif key == keyboard.Key.right:
            motor_left.run_forever(speed_sp=speed)
            motor_right.run_forever(speed_sp=-speed)
    except AttributeError:
        pass

def on_release(key):
    motor_left.stop()
    motor_right.stop()

    # Stop listener if 'esc' is pressed
    if key == keyboard.Key.esc:
        return False

# Set up listener
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
