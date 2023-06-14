from pynput.keyboard import Key, Listener
import paramiko
import signal
import sys

# Create a new SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the EV3 brick
ssh.connect('172.20.10.5', username='robot', password='maker')

# Open a new channel and start an interactive shell
channel = ssh.invoke_shell()

# Stop motors initially
channel.send("python3 -c 'from ev3dev2.motor import MoveTank, OUTPUT_A, OUTPUT_B; MoveTank(OUTPUT_A, OUTPUT_B).off()'\n")

# Define the commands for the arrow keys
commands = {
    Key.up: "python3 -c 'from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C; MoveTank(OUTPUT_B, OUTPUT_C).on_for_seconds(50, 50, 0.5)'",
    Key.down: "python3 -c 'from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C; MoveTank(OUTPUT_B, OUTPUT_C).on_for_seconds(-50, -50, 0.5)'",
    Key.left: "python3 -c 'from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C; MoveTank(OUTPUT_B, OUTPUT_C).on_for_seconds(-50, 50, 0.5)'",
    Key.right: "python3 -c 'from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C; MoveTank(OUTPUT_B, OUTPUT_C).on_for_seconds(50, -50, 0.5)'",
}


def on_press(key):
    if key in commands:
        # Print and send the command through the channel
        command = commands[key]
        print(f'Sending command: {command}')
        channel.send(command + "\n")

# Create the listener
listener = Listener(on_press=on_press)

# Start the listener in a non-blocking manner
listener.start()

# Set up signal handler for Ctrl+C
def signal_handler(sig, frame):
    print('Stopping...')
    channel.close()
    ssh.close()
    listener.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print("Script started. Press arrow keys to control the EV3 brick.")
print("Press Ctrl+C to stop the script.")

# Keep the main thread alive until the listener is stopped
while True:
    pass
