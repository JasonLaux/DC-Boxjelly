from PyQt5.QtCore import QFile, QIODevice
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
import sys
import pandas as pd
import os

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
    # data = {
    #     'status': [False, False, False],
    #     'CAL Number': ['CAL 001', 'CAL 002', 'CAL 003'],
    #     'Client Name': ['Amy', 'Jay', 'Jack'],
    #     'Clinet Address': ['8 Leonerd Street', '12 Collins Street', '5 Sutherland Street']
    # }

    os.chdir(os.getcwd()+"\..")
    from app.core.models import Job
    data = {
        'status': [],
        'CAL Number': [],
        'Client Name': [],
        'Client Address': []
    }
    for job in Job:
        print(job)
        data['status'].append(False),
        data['CAL Number'].append(job._id),
        data['Client Name'].append(job.client_name),
        #data['Clinet Address'].append(str(job.client_address_1)+' '+str(job.client_address_2)),
        data['Client Address'].append(''),
    
    df = pd.DataFrame(data)
    os.chdir(os.getcwd()+"\\ui")
    return df
