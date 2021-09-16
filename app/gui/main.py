from os import error, name
from typing import Counter
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QTableView, QItemDelegate, QGraphicsScene, QFileDialog
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel
import sys
from numpy import clongdouble, empty
from pandas.io.pytables import Selection, SeriesFixed
import pandas as pd
import pyqtgraph as pg
import os
from pathlib import Path
import logging
import numpy as np

from app.gui.utils import loadUI, getHomeTableData, getEquipmentsTableData, getRunsTableData, getResultData, converTimeFormat
from app.core.models import Job, Equipment
from app.core.resolvers import calculator, result_data, summary
from app.gui import resources

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
    def __init__(self):
        QMainWindow.__init__(self)
        
        # load main window ui
        window = loadUI(':/ui/main_window.ui', self)
        #window = loadUI("./app/gui/main_window.ui", self)
        self.ui = window

        # load other windows
        self.addClientWindow = AddClientWindow(self)
        self.constantsWindow = ConstantsWindow(self)
        self.importWindow = ImportWindow(self)
        self.analysisWindow = AnalyseWindow(self)
        self.addEquipmentWindow = AddEquipmentWindow(self)

        

        #Home Page
        self.ui.homeButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.homePage))
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

        # Return to Client Info Page
        self.ui.returnButton_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.clientInfoPage))
        self.ui.returnButton_2.clicked.connect(lambda: self.ui.runsTable.clearSelection())

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
        self.ui.homeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) #column stretch to window size
        self.ui.homeTable.setItemDelegate(AlignDelegate()) # text alignment


        ## Table insertion
        # Equipment Table
        self.ui.equipmentsTable.horizontalHeader().setStyleSheet("QHeaderView { font-size: 12pt; font-family: Verdana; font-weight: bold; }")
        self.equipmentModel = TableModel(data=pd.DataFrame([]))
        self.ui.equipmentsTable.setModel(self.equipmentModel)
        self.ui.equipmentsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.equipmentsTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ui.equipmentsTable.selectionModel().selectionChanged.connect(lambda: self.selection_changed('equipmentsTable'))
        self.ui.equipmentsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.equipmentsTable.setItemDelegate(AlignDelegate())
        self._selectedEquipID = ""

        # Run Table
        self.ui.runsTable.horizontalHeader().setStyleSheet("QHeaderView { font-size: 12pt; font-family: Verdana; font-weight: bold; }")        
        self.runModel = TableModel(data=pd.DataFrame([]))
        self.ui.runsTable.setModel(self.runModel)
        self.ui.runsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.runsTable.selectionModel().selectionChanged.connect(lambda: self.selection_changed('runsTable'))
        self.ui.runsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.runsTable.setItemDelegate(AlignDelegate())
        self.ui.analyseButton.clicked.connect(lambda: self.ui.runsTable.clearSelection())


        # Change selection behaviour. User can only select rows rather than cells. Single selection
        self.ui.homeTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.homeTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ui.homeTable.selectionModel().selectionChanged.connect(lambda: self.selection_changed('homeTable'))
        self._selectedRows = []
        self._selectedCalNum = ""
    
    def deleteRows(self, tableName):
        # Reverse sort rows indexes
        indexes = sorted(self._selectedRows, reverse=True)

        # Delete rows
        for row_idx in indexes:
            self.clientModel.removeRows(position=row_idx)


    def chooseClient(self):
        """
        Choose one client and goes into client info page.
        When not choosing any of the client, pop up a warning window
        """
        if self._selectedRows:
            self.ui.updateClientButton.setEnabled(False)
            self.ui.stackedWidget.setCurrentWidget(self.ui.clientInfoPage)
            self.ui.homeTable.clearSelection()
        else:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose a Client!")


    def deleteClient(self):
        """
        Delete chosen client on the Home Page by clicking 'delete client' button.
        When not choosing any of the client, pop up a warning window
        """
        if self._selectedRows:
            self.clientModel.layoutAboutToBeChanged.emit()
            self._selectedCalNum = self.clientModel._data.loc[self._selectedRows, 'CAL Number'].to_list()[0]
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
            self._selectedEquipID = self.equipmentModel._data.loc[self._selectedRows, 'ID'].to_list()[0]
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
            selectedRun = self.runModel._data.loc[self._selectedRows, 'ID'].to_list()
            # logger.debug(selectedRun)
            reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Do you want delete selected run or runs?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                for runId in selectedRun:
                    del Job[self._selectedCalNum][self._selectedEquipID].mex[runId]
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
            logger.debug(self._selectedRows)
            if tableName == "homeTable" and self._selectedRows != []:
                self.equipmentModel.layoutAboutToBeChanged.emit()
                source_selectedIndex = [self.proxy_model.mapToSource(modelIndex[0]).row()]
                logger.debug(source_selectedIndex)
                self._selectedCalNum = self.clientModel._data.loc[source_selectedIndex, 'CAL Number'].to_list()[0]
                logger.debug(self._selectedCalNum)
                self.ui.label_CALNum.setText(self._selectedCalNum)
                self.ui.clientNamelineEdit.setText(Job[self._selectedCalNum].client_name)
                self.ui.address1lineEdit.setText(Job[self._selectedCalNum].client_address_1)
                self.ui.address2lineEdit.setText(Job[self._selectedCalNum].client_address_2)
                self.equipmentModel.initialiseTable(data=getEquipmentsTableData(Job[self._selectedCalNum]))
                self.ui.equipmentsTable.setColumnHidden(2, True)
                self.equipmentModel.layoutChanged.emit()
            elif tableName == "equipmentsTable" and self._selectedRows != []:
                self.runModel.layoutAboutToBeChanged.emit()
                self._selectedEquipID = self.equipmentModel._data.loc[self._selectedRows, 'ID'].to_list()[0]
                self.runModel.initialiseTable(data=getRunsTableData(Job[self._selectedCalNum][self._selectedEquipID]))
                self.ui.runsTable.setColumnHidden(2, True)
                self.runModel.layoutChanged.emit()
            # elif tableName == "runsTable" and self._selectedRows != []:

        except AttributeError:
            raise AttributeError("Attribute does not exist! Table name may be altered!")
            
    def openConstantsWindow(self):
        """
        Open constant file instead of open constant window.
        """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        constantFilePath = os.path.join(base_path, 'constant.xlsx')

        try:
            os.startfile(constantFilePath)
        except FileNotFoundError:
            QtWidgets.QMessageBox.about(self, "Warning", "No constants file, Please check your path.")
        

        #self.constantsWindow.show()
    
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
    
    def openAnalysisWindow(self):
        """
        Open analysis window. Pop up warning when not choosing any of the runs.
        """
        try:
            if self._selectedRows:

                selectedRuns = self.runModel._data.loc[sorted(self._selectedRows), 'ID'].to_list()
                runs = list(map(lambda runId:Job[self._selectedCalNum][self._selectedEquipID].mex[runId], selectedRuns))
                self.analysisWindow.setRuns(runs) 
                self.analysisWindow.analyze()
                self._selectedRows = []
            else:
                QtWidgets.QMessageBox.about(self, "Warning", "Please choose at least one run to analyze.")
        except Exception as e:
            logger.error("Can't resolve raw data file!", exc_info=e)
            QtWidgets.QMessageBox.about(self, "Warning", "Can not resolve raw files. Please check the data.")
        
    
    def closeEvent(self, event):  
        reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Do you want to exit?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
        
            event.accept()  
        else:
            event.ignore() 
 
class ClientFilter(QSortFilterProxyModel):
    def __init__(self, parent):
        super(ClientFilter,self).__init__(parent)

    def filterAcceptsRow(self, source_row, source_parent):
        sourceModel = self.sourceModel()
        for i in range(sourceModel._data.shape[0]): # Bad practice
            idx = sourceModel.index(source_row, i, source_parent)
            logger.debug(idx.row())
            logger.debug(idx.column())
            if not idx.isValid():
                logger.debug("Invalid")
                return False
            else:
                logger.debug("Valid")
                return True


class ImportWindow(QMainWindow):
    def __init__(self, parent = None):
        super(ImportWindow, self).__init__(parent)
        self.parent = parent
        
        # load import page ui
        # window = loadUI(".\\app\\gui\\import_page.ui", self)
        #window = loadUI("./app/gui/import_page.ui", self)
        window = loadUI(':/ui/import_page.ui', self)

        self.ui = window
        self.equip = None
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
    
    def getNewRunInfo(self):
        newClient = {
            'ID': [],
            'Added Time': [],
            'Edited Time': []
        }
        return pd.DataFrame(newClient, index=[0]) 
    
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
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose or fill in both Client file and Lab file path.")
            return
        if (not os.path.isfile(self.clientPath)) or (not os.path.isfile(self.labPath)):
            QtWidgets.QMessageBox.about(self, "Warning", "File not found, Please check your file path.")
            return
        run = self.equip.mex.add()
        run.raw_client.upload_from(Path(self.clientPath))
        run.raw_lab.upload_from(Path(self.labPath))
        data = {
            'ID': run.id,
            'Added Time': converTimeFormat(run.added_at),
            'Edited Time': converTimeFormat(run.edited_at),
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
        try:
            os.startfile(self.clientPath)
        except FileNotFoundError:
            QtWidgets.QMessageBox.about(self, "Warning", "File not found, Please check your path.")
    
    def openLabFile(self):
        try:
            os.startfile(self.labPath)
        except FileNotFoundError:
            QtWidgets.QMessageBox.about(self, "Warning", "File not found, Please check your path.")


    def closeEvent(self, event):  
        reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()  
        else:
            event.ignore() 


class ConstantsWindow(QMainWindow):
    def __init__(self, parent = None):
        super(ConstantsWindow, self).__init__(parent)
        
        # load constants page ui
        # window = loadUI(".\\app\\gui\\constants_page.ui", self)
        #window = loadUI("./app/gui/constants_page.ui", self)
        window = loadUI(':/ui/constants_page.ui', self)

        self.ui = window

        ## Table insertion
        # self.ui.constantsTable

    def closeEvent(self, event):  
        reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()  
        else:
            event.ignore() 


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
    
    # def selection_changed(self, tableName):
    #     """
    #     Return the index of selected rows in an array.
    #     """
    #     try:
    #         # Single selection mode
    #         idx = getattr(self, tableName).selectionModel().selectedIndexes()[0]
    #         logger.debug(idx.row(), idx.column())
    #         # self._selectedRows = [idx.row() for idx in getattr(self, tableName).selectionModel().selectedIndexes()]
    #     except AttributeError:
    #         logger.error("Attribute does not exist! Table name may be altered!")
    #         raise AttributeError("Attribute does not exist! Table name may be altered!")
    #     logger.debug(self._selectedRows)

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

        self.resultModel.initialiseTable(data=summary(name_list, result_list))
        self.resultModel.layoutChanged.emit()


        
    def analyze(self):
        # TODO: insert analyze functions here
        logger.debug(self.runs)
        self.setWindowModality(Qt.ApplicationModal)
        self.show()
        return

    def closeEvent(self, event):  
        reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.__init__()
            event.accept()  
        else:
            event.ignore() 

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
        reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.ui.calNumLine.clear()
            self.ui.clientNameLine.clear()
            self.ui.clientAddress1Line.clear()
            self.ui.clientAddress2Line.clear()
            event.accept()  
        else:
            event.ignore() 
    
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
        reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.ui.modelLine.clear()
            self.ui.serialLine.clear()
            event.accept()  
        else:
            event.ignore() 


class TableModel(QAbstractTableModel):

    def __init__(self, data, set_bg = False, bg_index=None):
        super(TableModel, self).__init__()
        self._data = data
        # May be required to change logic
        # if data.empty is False:
        #     self._display = data.drop(labels=['Address'], axis=1)
        self._bg = set_bg
        self._bgCellIdx = bg_index
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
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
    
    def setData(self, index, value):
        self._data.iloc[index.row(), index.column()] = value
        return True

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