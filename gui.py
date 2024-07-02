# File: main.py
import sys, json, os.path
import serial.tools
import serial.tools.list_ports
import serial.tools.list_ports_linux
import vlc
import serial
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QDial,
) 
from PySide6.QtCore import (
    QFile, 
    QIODevice, 
    QStandardPaths, 
    QDir, 
    QRunnable,
    QThreadPool,
    Signal,
    QObject,
)
from PySide6 import QtCore

class SerialListenerSignals(QObject):
    on_playlist_start = Signal()
    on_playlist_stop = Signal()
    on_command = Signal(int)
    on_volume = Signal(int)

class SerialListener(QRunnable):
    '''
    Thread sitting in background and listening for incoming commands from serial port
    '''

    def __init__(self, serial_port) -> None:
        super().__init__()
        self.serial_port = serial_port
        self.signals = SerialListenerSignals()
        self.shutdown = False

    @QtCore.Slot(bool)
    def init_shutdown(self, value):
        print("Stopping listener...")
        self.shutdown = True


    def run(self):
        print("Start listing to serial port...")

        while self.shutdown == False:
            line = self.serial_port.readline().decode("UTF-8").rstrip()  # read until /n and strip new line chars
            if len(line) > 0:
                self.handle_command(line)


    def handle_command(self, command):
        print("Recived %s" % command)    
        if len(command.split(";")) == 2:
            button = command.split(";")[0]
            volume = command.split(";")[1]

            if int(button) > 0:
                if int(button) == 1:
                    self.signals.on_command.emit(0)
                if int(button) == 2:
                    self.signals.on_command.emit(1)
                if int(button) == 4:
                    self.signals.on_command.emit(2)
                if int(button) == 8:
                    self.signals.on_command.emit(3)
                if int(button) == 16:
                    self.signals.on_command.emit(4)
                if int(button) == 32:
                    self.signals.on_playlist_start.emit()
                if int(button) == 64:
                    self.signals.on_playlist_stop.emit()
            

            self.signals.on_volume.emit(int(volume) / 255 * 100)


vlc_instance = vlc.Instance() 
media_player = vlc_instance.media_player_new()
media_list_player = vlc_instance.media_list_player_new()

def find_first_arduino():
    for port in sorted(serial.tools.list_ports.comports(True)):
        if port.pid == 0x7523 and port.vid == 0x1a86:
            print("Found arduino: %s" % port.device)
            return port.device


arduino_port = find_first_arduino()
arduino = serial.Serial(port=arduino_port, baudrate=115200)


serial_listener = SerialListener(arduino)


def save_config():
    cfg = {
        "file_btn_0": window.lineEdit.text(),
        "file_btn_1": window.lineEdit_2.text(),
        "file_btn_2": window.lineEdit_3.text(),
        "file_btn_3": window.lineEdit_4.text(),
        "file_playlist": window.playlistEdit.text()
    }

    with open("nippelboard.json", "w") as f:
        f.write(json.dumps(cfg))


def choose_file(target):
    dlq = QFileDialog(None, "Datei auswählen", QDir.homePath(), "MP3(*.mp3)")
    
    if dlq.exec():
        filenames = dlq.selectedFiles()
        target.setText(filenames[0])


def button1_clicked():
    choose_file(window.lineEdit)


def button2_clicked():
    choose_file(window.lineEdit_2)


def button3_clicked():
    choose_file(window.lineEdit_3)


def button4_clicked():
    choose_file(window.lineEdit_4)


def playlist_clicked():
    choose_file(window.playlistEdit)


def play_position(pos=0):
    print("Now play pos %s" % pos)

    media = [
        window.lineEdit.text(),
        window.lineEdit_2.text(),
        window.lineEdit_3.text(),
        window.lineEdit_4.text()
    ]

    window.statusBar().showMessage("Playing %s" % media[pos])

    media_player.set_media(vlc.Media(media[pos]))
    
    if media_list_player.is_playing:
        media_list_player.set_pause(1)
    media_player.play()


def change_volume(volume):
    media_player.audio_set_volume(volume)
    window.volumeDial.setValue(volume)
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(lambda: serial_listener.init_shutdown(True))

    ui_file_name = "MainWindow.ui"
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
        sys.exit(-1)
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    if not window:
        print(loader.errorString())
        sys.exit(-1)


    serial_listener.signals.on_command.connect(lambda p: play_position(p))
    serial_listener.signals.on_volume.connect(lambda v: change_volume(v))
    
    window.pushButton.clicked.connect(button1_clicked)
    window.pushButton_2.clicked.connect(button2_clicked)
    window.pushButton_3.clicked.connect(button3_clicked)
    window.pushButton_4.clicked.connect(button4_clicked)
    window.playlistButton.clicked.connect(playlist_clicked)
    window.saveButton.clicked.connect(save_config)

    window.play0Button.clicked.connect(lambda: play_position(0))
    window.play1Button.clicked.connect(lambda: play_position(1))
    window.play2Button.clicked.connect(lambda: play_position(2))
    window.play3Button.clicked.connect(lambda: play_position(3))

    if os.path.isfile("nippelboard.json"):
        with open("nippelboard.json", "r") as f:
            config = json.load(f)
            window.lineEdit.setText(config["file_btn_0"])
            window.lineEdit_2.setText(config["file_btn_1"])
            window.lineEdit_3.setText(config["file_btn_2"])
            window.lineEdit_4.setText(config["file_btn_3"])

    media_player.audio_set_volume(100)
    volume = media_player.audio_get_volume()
    window.volumeDial.setValue(volume)

    window.volumeDial.valueChanged.connect(lambda x: change_volume(x))

    thread_pool = QThreadPool()
    thread_pool.start(serial_listener)

    window.show()

    sys.exit(app.exec())
