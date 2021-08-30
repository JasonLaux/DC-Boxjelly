from PyQt5.QtCore import QFile, QIODevice
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
import sys
import pandas as pd

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

'''
Return client info data as Dataframe
'''
def getHomeTableData():
    data = {
        'status': [False, False, False],
        'CAL Number': ['CAL 001', 'CAL 002', 'CAL 003'],
        'Client Name': ['Amy', 'Jay', 'Jack'],
        'Clinet Address': ['8 Leonerd Street', '12 Collins Street', '5 Sutherland Street']
    }
    df = pd.DataFrame(data)
    return df
