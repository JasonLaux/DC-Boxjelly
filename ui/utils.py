from PyQt5.QtCore import QFile, QIODevice
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
import sys
import pandas as pd
import os
from app.core.models import Job, Equipment

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

    data = {
        'status': [],
        'CAL Number': [],
        'Client Name': [],
        'Client Address': []
    }
    for job in Job:
        data['status'].append(False),
        data['CAL Number'].append(job._id),
        data['Client Name'].append(job.client_name),
        #data['Clinet Address'].append(str(job.client_address_1)+' '+str(job.client_address_2)),
        data['Client Address'].append(''),
    
    df = pd.DataFrame(data)
    return df

'''
Return equipments data as Dataframe
'''
def getEquipmentsTableData(job: Job):
    #job = Job[jobID]
    data = {
        'status': [],
        'Make/Model': [],
        'Serial Num': []
    }
    for equip in job:
        data['status'].append(False),
        data['Make/Model'].append(equip.model),
        data['Serial Num'].append(equip.serial),
    df = pd.DataFrame(data)
    return df

'''
Return runs data as Dataframe
'''
def getRunsTableData(equip: Equipment):
    #equip = Job[jobID][equipID]
    data = {
        'status': [],
        'ID': [],
        'Added Time': [],
        'Edited Time': []
    }
    for run in equip.mex:
        data['status'].append(False),
        data['ID'].append(run._id),
        data['Added Time'].append(run.added_at),
        data['Edited Time'].append(run.edited_at),
    df = pd.DataFrame(data)
    return df