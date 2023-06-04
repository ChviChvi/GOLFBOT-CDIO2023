from pynput import keyboard
from ev3dev2.motor import MoveTank, OUTPUT_C, OUTPUT_B

# Define your motors
tank_drive = MoveTank(OUTPUT_C, OUTPUT_B)

# Define the speed
speed = 50

# This function will be called when a key is pressed
def on_press(key):
    try:
        # If the up arrow key is pressed
        if key == keyboard.Key.up:
            tank_drive.on(speed, speed) # Move forward
        # If the down arrow key is pressed
        elif key == keyboard.Key.down:
            tank_drive.on(-speed, -speed) # Move backward
        # If the left arrow key is pressed
        elif key == keyboard.Key.left:
            tank_drive.on(-speed, speed) # Turn left
        # If the right arrow key is pressed
        elif key == keyboard.Key.right:
            tank_drive.on(speed, -speed) # Turn right
    except AttributeError:
        pass

# This function will be called when a key is released
def on_release(key):
    tank_drive.off() # Stop the motors
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
