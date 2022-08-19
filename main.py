
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
    if len(command.split(";")) == 2:
        button = command.split(";")[0]
        volume = command.split(";")[1]

        if int(button) > 0:
            handle_button(int(button))

        handle_volume(volume)


def handle_button(button):
    print("handling button %s" % button)
    if button == 1:
        play_id(1)

    if button == 2:
        play_id(2)

    if button == 4:
        play_id(3)

    if button == 8:
        play_id(4)

    if button == 16:
        play_id(5)

    if button == 32:
        playlist_start()

    if button == 64:
        playlist_stop()


def handle_volume(volume):
    print("handling volume change")


def play_id(song_id):
    print("Playing %s" % song_id)


def playlist_start():
    print("Starting playlist...")


def playlist_stop():
    print("Stopping playlist...")


if __name__ == "__main__":
    print("Starting nippelboard host...")
    listen()
