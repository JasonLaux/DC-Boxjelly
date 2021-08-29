from PyQt5.QtCore import QFile, QIODevice
from PyQt5.uic import loadUi
import sys

def loadUI(str, window):
    ui_file_name = str
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
        sys.exit(-1)
    loadedWindow = loadUi(ui_file, window)
    ui_file.close()
    if not loadedWindow:
        #print(loader.errorString())
        sys.exit(-1)
    return loadedWindow