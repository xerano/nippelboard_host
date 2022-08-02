
import vlc
import serial

serial_port = "/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0"

arduino = serial.Serial(port=serial_port, baudrate=115200)


def listen():
    while True:
        line = arduino.readline().decode("UTF-8").rstrip()  # read until /n and strip new line chars
        print(line)
        if len(line) > 0:
            handle_command(line)


def handle_command(command):
    button = command.split(";")[0] if ";" in command else "0"
    volume = command.split(";")[1] if len(command.split(";")) == 2 else 0

    if int(button) > 0:
        handle_button(button)

    handle_volume(volume)


def handle_button(button):
    print("handling button %s" % button)


def handle_volume(volume):
    print("handling volume change")


if __name__ == "__main__":
    print("Starting nippelboard host...")
    listen()
