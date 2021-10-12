from os import error, name
from typing import Counter
from PyQt5 import QtWidgets, QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QErrorMessage, QMainWindow, QHeaderView, QTableView, QItemDelegate, QGraphicsScene, QFileDialog, QDialog, QProgressBar, QPushButton
from PyQt5.QtCore import QObject, QRunnable, QThreadPool, Qt, QSortFilterProxyModel, QAbstractTableModel, QThread, pyqtSignal, pyqtSlot
import sys
from numpy import clongdouble, empty
from pandas.io.pytables import Selection, SeriesFixed
import pandas as pd
import pyqtgraph as pg
import os
from pathlib import Path
import logging
import numpy as np
import time
import tempfile
import shutil
import dateutil.parser


from app.gui.utils import loadUI, getHomeTableData, getEquipmentsTableData, getRunsTableData, getResultData, converTimeFormat, getConstantsTableData
from app.core.models import Job, Equipment, MexRawFile, ConstantFile, MexRun, constant_file_config
from app.core.resolvers import HeaderError, calculator, result_data, summary, extractionHeader, Header_data, pdf_visualization
from app.gui import resources
from app.export.pdf import get_pdf
from datetime import datetime
from copy import deepcopy
from shutil import copyfile
from app.core.definition import DATA_FOLDER

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

'''
#Run UI main file under root dir
py -m app.gui.main
'''

'''
Alter Python identifier to custom one for the purpose of icon placement
'''
try:
    # Include in try/except block if you're also targeting Mac/Linux
    from PyQt5.QtWinExtras import QtWin
    myappid = 'com.unimelb.software.dc'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)    
except ImportError:
    pass

class MainWindow(QMainWindow):

    JOB_LIST_WINDOW_TITLE = 'Job List'

    CLIENT_INFO_WINDOW_TITLE = 'Client Info'

    EQUIPMENT_INFO_WINDOW_TITLE = 'Equipment Info'


    def __init__(self):
        QMainWindow.__init__(self)
        
        # load main window ui
        window = loadUI(':/ui/main_window.ui', self)
        #window = loadUI("./app/gui/main_window.ui", self)
        self.ui = window
        self.setWindowTitle(self.JOB_LIST_WINDOW_TITLE)

        # load other windows
        self.addClientWindow = AddClientWindow(self)
        self.constantsWindow = ConstantsWindow(self)
        self.importWindow = ImportWindow(self)
        self.homeImportWindow = HomeImportWindow(self)
        self.analysisWindow = AnalyseWindow(self)
        self.addEquipmentWindow = AddEquipmentWindow(self)
        self.reuploadWindow = ReuploadWindow(self)

        #Home Page
        self.ui.homeButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.homePage))
        self.ui.homeButton.clicked.connect(lambda: self.setWindowTitle(self.JOB_LIST_WINDOW_TITLE))
        # View/Edit Client Info 
        self.ui.chooseClientButton.clicked.connect(self.chooseClient)
        self.ui.addClientButton.clicked.connect(lambda: self.ui.homeTable.clearSelection())
        self.ui.updateClientButton.clicked.connect(self.updateClientInfo)
        self.ui.clientNamelineEdit.textChanged.connect(lambda: self.ui.updateClientButton.setEnabled(True))
        self.ui.address1lineEdit.textChanged.connect(lambda: self.ui.updateClientButton.setEnabled(True))
        self.ui.address2lineEdit.textChanged.connect(lambda: self.ui.updateClientButton.setEnabled(True))

        #compare page
        self.ui.chooseEquipmentButton.clicked.connect(self.chooseEquipment)
        # Return to Home Page
        self.ui.returnButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.homePage))
        self.ui.returnButton.clicked.connect(lambda: self.ui.equipmentsTable.clearSelection())
        self.ui.returnButton.clicked.connect(lambda: self.ui.updateClientButton.setEnabled(False))
        self.ui.returnButton.clicked.connect(lambda: self.setWindowTitle(self.JOB_LIST_WINDOW_TITLE))

        # Return to Client Info Page
        self.ui.returnButton_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.clientInfoPage))
        self.ui.returnButton_2.clicked.connect(lambda: self.ui.runsTable.clearSelection())
        self.ui.returnButton_2.clicked.connect(lambda: self.setWindowTitle(self.CLIENT_INFO_WINDOW_TITLE))

        # Delete client
        self.ui.deleteClientButton.clicked.connect(self.deleteClient)

        # Add equipment
        self.ui.addEquipmentButton.clicked.connect(lambda: self.ui.equipmentsTable.clearSelection())

        # Delete equipment
        self.ui.deleteEquipmentButton.clicked.connect(self.deleteEquipment)
        # Add and delete run
        self.ui.importButton.clicked.connect(lambda: self.ui.runsTable.clearSelection())
        self.ui.deleteRunButton.clicked.connect(self.deleteRun)
        
        
        #Dynamic search
        self.ui.homeTable.horizontalHeader().setStyleSheet("QHeaderView { font-size: 12pt; font-family: Verdana; font-weight: bold; }")       
        self.clientModel = TableModel(data=getHomeTableData())

        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setFilterKeyColumn(-1) # Search all columns.
        self.proxy_model.setSourceModel(self.clientModel)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.ui.searchBar.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.ui.searchBar.textEdited.connect(self.ui.homeTable.clearSelection)

        self.ui.homeTable.setModel(self.proxy_model)
        self.ui.homeTable.setSortingEnabled(True)
        self.ui.homeTable.sortByColumn(0, Qt.AscendingOrder)
        self.ui.homeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) #column stretch to window size
        self.ui.homeTable.setItemDelegate(AlignDelegate()) # text alignment


        ## Table insertion
        # Equipment Table
        self.ui.equipmentsTable.horizontalHeader().setStyleSheet("QHeaderView { font-size: 12pt; font-family: Verdana; font-weight: bold; }")
        self.equipmentModel = TableModel(data=pd.DataFrame([]))

        self.equip_sortermodel = QSortFilterProxyModel()
        self.equip_sortermodel.setSourceModel(self.equipmentModel)
        self.ui.equipmentsTable.setModel(self.equip_sortermodel)
        self.ui.equipmentsTable.setSortingEnabled(True)
        self.ui.equipmentsTable.sortByColumn(0, Qt.AscendingOrder)
        self.ui.equipmentsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.equipmentsTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ui.equipmentsTable.selectionModel().selectionChanged.connect(lambda: self.selection_changed('equipmentsTable'))
        self.ui.equipmentsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.equipmentsTable.setItemDelegate(AlignDelegate())

        self._selectedEquipID = ""

        # Run Table
        self.ui.runsTable.horizontalHeader().setStyleSheet("QHeaderView { font-size: 12pt; font-family: Verdana; font-weight: bold; }")        
        self.runModel = TableModel(data=pd.DataFrame([]))
        self.run_sortermodel = QSortFilterProxyModel()
        self.run_sortermodel.setSourceModel(self.runModel)        
        self.ui.runsTable.setModel(self.run_sortermodel)
        self.ui.runsTable.setSortingEnabled(True)
        self.ui.runsTable.sortByColumn(0, Qt.AscendingOrder)
        self.ui.runsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.runsTable.selectionModel().selectionChanged.connect(lambda: self.selection_changed('runsTable'))
        self.ui.runsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.runsTable.setItemDelegate(AlignDelegate())
        self.ui.runsTable.setContextMenuPolicy(Qt.CustomContextMenu) 
        self.ui.runsTable.customContextMenuRequested.connect(self.showContextMenu)


        # Change selection behaviour. User can only select rows rather than cells. Single selection
        self.ui.homeTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.homeTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ui.homeTable.selectionModel().selectionChanged.connect(lambda: self.selection_changed('homeTable'))
        self._selectedRows = []
        self._selectedCalNum = ""
        self._selectedRuns = []
        self._sourceIndex = {}


    def chooseClient(self):
        """
        Choose one client and goes into client info page.
        When not choosing any of the client, pop up a warning window
        """
        if self._selectedRows:
            self.ui.updateClientButton.setEnabled(False)
            self.ui.stackedWidget.setCurrentWidget(self.ui.clientInfoPage)
            self.ui.homeTable.clearSelection()
            self.setWindowTitle(self.CLIENT_INFO_WINDOW_TITLE)
        else:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose a Client!")


    def deleteClient(self):
        """
        Delete chosen client on the Home Page by clicking 'delete client' button.
        When not choosing any of the client, pop up a warning window
        """
        if self._selectedRows:
            self.clientModel.layoutAboutToBeChanged.emit()
            self._selectedCalNum = self.clientModel._data.loc[self._sourceIndex["homeTable"], 'CAL Number'].to_list()[0]
            reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Do you want delete this client?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                del Job[self._selectedCalNum] 

                self.clientModel.initialiseTable(data=getHomeTableData())
                self.clientModel.layoutChanged.emit()
            self.ui.homeTable.clearSelection()

            if self.clientModel.isTableEmpty:
                self._selectedRows = []
        else:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose a client to delete.")
    

    def updateClientInfo(self):
        """
        Update client info on the Client Info Page by clicking 'update' button.
        """
        self.clientModel.layoutAboutToBeChanged.emit()
        self.ui.updateClientButton.setEnabled(False)

        newClientName = self.ui.clientNamelineEdit.text()
        newFstAddress = self.ui.address1lineEdit.text()
        newSndAddress = self.ui.address2lineEdit.text()

        try: 
            Job[self._selectedCalNum].client_name = newClientName
            Job[self._selectedCalNum].client_address_1 = newFstAddress
            Job[self._selectedCalNum].client_address_2 = newSndAddress
            QtWidgets.QMessageBox.about(self, ' ', "Successfully updated user information.")
        except AttributeError:
            raise error("Job ID is not found!")

        # Update client info on the Home Page
        self.clientModel.initialiseTable(data=getHomeTableData())
        self.clientModel.layoutChanged.emit()


    def chooseEquipment(self):
        """
        Choose one equipment and goes into Equipment info page.
        When not choosing any of the equipments, pop up a warning window.
        """
        if self._selectedRows:
            self.ui.stackedWidget.setCurrentWidget(self.ui.equipmentInfoPage)
            self._selectedRows = []
            self.setWindowTitle(self.EQUIPMENT_INFO_WINDOW_TITLE)

            # Display the equipment info
            self.ui.label_eqCAL.setText(self._selectedCalNum)
            self.ui.label_eqCN.setText(Job[self._selectedCalNum].client_name)
            self.ui.label_eqSN.setText(Job[self._selectedCalNum][self._selectedEquipID].serial)
            self.ui.label_eqMN.setText(Job[self._selectedCalNum][self._selectedEquipID].model)
            self.ui.equipmentsTable.clearSelection()
        else:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose an Equipment!")


    def deleteEquipment(self):
        """
        Delete chosen equipment on the Client Info Page by clicking 'delete equipment' button.
        When not choosing any of the equipment, pop up a warning window.
        """
        if self._selectedRows:
            self.equipmentModel.layoutAboutToBeChanged.emit()
            self._selectedEquipID = self.equipmentModel._data.loc[self._sourceIndex["equipmentsTable"], 'ID'].to_list()[0]
            reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Do you want delete this Equipment?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                del Job[self._selectedCalNum][self._selectedEquipID]
                self.equipmentModel.initialiseTable(data=getEquipmentsTableData(Job[self._selectedCalNum]))
                self.equipmentModel.layoutChanged.emit()
            self.ui.equipmentsTable.clearSelection()
        else:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose a client to delete.")
            

    def deleteRun(self):
        """
        Delete chosen run on the Client Info Page by clicking 'delete run' button.
        When not choosing any of the equipment, pop up a warning window.
        """
        if self._selectedRows:
            self.runModel.layoutAboutToBeChanged.emit()
            selectedRun = self.runModel._data.loc[self._sourceIndex["runsTable"], 'ID'].to_list()
            # logger.debug(selectedRun)
            reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Do you want delete selected run or runs?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                for runId in selectedRun:
                    try:
                        del Job[self._selectedCalNum][self._selectedEquipID].mex[runId]
                    except PermissionError:
                        QtWidgets.QMessageBox.about(self, "Warning", "Please close the raw file first.")
                        return
                self.runModel.initialiseTable(data=getRunsTableData(Job[self._selectedCalNum][self._selectedEquipID]))
                self.runModel.layoutChanged.emit()
            
            self.ui.runsTable.clearSelection()
        else:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose a run to delete.")
    

    def selection_changed(self, tableName):
        """
        Return the index of selected rows in an array.
        """
        try:
            # TODO Order is based on the selection. Need to sort first?
            modelIndex = getattr(self, tableName).selectionModel().selectedRows() # QModelIndexList
            self._selectedRows = [idx.row() for idx in modelIndex]
            self._sourceIndex = {}
            logger.debug(self._selectedRows)
            if tableName == "homeTable" and self._selectedRows != []:
                self.equipmentModel.layoutAboutToBeChanged.emit()
                source_selectedIndex = [self.proxy_model.mapToSource(modelIndex[0]).row()]
                self._sourceIndex.setdefault("homeTable", source_selectedIndex)
                logger.debug(source_selectedIndex)
                self._selectedCalNum = self.clientModel._data.loc[source_selectedIndex, 'CAL Number'].to_list()[0]
                logger.debug(self._selectedCalNum)
                self.ui.label_CALNum.setText(self._selectedCalNum)
                self.ui.clientNamelineEdit.setText(Job[self._selectedCalNum].client_name)
                self.ui.address1lineEdit.setText(Job[self._selectedCalNum].client_address_1)
                self.ui.address2lineEdit.setText(Job[self._selectedCalNum].client_address_2)
                self.equipmentModel.initialiseTable(data=getEquipmentsTableData(Job[self._selectedCalNum]))
                self.equipmentModel.layoutChanged.emit()
                self.ui.equipmentsTable.setColumnHidden(2, True)

            elif tableName == "equipmentsTable" and self._selectedRows != []:
                self.runModel.layoutAboutToBeChanged.emit()
                source_selectedIndex = [self.equip_sortermodel.mapToSource(modelIndex[0]).row()]
                self._sourceIndex.setdefault("equipmentsTable", source_selectedIndex)
                logger.debug(source_selectedIndex)
                self._selectedEquipID = self.equipmentModel._data.loc[source_selectedIndex, 'ID'].to_list()[0]
                self.runModel.initialiseTable(data=getRunsTableData(Job[self._selectedCalNum][self._selectedEquipID]))
                self.runModel.layoutChanged.emit()
                # self.ui.runsTable.setColumnHidden(2, True)

            elif tableName == "runsTable" and self._selectedRows != []:
                source_selectedIndex = []
                for idx in modelIndex:
                    source_selectedIndex.append(self.run_sortermodel.mapToSource(idx).row())
                self._sourceIndex.setdefault("runsTable", source_selectedIndex)
                logger.debug(source_selectedIndex)
                selectedRuns = self.runModel._data.loc[sorted(source_selectedIndex), 'ID'].to_list()
                runs = list(map(lambda runId:Job[self._selectedCalNum][self._selectedEquipID].mex[runId], selectedRuns))
                self._selectedRuns = runs
                logger.debug(self._selectedRuns)
                
                

        except AttributeError:
            raise AttributeError("Attribute does not exist! Table name may be altered!")


    def openConstantsWindow(self):
        """
        Open constant file instead of open constant window.
        """
        self.addClientWindow.setFixedSize(750, 500)
        self.constantsWindow.show()


    def openAddClientWindow(self):
        self.addClientWindow.setFixedSize(850, 320)
        self.addClientWindow.setWindowModality(Qt.ApplicationModal)
        self.addClientWindow.show()


    def openAddEquipmentWindow(self):
        self.addEquipmentWindow.setFixedSize(850, 320)
        self.addEquipmentWindow.setWindowModality(Qt.ApplicationModal)
        self.addEquipmentWindow.show()
        self.addEquipmentWindow.job = Job[self._selectedCalNum]


    def openImportWindow(self):
        self.importWindow.setFixedSize(850, 320)
        self.importWindow.setWindowModality(Qt.ApplicationModal)
        self.importWindow.show()
        self.importWindow.equip = Job[self._selectedCalNum][self._selectedEquipID]


    def openHomeImportWindow(self):
        self.homeImportWindow.setFixedSize(850, 320)
        self.homeImportWindow.setWindowModality(Qt.ApplicationModal)
        self.homeImportWindow.show()
    
    
    def openReuploadWindow(self):
        self.reuploadWindow.setFixedSize(850, 320)
        self.reuploadWindow.setWindowModality(Qt.ApplicationModal)
        self.reuploadWindow.show()


    def openAnalysisWindow(self):
        """
        Choose runs and goes into the analysis page.
        When not choosing any of runs, pop up a warning window
        """
        if self._selectedRows:
            try:
                self.analysisWindow.setRuns(self._selectedRuns) 
                # initailize constants label
                if constant_file_config.default_id:
                    if ConstantFile[constant_file_config.default_id].note:
                        self.analysisWindow.ui.constantsLabel.setText("Current Constants File: %s (%s)" % (constant_file_config.default_id, ConstantFile[constant_file_config.default_id].note))
                    else:
                        self.analysisWindow.ui.constantsLabel.setText("Current Constants File: %s " % constant_file_config.default_id)
                else:
                    self.analysisWindow.ui.constantsLabel.setText("Current Constants File: Template Constants ")
                self.analysisWindow.setWindowModality(Qt.ApplicationModal)
                self.analysisWindow.show()
                self.ui.runsTable.clearSelection()
            except Exception as e:
                logger.error("Can't resolve raw data file!", exc_info=e)
                QtWidgets.QMessageBox.about(self, "Warning", "Can not resolve raw files. Please check the data.")
        else:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose at least one run to analyze.")

        
        
    def showContextMenu(self):  
        self.ui.runsTable.contextMenu = QtWidgets.QMenu(self)
        self.ui.runsTable.contextMenu.setStyleSheet("""
            QMenu:selected {background-color: #ddf; color: #000;}
            """
            )

        def add_action(name, handler):
            action = self.ui.runsTable.contextMenu.addAction(name)
            action.triggered.connect(lambda: self.actionHandler(handler))
            
        add_action('Open raw client file', 'OpenClientFile')
        add_action('Open raw lab file', 'OpenLabFile')
        add_action('Re-upload', "Reupload")
        add_action('Export raw client to..', 'export_client')
        add_action('Export raw lab to..', 'export_lab')

        self.ui.runsTable.contextMenu.popup(QtGui.QCursor.pos())  # Menu position based on cursor
        self.ui.runsTable.contextMenu.show()


    def actionHandler(self, action):
        logger.debug("Open menu")

        # If multiple runs are chosen, only the first run is processed
        selectedRun = self.runModel._data.loc[sorted(self._sourceIndex["runsTable"]), 'ID'].to_list()[0]
        run = Job[self._selectedCalNum][self._selectedEquipID].mex[selectedRun]

        if action == "OpenClientFile":
            os.startfile(run.raw_client.path)
        elif action == "OpenLabFile":
            os.startfile(run.raw_lab.path)
        elif action == "Reupload":
            self.openReuploadWindow()
            self.reuploadWindow.setRuns(selectedRun, run)
        elif action == 'export_lab':
            self.export_raw_file(run.raw_lab, 'lab')
        elif action == 'export_client':
            self.export_raw_file(run.raw_client, 'client')

    def export_raw_file(self, raw: MexRawFile, type: str):

        if not raw.exists:
            QtWidgets.QErrorMessage().showMessage(f'The {type} file does not exist!')
            return

        path, _ = QFileDialog.getSaveFileName(self, f'Save {type} file to',
            raw.export_file_name, 'CSV Files (*.csv)')

        if path:
            raw.export_to(Path(path))


class ImportWindow(QMainWindow):
    def __init__(self, parent = None):
        super(ImportWindow, self).__init__(parent)
        self.parent = parent
        
        # load import page ui
        # window = loadUI(".\\app\\gui\\import_page.ui", self)
        #window = loadUI("./app/gui/import_page.ui", self)
        window = loadUI(':/ui/import_page.ui', self)

        self.ui = window
        self.equip: Equipment = None
        self.clientPath = self.ui.clientFilePathLine.text()
        self.labPath = self.ui.labFilePathLine.text()
        self.ui.clientFilePathLine.textChanged.connect(self.sync_clientLineEdit)
        self.ui.labFilePathLine.textChanged.connect(self.sync_labLineEdit)

        # link buttons to actions
        self.importClientFilebutton.clicked.connect(self.chooseRawClient)
        self.importLabFileButton.clicked.connect(self.chooseRawLab)
        self.importSubmitButton.clicked.connect(self.addNewRun)
        self.clientOpenFile.clicked.connect(self.openClientFile)
        self.labOpenFile.clicked.connect(self.openLabFile)

    def sync_clientLineEdit(self):
        self.clientPath = self.ui.clientFilePathLine.text()
    
    def sync_labLineEdit(self):
        self.labPath = self.ui.labFilePathLine.text()
    
    def chooseRawClient(self):
        file_filter = 'Raw Data File (*.csv)'
        self.clientPath = QFileDialog.getOpenFileName(
            parent = self,
            caption = 'Please Select Client Raw File',
            directory = os.getcwd(),
            filter = file_filter,
            initialFilter = 'Raw Data File (*.csv)'
        )[0]
        logger.debug("Client raw file: %s", self.clientPath)
        self.ui.clientFilePathLine.setText(self.clientPath)
    

    def chooseRawLab(self):
        file_filter = 'Raw Data File (*.csv)'
        self.labPath = QFileDialog.getOpenFileName(
            parent = self,
            caption = 'Please Select Lab Raw File',
            directory = os.getcwd(),
            filter = file_filter,
            initialFilter = 'Raw Data File (*.csv)'
        )[0]
        logger.debug("Lab raw file: %s", self.labPath)
        self.ui.labFilePathLine.setText(self.labPath)


    def addNewRun(self):
        self.parent.runModel.layoutAboutToBeChanged.emit()
        self.parent.ui.runsTable.clearSelection()
        if len(self.clientPath) == 0 or len(self.labPath) == 0:
            QtWidgets.QMessageBox.about(self, "Warning", "Please fill in both Client file and Lab file path.")
            return
        if (not os.path.isfile(self.clientPath)) or (not os.path.isfile(self.labPath)):
            QtWidgets.QMessageBox.about(self, "Warning", "File not found, Please check your file path.")
            return
        run: MexRun = self.equip.mex.add()
        run.raw_client.upload_from(Path(self.clientPath))
        run.raw_lab.upload_from(Path(self.labPath))

        error = self.equip.check_consistency()
        if error:
            run.delete()
            QErrorMessage(self).showMessage(error)
            return

        data = {
            'ID': run.id,
            # 'Added Time': converTimeFormat(run.added_at),
            'Edited Time': converTimeFormat(run.edited_at),
            'Measurement Date': converTimeFormat(run.measured_at).split()[0],
            'Operator': run.operator,
        }
        self.parent.runModel.addData(pd.DataFrame(data, index=[0]))
        self.parent.runModel.layoutChanged.emit()
        
        # Finish add new run and quit
        self.hide()
        self.equip = None
        self.clientPath = ""
        self.labPath = ""
        self.ui.clientFilePathLine.clear()
        self.ui.labFilePathLine.clear()
        # TODO: Display another window to confirm information
    
    def openClientFile(self):
        if not os.path.isfile(self.clientPath):
            QtWidgets.QMessageBox.about(self, "Warning", "Client file not found, Please check your file path.")
            return
        if self.clientPath != "":
            try:
                os.startfile(self.clientPath)
            except FileNotFoundError:
                QtWidgets.QMessageBox.about(self, "Warning", "File not found, Please check your path.")
    
    def openLabFile(self):
        if not os.path.isfile(self.labPath):
            QtWidgets.QMessageBox.about(self, "Warning", "Lab file not found, Please check your file path.")
            return
        if self.labPath != "":
            try:
                os.startfile(self.labPath)
            except FileNotFoundError:
                QtWidgets.QMessageBox.about(self, "Warning", "File not found, Please check your path.")


    def closeEvent(self, event):  
        if len(self.ui.clientFilePathLine.text()) != 0 or len(self.ui.labFilePathLine.text()) != 0:
            reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window? \nAll inputs will be clear.', QtWidgets.QMessageBox.Yes,
                                                QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.ui.clientFilePathLine.clear()
                self.ui.labFilePathLine.clear()
                event.accept()  
            else:
                event.ignore() 
        else:
            event.accept() 


class ReuploadWindow(ImportWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.selectedRun = None
        self.run = None

    def addNewRun(self):
        self.parent.runModel.layoutAboutToBeChanged.emit()
        self.parent.ui.runsTable.clearSelection()
        if len(self.clientPath) == 0 or len(self.labPath) == 0:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose or fill in both Client file and Lab file path.")
            return
        if (not os.path.isfile(self.clientPath)) or (not os.path.isfile(self.labPath)):
            QtWidgets.QMessageBox.about(self, "Warning", "File not found, Please check your file path.")
            return

        self.run.raw_client.upload_from(Path(self.clientPath))
        self.run.raw_lab.upload_from(Path(self.labPath))
        
        self.parent.runModel.initialiseTable(data=getRunsTableData(Job[self.parent._selectedCalNum][self.parent._selectedEquipID]))

        self.parent.runModel.layoutChanged.emit()
        
        # Finish add new run and quit
        self.hide()
        self.equip = None
        self.clientPath = ""
        self.labPath = ""
        self.ui.clientFilePathLine.clear()
        self.ui.labFilePathLine.clear()
    

    def setRuns(self, selectedRun, run):
        logger.debug("Selected RunID: %s", selectedRun)
        self.selectedRun = selectedRun
        self.run = run
        pass


class HomeImportWindow(QMainWindow):
    def __init__(self, parent = None):
        super(HomeImportWindow, self).__init__(parent)
        self.parent = parent
        
        # load import page ui
        # window = loadUI(".\\app\\gui\\import_page.ui", self)
        #window = loadUI("./app/gui/import_page.ui", self)
        window = loadUI(':/ui/import_page.ui', self)
        self.ui = window
        self.confirmWindow = ConfirmWindow(self)
        self.data = Header_data()
        self.clientPath = self.ui.clientFilePathLine.text()
        self.labPath = self.ui.labFilePathLine.text()
        self.ui.clientFilePathLine.textChanged.connect(self.sync_clientLineEdit)
        self.ui.labFilePathLine.textChanged.connect(self.sync_labLineEdit)

        # link buttons to actions
        self.importClientFilebutton.clicked.connect(self.chooseRawClient)
        self.importLabFileButton.clicked.connect(self.chooseRawLab)
        self.importSubmitButton.clicked.connect(self.submit)
        self.clientOpenFile.clicked.connect(self.openClientFile)
        self.labOpenFile.clicked.connect(self.openLabFile)
        self.confirmWindow.confirmButton.clicked.connect(self.addNewRun)
        self.confirmWindow.quitButton.clicked.connect(self.confirmWindow.close)

    def sync_clientLineEdit(self):
        self.clientPath = self.ui.clientFilePathLine.text()
    
    def sync_labLineEdit(self):
        self.labPath = self.ui.labFilePathLine.text()
    
    def chooseRawClient(self):
        file_filter = 'Raw Data File (*.csv)'
        self.clientPath = QFileDialog.getOpenFileName(
            parent = self,
            caption = 'Please Select Client Raw File',
            directory = os.getcwd(),
            filter = file_filter,
            initialFilter = 'Raw Data File (*.csv)'
        )[0]
        logger.debug("Client raw file: %s", self.clientPath)
        self.ui.clientFilePathLine.setText(self.clientPath)
    
    def chooseRawLab(self):
        file_filter = 'Raw Data File (*.csv)'
        self.labPath = QFileDialog.getOpenFileName(
            parent = self,
            caption = 'Please Select Lab Raw File',
            directory = os.getcwd(),
            filter = file_filter,
            initialFilter = 'Raw Data File (*.csv)'
        )[0]
        logger.debug("Lab raw file: %s", self.labPath)
        self.ui.labFilePathLine.setText(self.labPath)
    
    def submit(self):
        # file path check
        if self.clientPath.strip() == "" or self.labPath.strip() == "":
            QtWidgets.QMessageBox.about(self, "Warning", "Please fill in both client file and lab file path.")
            return
        if (not os.path.isfile(self.clientPath)) or (not os.path.isfile(self.labPath)):
            QtWidgets.QMessageBox.about(self, "Warning", "File not found, Please check your file path.")
            return
        
        # resolve header data from file
        try: 
            self.data = extractionHeader(self.clientPath, self.labPath)
        except HeaderError as e:
            QtWidgets.QMessageBox.about(self, "Warning", "".join(list(e.args)))
            return

        # pop up confirm page
        self.confirmWindow.calNumLine.setText(self.data.CAL_num)
        self.confirmWindow.clientNameLine.setText(self.data.Client_name)
        self.confirmWindow.clientAddress1Line.setText(self.data.address_1)
        self.confirmWindow.clientAddress2Line.setText(self.data.address_2)
        self.confirmWindow.chamberLine.setText(self.data.model+" "+self.data.serial)
        self.confirmWindow.operatorLine.setText(self.data.operator)
        self.confirmWindow.measurementLine.setText(self.data.date)
        self.confirmWindow.setFixedSize(800, 560)
        # self.confirmWindow.setWindowModality(Qt.ApplicationModal)
        self.confirmWindow.show()
        
    def addNewRun(self):
        # prepare update tables
        self.parent.clientModel.layoutAboutToBeChanged.emit()
        self.parent.equipmentModel.layoutAboutToBeChanged.emit()
        self.parent.runModel.layoutAboutToBeChanged.emit()

        jobsID = []
        for job in Job:
            jobsID.append(job.id)
        if not self.data.CAL_num in jobsID:
            # if job not exsited, create job, equip and add one run
            job = Job.make(self.data.CAL_num, client_name = self.data.Client_name, client_address_1 = self.data.address_1, client_address_2 = self.data.address_2)
            newClient = {
                'CAL Number': self.data.CAL_num,
                'Client Name': self.data.Client_name,
            }
            # TODO: fix ValueError bug
            try:
                self.parent.clientModel.addData(pd.DataFrame(newClient, index=[0]) )
            except ValueError:
                pass
            self.parent.clientModel.layoutChanged.emit()
            equip = job.add_equipment(model = self.data.model, serial = self.data.serial)
            newEquip = {
                'Make/Model': self.data.model,
                'Serial Num': self.data.serial,
                'ID': equip.id,
            }
            # TODO: fix ValueError bug
            try:
                self.parent.equipmentModel.addData(pd.DataFrame(newEquip, index=[0]) )
            except ValueError:
                pass
            self.parent.equipmentModel.layoutChanged.emit()
            run = equip.mex.add()
            run.raw_client.upload_from(Path(self.clientPath))
            run.raw_lab.upload_from(Path(self.labPath))
            error = equip.check_consistency()
            if error:
                run.delete()
                QErrorMessage(self).showMessage(error)
                return
            data = {
                    'ID': run.id,
                    # 'Added Time': converTimeFormat(run.added_at),
                    'Edited Time': converTimeFormat(run.edited_at),
                    'Measurement Date': converTimeFormat(run.measured_at).split()[0],
                    'Operator': run.operator,
            }
            # TODO: fix ValueError bug
            try:
                self.parent.runModel.addData(pd.DataFrame(data, index=[0]))
            except ValueError:
                pass
            self.parent.runModel.layoutChanged.emit()
        else:
            job = Job[self.data.CAL_num]
            equipsID = []
            for equip in job:
                equipsID.append(equip.id)
            equipId = self.data.model+' '+self.data.serial
            if not equipId in equipsID:
                # if equip not existed, create equip then add run  
                equip = job.add_equipment(model = self.data.model, serial = self.data.serial)
                newEquip = {
                    'Make/Model': self.data.model,
                    'Serial Num': self.data.serial,
                    'ID': equip.id,
                }
                # TODO: fix ValueError bug
                try:
                    self.parent.equipmentModel.addData(pd.DataFrame(newEquip, index=[0]) )
                except ValueError:
                    pass
                self.parent.equipmentModel.layoutChanged.emit()
                run = equip.mex.add()
                run.raw_client.upload_from(Path(self.clientPath))
                run.raw_lab.upload_from(Path(self.labPath))
                error = equip.check_consistency()
                if error:
                    run.delete()
                    QErrorMessage(self).showMessage(error)
                    return
                data = {
                    'ID': run.id,
                    # 'Added Time': converTimeFormat(run.added_at),
                    'Edited Time': converTimeFormat(run.edited_at),
                    'Measurement Date': converTimeFormat(run.measured_at).split()[0],
                    'Operator': run.operator,
                }
                # TODO: fix ValueError bug
                try:
                    self.parent.runModel.addData(pd.DataFrame(data, index=[0]))
                except ValueError:
                    pass
                self.parent.runModel.layoutChanged.emit()
            else:
                # if both job and equip existed, add run to it
                equip = Job[self.data.CAL_num][equipId]
                run = equip.mex.add()
                run.raw_client.upload_from(Path(self.clientPath))
                run.raw_lab.upload_from(Path(self.labPath))
                error = equip.check_consistency()
                if error:
                    run.delete()
                    QErrorMessage(self).showMessage(error)
                    return
                data = {
                    'ID': run.id,
                    # 'Added Time': converTimeFormat(run.added_at),
                    'Edited Time': converTimeFormat(run.edited_at),
                    'Measurement Date': converTimeFormat(run.measured_at).split()[0],
                    'Operator': run.operator,
                }
                # TODO: fix ValueError bug
                try:
                    self.parent.runModel.addData(pd.DataFrame(data, index=[0]))
                except ValueError:
                    pass
                self.parent.runModel.layoutChanged.emit()
        
        # pop up message when import successfully
        QtWidgets.QMessageBox.about(self, "Notification", "File imported successfully!")
        
        # Finish add new run and quit
        self.hide()
        self.confirmWindow.close()
        self.clientPath = ""
        self.labPath = ""
        self.ui.clientFilePathLine.clear()
        self.ui.labFilePathLine.clear()
    
    def openClientFile(self):
        if not os.path.isfile(self.clientPath):
            QtWidgets.QMessageBox.about(self, "Warning", "Client file not found, Please check your file path.")
            return
        if self.clientPath != "":
            try:
                os.startfile(self.clientPath)
            except FileNotFoundError:
                QtWidgets.QMessageBox.about(self, "Warning", "File not found, Please check your path.")
    
    def openLabFile(self):
        if not os.path.isfile(self.labPath):
            QtWidgets.QMessageBox.about(self, "Warning", "Lab file not found, Please check your file path.")
            return
        if self.clientPath != "":
            try:
                os.startfile(self.labPath)
            except FileNotFoundError:
                QtWidgets.QMessageBox.about(self, "Warning", "File not found, Please check your path.")

    def closeEvent(self, event):  
        if len(self.ui.clientFilePathLine.text()) != 0 or len(self.ui.labFilePathLine.text()) != 0:
            reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window? \nAll inputs will be clear.', QtWidgets.QMessageBox.Yes,
                                                QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.ui.clientFilePathLine.clear()
                self.ui.labFilePathLine.clear()
                event.accept()  
            else:
                event.ignore() 
        else:
            event.accept() 


class ConfirmWindow(QMainWindow):
    def __init__(self, parent = None):
        super(ConfirmWindow, self).__init__(parent)
        
        # load constants page ui
        self.ui = loadUI(':/ui/run_info.ui', self)


class ConstantsWindow(QMainWindow):
    def __init__(self, parent = None):
        super(ConstantsWindow, self).__init__(parent)
        self.parent = parent 
        # load constants page ui
        self.ui = loadUI(':/ui/constants_page.ui', self)
        # initialize label
        if constant_file_config.default_id:
            self.ui.idLabel.setText(constant_file_config.default_id)
        else:
            self.ui.idLabel.setText("Template")
        # Templete constants file path
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        self.templete_path = os.path.join(base_path, 'constant.xlsx')
        # Table insertion
        self.ui.constantsTable.horizontalHeader().setStyleSheet("QHeaderView { font-size: 12pt; font-family: Verdana; font-weight: bold; }")
        self.constantModel = TableModel(data=pd.DataFrame([]), editable=True)
        self.constant_sortermodel = QSortFilterProxyModel()
        self.constant_sortermodel.setSourceModel(self.constantModel)
        self.ui.constantsTable.setModel(self.constant_sortermodel)
        self.ui.constantsTable.setSortingEnabled(True)
        self.ui.constantsTable.sortByColumn(1, Qt.AscendingOrder)
        self.ui.constantsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.constantsTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ui.constantsTable.selectionModel().selectionChanged.connect(lambda: self.selection_changed())
        self.ui.constantsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.constantsTable.setItemDelegate(AlignDelegate())
        self.ui.constantsTable.setColumnHidden(2, True) #??
        self._selectedSourceIndex = None
        self._selectedConstantsID = ""

        # Context menu
        self.ui.constantsTable.setContextMenuPolicy(Qt.CustomContextMenu) 
        self.ui.constantsTable.customContextMenuRequested.connect(self.showContextMenu)

        # link buttons to function
        # self.openButton.clicked.connect(self.openDefaultConstantsFile)
        self.defaultButton.clicked.connect(self.setDefault)
        self.createButton.clicked.connect(self.create)
        self.deleteButton.clicked.connect(self.delete)
        # link table raw to double click
        # self.ui.constantsTable.doubleClicked.connect(self.openConstantsFile)
        # initiallize table
        self.constantModel.layoutAboutToBeChanged.emit()
        self.constantModel.initialiseTable(data=getConstantsTableData())
        self.constantModel.layoutChanged.emit()
        self.constantModel.dataChanged.connect(self.onDescriptionChanged)


    def onDescriptionChanged(self, tLeft, bRight):
        if self._selectedConstantsID == "Template":
            return
        logger.debug(self.constantModel._data.iloc[tLeft.row(), tLeft.column()])
        ConstantFile[self._selectedConstantsID].note = self.constantModel._data.iloc[tLeft.row(), tLeft.column()]


    def showContextMenu(self):  
        self.ui.constantsTable.contextMenu = QtWidgets.QMenu(self)
        self.ui.constantsTable.contextMenu.setStyleSheet("""
            QMenu:selected {background-color: #ddf; color: #000;}
            """
            )

        def add_action(name, handler):
            action = self.ui.constantsTable.contextMenu.addAction(name)
            action.triggered.connect(lambda: self.actionHandler(handler))
            
        add_action('Open constant.xlsx', "OpenConstantFile")

        self.ui.constantsTable.contextMenu.popup(QtGui.QCursor.pos())  # Menu position based on cursor
        self.ui.constantsTable.contextMenu.show()


    def actionHandler(self, action):
        logger.debug("Open menu")

        if action == "OpenConstantFile":
            self.openConstantsFile()
        
    def openDefaultConstantsFile(self):
        try:
            os.startfile(constant_file_config.get_path())
        except FileNotFoundError:
            QtWidgets.QMessageBox.about(self, "Warning", "No constants file, Please check your path.")

    def openConstantsFile(self):
        if self._selectedConstantsID == "Template":
            os.startfile(self.templete_path)
        else:
            try:
                os.startfile(ConstantFile[self._selectedConstantsID].path)
            except FileNotFoundError:
                QtWidgets.QMessageBox.about(self, "Warning", "No constants file, Please check your path.")

    def setDefault(self):
        # check if chose one row
        if self._selectedConstantsID == "":
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose a constants.")
            return
        # check if choosing template row
        if self._selectedConstantsID == "Template":
            del constant_file_config.default_id
            self.ui.idLabel.setText("Template")
            return
        # set default constants file
        constant_file_config.default_id = ConstantFile[self._selectedConstantsID].id
        # refresh display
        self.ui.idLabel.setText(constant_file_config.default_id)

    def create(self):
        # create constants
        ConstantFile.make()
        # refresh table
        self.constantModel.layoutAboutToBeChanged.emit()
        self.constantModel.initialiseTable(data=getConstantsTableData())
        self.constantModel.layoutChanged.emit()
    
    def delete(self):
        # check if chose one row
        if self._selectedConstantsID == "":
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose a constants.")
            return
        # check if choosing template row
        if self._selectedConstantsID == "Template":
            QtWidgets.QMessageBox.about(self, "Warning", "Sorry, template constants can not be deleted.")
            return
        #pop up confirm window
        if str(self._selectedConstantsID) == constant_file_config.default_id:
            reply = QtWidgets.QMessageBox.question(self, u'Warning', u'You are deleting currently selected file. \nAre you sure you want to proceed? \nAfter deletion, selected file will be set as DEFAULT. ', 
                                               QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        else:
            reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Do you want delete this constants file?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            # delete chosen constants
            try:
                ConstantFile[self._selectedConstantsID].delete()
            except PermissionError:
                QtWidgets.QMessageBox.about(self, "Warning", "Please close the constants file first.")
                return
            # refresh table
            self.constantModel.layoutAboutToBeChanged.emit()
            self.constantModel.initialiseTable(data=getConstantsTableData())
            self.constantModel.layoutChanged.emit()
            self.ui.constantsTable.clearSelection()
            # refresh display
            if constant_file_config.default_id:
                self.ui.idLabel.setText(constant_file_config.default_id)
            else:
                self.ui.idLabel.setText("DEFAULT")
        else:
            self.ui.constantsTable.clearSelection()
            return

    def selection_changed(self):
        """
        Return the index of selected rows in an array.
        """
        modelIndex =self.ui.constantsTable.selectionModel().selectedRows() # QModelIndexList
        self._selectedRows = [idx.row() for idx in modelIndex]
        logger.debug(self._selectedRows)
        if len(self._selectedRows) > 0:
            source_selectedIndex = [self.constant_sortermodel.mapToSource(modelIndex[0]).row()]
            logger.debug(source_selectedIndex)
            self._selectedConstantsID = self.constantModel._data.loc[source_selectedIndex, 'ID'].to_list()[0]
            self._selectedSourceIndex = source_selectedIndex
        elif len(self._selectedRows) == 0:
            self._selectedConstantsID = ""


class AnalyseWindow(QMainWindow):
    def __init__(self, parent = None):
        super(AnalyseWindow, self).__init__(parent)
        
        # load analyse page ui
        # window = loadUI(".\\app\\gui\\analyse_page.ui", self)
        #window = loadUI("./app/gui/analyse_page.ui", self) 
        window = loadUI(':/ui/analyse_page.ui', self)
        self.ui = window
        self._selectedRows = []
        self.runs = []
        self.tabTables = []
        self.lastClicked = []
        self.color = ['b', 'c', 'r', 'm', 'k', 'y']
        self.summay = None
        self.constant = None
        self.parent = parent
        ## Table and Graph insertion
        # self.ui.resultGraph
        # self.ui.run1Table
        # self.ui.run2Table  (This should be dynamic)
        # self.ui.resultTable
        # Result Table
        self.ui.resultTable.horizontalHeader().setStyleSheet("QHeaderView { font-size: 12pt; font-family: Verdana; font-weight: bold; }")       
        self.resultModel = TableModel(pd.DataFrame())
        self.ui.resultTable.setModel(self.resultModel)
        self.ui.resultTable.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        # self.ui.resultTable.selectionModel().selectionChanged.connect(lambda: self.selection_changed('resultTable'))
        self.ui.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.resultTable.setItemDelegate(AlignDelegate()) # text alignment
        # Graph
        self.ui.resultGraph.setBackground(background=None)
        self.plot_item = self.ui.resultGraph.addPlot()
        self.plot_item.setLabel('bottom', "Effective Energy (keV)")
        self.plot_item.setLabel('left', "Calibration Factor (mGy/nc)")
        self.plot_item.addLegend(offset=(-30, 30))
        self.plot_item.showGrid(y=True)
        self.plot_item.setMenuEnabled(False)
        # logger.debug(self.ui.tabWidget.count())
        self.ui.generatePdfButton.clicked.connect(self.generate_pdf)

    def setRuns(self, runs):
        
        self.runs = runs
        result_list = []
        name_list = []
        self.resultModel.layoutAboutToBeChanged.emit()
        for run in runs:
            # get Leakage Current Data of each run
            # get data from resolver
            result = calculator(run.raw_client.path, run.raw_lab.path)
            result_list.append(result)
            self.tabTables.append(result.df_leakage)
            self.leakageCurrentModel = TableModel(result.df_leakage, set_bg=True, bg_index=result.highlight)
            self.tabTable = QTableView()
            self.tabTable.horizontalHeader().setStyleSheet("QHeaderView { font-size: 8pt; font-family: Verdana; font-weight: bold; }")       
            self.tabTable.setModel(self.leakageCurrentModel)
            self.tabTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.ui.tabWidget.addTab(self.tabTable, "Run "+str(run.id))
            name_list.append("Run "+str(run.id))
            self.tabTable.setItemDelegate(AlignDelegate()) # text alignment

            # Draw graph
            self.plot_item.addItem(self.plot(result.X['E_eff'].tolist(), result.df_NK['NK'].tolist(), color=self.color[run.id % len(self.color) - 1], runId=run.id))

        self.constant = result_list[0].df_otherConstant
        self.summay = summary(name_list, result_list)
        self.resultModel.initialiseTable(data=self.summay)
        
        self.resultModel.layoutChanged.emit()
    

    def plot(self, x, y, color, runId):
        scatter_item = pg.ScatterPlotItem(
            size=8,
            pen=pg.mkPen(None),
            brush=pg.mkBrush(color),
            symbol='s',
            hoverable=True,
            hoverSymbol='s',
            hoverSize=12,
            hoverPen=pg.mkPen('r', width=2),
            hoverBrush=pg.mkBrush('g'),
            name="Run " + str(runId),
            # tip='This is a test'.format
            tip='x: {x:.3g}\ny: {y:.3g}'.format
        )
        scatter_item.addPoints(
            x=np.array(x),
            y=np.array(y)
            # size=(np.random.random(n) * 20.).astype(int),
            # brush=[pg.mkBrush(x) for x in np.random.randint(0, 256, (n, 3))],
            # data=np.arange(n)
        )
        # scatter_item.sigClicked.connect(self.clicked)
        # scatter_item.sigHovered.connect(self.hovered)
        return scatter_item
    
    # def clicked(self, plot, points):
    #     for p in self.lastClicked:
    #         p.resetPen()
    #     print("clicked points", points)
    #     for point in points:
    #         print(33333333)
    #         point.setPen(pg.mkPen('b', width=2))
    #     self.lastClicked = points
    
    # def hovered(self, plot, points):
    #     if points:
    #         print(points[0].viewPos())
    def generate_pdf(self):
        # QtWidgets.QMessageBox.about(self, "Generating PDF...")

        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        info_dict = self.gather_info()

        file_name, _ = QFileDialog.getSaveFileName(self, 'Save PDF Report', info_dict["cal_num"] + " MEX " + info_dict["model"] + " sn " + info_dict["serial"], "PDF file (*.pdf)")

        logger.debug(file_name)
        if file_name:
            
            pool = QThreadPool.globalInstance()

            workerSignals = ProgressWorkerSignals()
            worker = PdfWorker(file_name, info_dict, workerSignals, self.summay, self.constant)
            ticker = ProgressBarCounter(workerSignals)   
            progressBar = ProgressBar(self, workerSignals)

            pool.start(worker)
            pool.start(ticker)

            # QtWidgets.QMessageBox.about(self, "Finish!")
            # workerSignals.finished.connect(lambda: self.export_pdf(temp_folder))

    def gather_info(self):

        date_list = []
        ic_hv = []

        equipmentID = self.parent._selectedEquipID
        cal_num = self.parent._selectedCalNum
        client_name = Job[cal_num].client_name
        first_address = Job[cal_num].client_address_1
        second_address = Job[cal_num].client_address_2
        serial = Job[cal_num][equipmentID].serial
        model = Job[cal_num][equipmentID].model

        # Only first operator is considered
        operator = self.runs[0].operator
        for run in self.runs:
            date_list.append(dateutil.parser.isoparse(run.measured_at))
            ic_hv.append(run.IC_HV)

        earliest_date = min(date_list).strftime("%d %b %Y")
        latest_date = max(date_list).strftime("%d %b %Y")

        period = earliest_date + " to " + latest_date
        report_date = datetime.today().strftime("%d %b %Y")

        ichv = ic_hv[0]

        if int(ichv) < 0:
            flag = "(" + ichv + ")" + " on the guard electrode " + "Positive " + "(Central Electrode Negative)"
        else:
            flag = "(" + ichv + ")" + "on the guard electrode " + "Negative " + "(Central Electrode Negative)"

        return deepcopy({"cal_num": cal_num,
                "client_name": client_name,
                "address1": first_address,
                "address2": second_address,
                "model": model,
                "serial": serial,
                "operator": operator,
                "period": period,
                "report_date": report_date,
                "ic_hv": str(ichv) + 'V',
                "polarity": flag
                })
    


    def closeEvent(self, event):  
        self.__init__(self.parent)
        event.accept()           


class AddClientWindow(QMainWindow):

    def __init__(self, parent = None):
        super(AddClientWindow, self).__init__(parent)
        self.parent = parent
    
        # load add client page ui
        # window = loadUI(".\\app\\gui\\add_client_page.ui", self)
        #window = loadUI("./app/gui/add_client_page.ui", self) 
        window = loadUI(':/ui/add_client_page.ui', self)
        self.ui = window
        self.clientName = ""
        self.clientAddress1 = ""
        self.clientAddress2 = ""
        self.calNumber = ""

        self.clientSubmitButton.clicked.connect(self.addNewClient)
        
    def closeEvent(self, event):  
        if len(self.ui.calNumLine.text()) != 0 or len(self.ui.clientNameLine.text()) != 0 or len(self.ui.clientAddress1Line.text()) != 0 or len(self.ui.clientAddress2Line.text()) != 0:
            reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window? \nAll inputs will be clear.', QtWidgets.QMessageBox.Yes,
                                                QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.ui.calNumLine.clear()
                self.ui.clientNameLine.clear()
                self.ui.clientAddress1Line.clear()
                self.ui.clientAddress2Line.clear()
                event.accept()  
            else:
                event.ignore() 
        else:
            event.accept() 
    
    def getNewClientInfo(self):

        newClient = {
            'CAL Number': self.calNumber,
            'Client Name': self.clientName
        }
        return pd.DataFrame(newClient, index=[0]) 

    def addNewClient(self):
        self.parent.clientModel.layoutAboutToBeChanged.emit()
        self.parent.ui.homeTable.clearSelection()
        self.calNumber = self.ui.calNumLine.text()
        self.clientName = self.ui.clientNameLine.text()
        self.clientAddress1 = self.ui.clientAddress1Line.text()
        self.clientAddress2 = self.ui.clientAddress2Line.text()

        # Check duplicated ID
        # IDs = getHomeTableData()['CAL Number'].values.tolist()
        # if self.calNumber in IDs:
        #     QtWidgets.QMessageBox.about(self, "Warning", "CAL number already existed in file system!")
        #     return

        # Check calNumber and clientName are not empty
        if len(self.calNumber)==0 or len(self.clientName)==0:
            QtWidgets.QMessageBox.about(self, "Warning", "Please fill in CAL Number and Client Name!")
            return

        try:
            Job.make(self.calNumber, client_name = self.clientName, client_address_1 = self.clientAddress1, client_address_2 = self.clientAddress2)
        except ValueError:
            QtWidgets.QMessageBox.about(self, "Warning", "CAL number already existed in file system!")
            return

        self.parent.clientModel.addData(self.getNewClientInfo())
        self.parent.clientModel.layoutChanged.emit()
        
        # Finish add new client and quit
        self.hide()
        self.clientName = ""
        self.clientAddress1 = ""
        self.clientAddress2 = ""
        self.calNumber = ""
        self.ui.calNumLine.clear()
        self.ui.clientNameLine.clear()
        self.ui.clientAddress1Line.clear()
        self.ui.clientAddress2Line.clear()
        # TODO: Display another window to confirm information


class AddEquipmentWindow(QMainWindow):
    def __init__(self, parent = None):
        super(AddEquipmentWindow, self).__init__(parent)
        self.parent = parent
        
        # load add equipment page ui
        # window = loadUI(".\\app\\gui\\add_equipment_page.ui", self)
        #window = loadUI("./app/gui/add_equipment_page.ui", self)
        window = loadUI(':/ui/add_equipment_page.ui', self)
        self.ui = window
        self.model = ""
        self.serial = ""
        self.id = ""
        self.job = None
        self.equipmentSubmitButton.clicked.connect(self.addNewEquip)
    
    def getNewEquipInfo(self):
        newEquip = {
            'Make/Model': self.model,
            'Serial Num': self.serial,
            'ID': self.id,
        }
        return pd.DataFrame(newEquip, index=[0]) 
    
    def addNewEquip(self):
        self.parent.equipmentModel.layoutAboutToBeChanged.emit()
        self.model = self.ui.modelLine.text()
        self.serial = self.ui.serialLine.text()
        # TODO: Check duplicated ID
        if len(self.model)==0 or len(self.serial)==0:
            QtWidgets.QMessageBox.about(self, "Warning", "Please fill in Make/Model and Serial!")
            return
        try:
            equip = self.job.add_equipment(model = self.model, serial = self.serial)
        except ValueError:
            QtWidgets.QMessageBox.about(self, "Warning", "Equipment already existed in the Job!")
            return
        self.id = equip.id
        self.parent.equipmentModel.addData(self.getNewEquipInfo())
        self.parent.equipmentModel.layoutChanged.emit()
        
        # Finish add new equipment and quit
        self.hide()
        self.model = ""
        self.serial = ""
        self.id = ""
        self.job = None
        self.ui.modelLine.clear()
        self.ui.serialLine.clear()
        # TODO: Display another window to confirm information

    def closeEvent(self, event):  
        if len(self.ui.modelLine.text()) != 0 or len(self.ui.serialLine.text()) != 0:
            reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window? \nAll inputs will be clear.', QtWidgets.QMessageBox.Yes,
                                                QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.ui.modelLine.clear()
                self.ui.serialLine.clear()
                event.accept()  
            else:
                event.ignore() 
        else:
            event.accept() 


class TableModel(QAbstractTableModel):

    def __init__(self, data, set_bg = False, bg_index=None, editable=False):
        super(TableModel, self).__init__()
        self._data = data
        # May be required to change logic
        # if data.empty is False:
        #     self._display = data.drop(labels=['Address'], axis=1)
        self._bg = set_bg
        self._bgCellIdx = bg_index
        self._editable = editable
    
    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            # Address is at the end of columns
            # if index.column() != self.columnNum - 1:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

        if role == Qt.BackgroundRole:
            if self._bg and (index.row(), index.column()) in self._bgCellIdx:
                return QtGui.QColor('yellow')

    def rowCount(self, index=None):
        return self._data.shape[0]

    def columnCount(self, index=None):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

    def addData(self, newData):
        if newData.empty is False:
            self._data = self._data.convert_dtypes()
            self._data = self._data.append(newData, ignore_index=True)
        else:
            pass

    def delData(self, idx):
        if idx:
            self._data = self._data.drop(idx)
            self._data.reset_index(drop=True, inplace=True)
            logger.debug(self._data)
        else:
            pass
    
    def setData(self, index, value, role):
        if role == Qt.EditRole and self._editable:
            self._data.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index, (Qt.DisplayRole, ))
            return True
        return False

    def initialiseTable(self, data):
    
        self._data = data

    def setHeaderData(self, section, orientation, data, role=Qt.EditRole):
        if orientation == Qt.Horizontal and role in (Qt.DisplayRole, Qt.EditRole):
            try:
                self.horizontalHeaders[section] = data

                return True
            except:
                return False
        return super().setHeaderData(section, orientation, data, role)
    
    def isTableEmpty(self):

        return self._data.empty
    
    def flags(self, index):
        if self._editable and index.column() == 2:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
    # def removeRows(self, position, rows=1, index=QModelIndex()):

    #     self.beginRemoveRows(QModelIndex(), position, position + rows - 1)  
    #     # logger.debug("Drop")     
    #     # logger.debug(self._data.drop(position))
    #     self._data = self._data.drop(position)
    #     self._data.reset_index(drop=True, inplace=True)
    #     self.endRemoveRows()

    #     return True

    '''
    https://stackoverflow.com/questions/28218882/how-to-insert-and-remove-row-from-model-linked-to-qtablevie
    '''
    # def insertRows(self, position, rows=1, index=QModelIndex()):
    #     indexSelected=self.index(position, 0)
    #     itemSelected=indexSelected.data().toPyObject()

    #     self.beginInsertRows(QModelIndex(), position, position + rows - 1)
    #     for row in range(rows):
    #         self.items.insert(position + row,  "%s_%s"% (itemSelected, self.added))
    #         self.added+=1
    #     self.endInsertRows()
    #     return True


class AlignDelegate(QItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignCenter
        QItemDelegate.paint(self, painter, option, index)


class ProgressWorkerSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

class ProgressBarCounter(QRunnable):
    """
    Runs a counter thread.
    """

    def __init__(self, signals: ProgressWorkerSignals):
        super().__init__()
        self._signals = signals
        self._stop = False
        signals.finished.connect(self.stop)

    def run(self):
        count = 0
        while count < 100 and not self._stop:
            count +=10
            time.sleep(1)
            self._signals.progress.emit(count)

    def stop(self):
        self._stop = True

class PdfWorker(QRunnable):
    """
    A thread to handle pdf generation
    """

    def __init__(self, path, info_dict, signals: ProgressWorkerSignals, summary, constant) -> None:
        super().__init__()
        self._info_dict = info_dict
        self._signals = signals
        self._path = path
        self.summary = summary
        self.constant = constant


    def run(self):
        temp_folder = tempfile.mkdtemp(dir=DATA_FOLDER.absolute())
        logger.debug(temp_folder)
        pdf_visualization(temp_folder, self.summary, self.constant)
        pdf = get_pdf(temp_folder, **self._info_dict)

        shutil.copyfile(pdf, self._path)

        try:
            logger.debug('Cleaning temporary folder...')
            shutil.rmtree(temp_folder)
        except OSError as e:
            print ("Error: %s - %s." % (e.filename, e.strerror))

        self._signals.finished.emit()

class ProgressBar(QDialog):
    """
    Simple dialog that consists of a Progress Bar.
    """
    def __init__(self, parent, signals: ProgressWorkerSignals):
        super().__init__(parent)

        self.setWindowTitle('Generating PDF...')
        self.progress = QProgressBar(self)
        self.progress.setGeometry(0, 0, 300, 25)
        self.progress.setMaximum(100)
        # self.button = QPushButton('Finish', self)
        # self.button.move(0, 30)
        # self.button.clicked.connect(self.onFinishButtonClick)
        # self.button.setVisible(False)
        signals.finished.connect(self.onProgressFinish)
        signals.progress.connect(self.onProgressChanged)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        # self.setWindowFlag(QtCore.Qt.WindowTitleHint, False)
        # self.setWindowFlag(QtCore.Qt.WindowSystemMenuHint, False)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.show()

    def onProgressChanged(self, value):
        self.progress.setValue(value)
    
    def onProgressFinish(self):
        self.accept()

def start_event_loop():
    # os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    # sys.argv += ['--style', 'fusion']
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(':/icons/app.ico'))

    mainWindow = MainWindow()
    mainWindow.show()
    return app.exec_()


if __name__ == '__main__':
    ret = start_event_loop()
    sys.exit(ret)