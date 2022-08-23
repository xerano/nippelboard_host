import vlc
import serial
#################################################################################################
# media setup                                                                                   #
#                                                                                               #
#################################################################################################
media = [
    "/path/to/song/button0.mp3",
    "/path/to/song/button1.mp3",
    "/path/to/song/button2.mp3",
    "/path/to/song/button3.mp3"
]

playlist_location = "/path/to/playlist/pl.m3u"

################################################################################################
serial_port = "/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0"

arduino = serial.Serial(port=serial_port, baudrate=115200)

media_player = vlc.MediaPlayer()
media_list_player = vlc.MediaListPlayer()

playlist = vlc.MediaList()
playlist.add_media(playlist_location)

print(playlist.count())

media_list_player.set_media_list(playlist)


playlist_started = False


def listen():
    while True:
        line = arduino.readline().decode("UTF-8").rstrip()  # read until /n and strip new line chars
        print(line)
        if len(line) > 0:
            handle_command(line)


def handle_command(command):
    print(command)
    if len(command.split(";")) == 2:
        button = command.split(";")[0]
        volume = command.split(";")[1]

        if int(button) > 0:
            handle_button(int(button))

        handle_volume(volume)


def handle_button(button):
    print("handling button %s" % button)
    if button == 1:
        play_id(0)

    if button == 2:
        play_id(1)

    if button == 4:
        play_id(2)

    if button == 8:
        play_id(3)

    if button == 16:
        play_id(4)

    if button == 32:
        playlist_start()

    if button == 64:
        playlist_stop()


def handle_volume(volume):
    print("handling volume change")


def play_id(song_id):
    print("Playing %s" % song_id)
    media_player.set_media(vlc.Media(media[song_id]))
    if media_list_player.is_playing:
        media_list_player.set_pause(1)
    media_player.play()


def playlist_start():
    global playlist_started
    print("Starting playlist...")
    state = media_list_player.get_state()
    print(state)
    media_player.stop()

    if not playlist_started:
        media_list_player.play_item_at_index(0)
        playlist_started = True
    else:
        media_list_player.set_pause(0)


def playlist_stop():
    print("Stopping playlist...")
    media_list_player.set_pause(1)


if __name__ == "__main__":
    print("Starting nippelboard host...")
    listen()
