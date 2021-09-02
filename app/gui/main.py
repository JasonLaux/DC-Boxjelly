from os import error
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHeaderView, QTableView, QItemDelegate, QGraphicsScene, QFileDialog
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel, QAbstractItemModel, QModelIndex
import sys
from numpy import empty
from pandas.io.pytables import SeriesFixed
from app.gui.utils import loadUI, getHomeTableData, getEquipmentsTableData, getRunsTableData, getResultData, getLeakageCurrentData
import pandas as pd
import pyqtgraph as pg
from app.core.models import Job, Equipment
import os
from pathlib import Path


'''
#Run UI main file under root dir
py -m app.gui.main
'''
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
        # load main window ui
        window = loadUI(".\\app\\gui\\main_window.ui", self)
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
        self.ui.updateClientButton.setEnabled(False)
        self.ui.updateClientButton.clicked.connect(self.updateClientInfo)
        self.ui.clientNamelineEdit.editingFinished.connect(lambda: self.ui.updateClientButton.setEnabled(True))
        self.ui.address1lineEdit.editingFinished.connect(lambda: self.ui.updateClientButton.setEnabled(True))
        self.ui.address2lineEdit.editingFinished.connect(lambda: self.ui.updateClientButton.setEnabled(True))

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
        # Delete equipment
        self.ui.deleteEquipmentButton.clicked.connect(self.deleteEquipment)
        # Delete run
        self.ui.deleteRunButton.clicked.connect(self.deleteRun)
        
        
        #Dynamic search

        # calNumber = ["Cal Number1", "Cal Number2", "Cal Number3"] 
        # clientName = ["Adams", "Peter", "James"]
        # dataList = []
        # for i in range(len(calNumber)):
        #     dataList.append(['',calNumber[i],clientName[i]])

        self.ui.homeTable.horizontalHeader().setStyleSheet("QHeaderView { font-size: 16pt; font-family: Verdana; font-weight: bold;  border: 0.5px solid black; }")
        self.clientModel = TableModel(data=getHomeTableData())

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(-1) # Search all columns.
        self.proxy_model.setSourceModel(self.clientModel)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.ui.searchBar.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.ui.homeTable.setModel(self.clientModel)
        self.ui.homeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) #column stretch to window size
        self.ui.homeTable.setItemDelegate(AlignDelegate()) # text alignment


        ## Table insertion
        # Equipment Table
        self.ui.equipmentsTable.horizontalHeader().setStyleSheet("QHeaderView { font-size: 16pt; font-family: Verdana; font-weight: bold;  border: 0.5px solid black; }")
        self.equipmentModel = TableModel(data=pd.DataFrame([]))
        self.ui.equipmentsTable.setModel(self.equipmentModel)
        self.ui.equipmentsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.equipmentsTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ui.equipmentsTable.selectionModel().selectionChanged.connect(lambda: self.selection_changed('equipmentsTable'))
        self.ui.equipmentsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.equipmentsTable.setItemDelegate(AlignDelegate())
        self._selectedEquipID = ""

        # Run Table
        self.ui.runsTable.horizontalHeader().setStyleSheet("QHeaderView { font-size: 16pt; font-family: Verdana; font-weight: bold;  border: 0.5px solid black; }")        
        self.runModel = TableModel(data=pd.DataFrame([]))
        self.ui.runsTable.setModel(self.runModel)
        self.ui.runsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.runsTable.selectionModel().selectionChanged.connect(lambda: self.selection_changed('runsTable'))
        self.ui.runsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.runsTable.setItemDelegate(AlignDelegate())


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


    # choose one client and goes into client info page
    def chooseClient(self):
        if self._selectedRows:
            self.ui.stackedWidget.setCurrentWidget(self.ui.clientInfoPage)
            self.ui.homeTable.clearSelection()
        # when not choosing any of the client, pop up a warning window
        else:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose a Client!")

    # delete chosen client on the Home Page by clicking 'delete client' button
    def deleteClient(self):
        if self._selectedRows:
            self._selectedCalNum = self.clientModel._data.loc[self._selectedRows, 'CAL Number'].to_list()[0]
            reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Do you want delete this client?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                del Job[self._selectedCalNum] 

                self.clientModel.initialiseTable(data=getHomeTableData())
                self.clientModel.layoutChanged.emit()

            self.ui.homeTable.clearSelection()
        # when not choosing any of the client, pop up a warning window
        else:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose a client to delete.")
    
    # Update client info on the Client Info Page by clicking 'update' button
    def updateClientInfo(self):

        self.ui.updateClientButton.setEnabled(False)

        newClientName = self.ui.clientNamelineEdit.text()
        newFstAddress = self.ui.address1lineEdit.text()
        newSndAddress = self.ui.address2lineEdit.text()
        error = False

        if newClientName or newFstAddress or newSndAddress:
            try: 
                Job[self._selectedCalNum].client_name = newClientName
                Job[self._selectedCalNum].client_address_1 = newFstAddress
                Job[self._selectedCalNum].client_address_2 = newSndAddress
            except AttributeError:
                error = True
                raise error("Job ID is not found!")
            if error is False:
                # Update client info on the Home Page
                self.clientModel.initialiseTable(data=getHomeTableData())
                self.clientModel.layoutChanged.emit()
        else:
            print("No need to update any client info")
            


    # choose one equipment and goes into Equipment info page
    def chooseEquipment(self):
        if self._selectedRows:
            self.ui.stackedWidget.setCurrentWidget(self.ui.equipmentInfoPage)
            self._selectedRows = []

            # Display the equipment info
            self.ui.label_eqCAL.setText(self._selectedCalNum)
            self.ui.label_eqCN.setText(Job[self._selectedCalNum].client_name)
            self.ui.label_eqSN.setText(Job[self._selectedCalNum][self._selectedEquipID].serial)
            self.ui.label_eqMN.setText(Job[self._selectedCalNum][self._selectedEquipID].model)
            self.ui.equipmentsTable.clearSelection()
        # when not choosing any of the equipments, pop up a warning window
        else:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose an Equipment!")
    # delete chosen equipment on the Client Info Page by clicking 'delete equipment' button
    def deleteEquipment(self):
        if self._selectedRows:
            self._selectedEquipID = self.equipmentModel._data.loc[self._selectedRows, 'ID'].to_list()[0]
            reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Do you want delete this Equipment?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                del Job[self._selectedCalNum][self._selectedEquipID]
                self.equipmentModel.initialiseTable(data=getEquipmentsTableData(Job[self._selectedCalNum]))
                self.equipmentModel.layoutChanged.emit()
            self._selectedRows = []
        # when not choosing any of the equipment, pop up a warning window
        else:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose a client to delete.")

    # delete chosen run on the Client Info Page by clicking 'delete run' button
    def deleteRun(self):
        if self._selectedRows:
            self._selectedRun = self.runModel._data.loc[self._selectedRows, 'ID'].to_list()[0]
            reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Do you want delete this run?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                del Job[self._selectedCalNum][self._selectedEquipID].mex[self._selectedRun]
                self.runModel.initialiseTable(data=getRunsTableData(Job[self._selectedCalNum][self._selectedEquipID]))
                self.runModel.layoutChanged.emit()
            self._selectedRows = []
        # when not choosing any of the equipment, pop up a warning window
        else:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose a run to delete.")

    # Return the index of selected rows in an array
    def selection_changed(self, tableName):
        try:
            # TODO Order is based on the selection. Need to sort first?
            self._selectedRows = [idx.row() for idx in getattr(self, tableName).selectionModel().selectedRows()]
            print(self._selectedRows)
            if tableName == "homeTable" and self._selectedRows != []:
                self._selectedCalNum = self.clientModel._data.loc[self._selectedRows, 'CAL Number'].to_list()[0]
                self.ui.label_CALNum.setText(self._selectedCalNum)
                self.ui.clientNamelineEdit.setText(Job[self._selectedCalNum].client_name)
                self.ui.address1lineEdit.setText(Job[self._selectedCalNum].client_address_1)
                self.ui.address2lineEdit.setText(Job[self._selectedCalNum].client_address_2)

                self.equipmentModel.initialiseTable(data=getEquipmentsTableData(Job[self._selectedCalNum]))
                self.equipmentModel.layoutChanged.emit()
            elif tableName == "equipmentsTable" and self._selectedRows != []:
                self._selectedEquipID = self.equipmentModel._data.loc[self._selectedRows, 'ID'].to_list()[0]
                self.runModel.initialiseTable(data=getRunsTableData(Job[self._selectedCalNum][self._selectedEquipID]))
                self.runModel.layoutChanged.emit()
            # elif tableName == "runsTable" and self._selectedRows != []:

        except AttributeError:
            raise AttributeError("Attribute does not exist! Table name may be altered!")
            

    # define open window functions
    def openConstantsWindow(self):
        self.constantsWindow.show()
    
    def openAddClientWindow(self):
        self.addClientWindow.setFixedSize(850, 320)
        self.addClientWindow.show()
    
    def openAddEquipmentWindow(self):
        self.addEquipmentWindow.setFixedSize(850, 320)
        self.addEquipmentWindow.show()
        self.addEquipmentWindow.job = Job[self._selectedCalNum]

    def openImportWindow(self):
        self.importWindow.setFixedSize(850, 320)
        self.importWindow.show()
        self.importWindow.equip = Job[self._selectedCalNum][self._selectedEquipID]
    
    def openAnalysisWindow(self):
        # Pop up warning when not choosing any of the runs
        if self._selectedRows:
            self._selectedRuns = self.runModel._data.loc[self._selectedRows, 'ID'].to_list()
            runs = list(map(lambda runId:Job[self._selectedCalNum][self._selectedEquipID].mex[runId], self._selectedRuns))
            self.analysisWindow.setRuns(runs) 
            self.analysisWindow.analyze()
            self._selectedRows = []
        else:
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose at least one run to analyze.")
        
    
    def closeEvent(self, event):  
        reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Do you want to exit?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
        
            event.accept()  
        else:
            event.ignore() 
    

class ImportWindow(QMainWindow):
    def __init__(self, parent = None):
        super(ImportWindow, self).__init__(parent)
        self.parent = parent
        
        # load import page ui
        window = loadUI(".\\app\\gui\\import_page.ui", self)
        #window = loadUI("./app/gui/import_page.ui", self)
        self.ui = window
        self.equip = None
        self.clientPath = ""
        self.labPath = ""
        self.importClientFilebutton.pressed.connect(self.chooseRawClient)
        self.importLabFileButton.pressed.connect(self.chooseRawLab)
        self.importSubmitButton.pressed.connect(self.addNewRun)
    
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
        print("Client raw file: ", self.clientPath)
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
        print("Lab raw file: ", self.labPath)
        self.ui.labFilePathLine.setText(self.labPath)

    def addNewRun(self):
        if (not os.path.isfile(self.clientPath)) or (not os.path.isfile(self.labPath)):
            QtWidgets.QMessageBox.about(self, "Warning", "Please choose both Client raw file and Lab raw file!")
            return
        run = self.equip.mex.add()
        run.raw_client.upload_from(Path(self.clientPath))
        run.raw_lab.upload_from(Path(self.labPath))
        data = {
            'ID': run.id,
            'Added Time': run.added_at,
            'Edited Time': run.edited_at,
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
        window = loadUI(".\\app\\gui\\constants_page.ui", self)
        #window = loadUI("./app/gui/constants_page.ui", self)        
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
        window = loadUI(".\\app\\gui\\analyse_page.ui", self)
        #window = loadUI("./app/gui/analyse_page.ui", self)        
        self.ui = window
        self._selectedRows = []
        self.runs = []
        self.tabTables = []

        ## Table and Graph insertion
        # self.ui.resultGraph
        # self.ui.run1Table
        # self.ui.run2Table  (This should be dynamic)
        # self.ui.resultTable
        # Result Table
        self.resultModel = TableModel(data=getResultData())
        self.ui.resultTable.setModel(self.resultModel)
        self.ui.resultTable.selectionModel().selectionChanged.connect(lambda: self.selection_changed('resultTable'))
        self.ui.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Graph
        scene = QGraphicsScene()
        self.ui.resultGraph.setScene(scene)
        self.plotWdgt = pg.PlotWidget()
        self.plotWdgt.setBackground('w')
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        plot_item = self.plotWdgt.plot(data, pen=pg.mkPen(width=15))
        proxy_widget = scene.addWidget(self.plotWdgt)

        # Tab and table
        print(self.ui.tabWidget.count())
    
    # Return the index of selected rows in an array
    def selection_changed(self, tableName):
        try:
            # Single selection mode
            idx = getattr(self, tableName).selectionModel().selectedIndexes()[0]
            print(idx.row(), idx.column())
            # self._selectedRows = [idx.row() for idx in getattr(self, tableName).selectionModel().selectedIndexes()]
        except AttributeError:
            print("Attribute does not exist! Table name may be altered!")
            raise AttributeError("Attribute does not exist! Table name may be altered!")
        print(self._selectedRows)
    
    def setRuns(self, runs):
        self.runs = runs
        for run in runs:
            # get Leakage Current Data of each run
            data = getLeakageCurrentData()
            self.tabTables.append(data)
            self.leakageCurrentModel = TableModel(data)
            self.tabTable = QTableView()
            self.tabTable.setModel(self.leakageCurrentModel)
            self.tabTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.ui.tabWidget.addTab(self.tabTable, "Run "+str(run.id))
        
    def analyze(self):
        # TODO: insert analyze functions here
        print(self.runs)
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


class AddClientWindow(QMainWindow):

    def __init__(self, parent = None):
        super(AddClientWindow, self).__init__(parent)
        self.parent = parent
    
        # load add client page ui
        window = loadUI(".\\app\\gui\\add_client_page.ui", self)
        #window = loadUI("./app/gui/add_client_page.ui", self)        
        self.ui = window
        self.clientName = ""
        self.clientAddress1 = ""
        self.clientAddress2 = ""
        self.calNumber = ""

        self.clientSubmitButton.pressed.connect(self.addNewClient)
        
    def closeEvent(self, event):  
        reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
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
        self.calNumber = self.ui.calNumLine.text()
        self.clientName = self.ui.clientNameLine.text()
        self.clientAddress1 = self.ui.clientAddress1Line.text()
        self.clientAddress2 = self.ui.clientAddress2Line.text()

        # Check duplicated ID
        IDs = getHomeTableData()['CAL Number'].values.tolist()
        if self.calNumber in IDs:
            QtWidgets.QMessageBox.about(self, "Warning", "CAL number already existed in file system!")
            return

        # Check calNumber and clientName are not empty
        if len(self.calNumber)==0 or len(self.clientName)==0:
            QtWidgets.QMessageBox.about(self, "Warning", "Please fill in CAL Number and Client Name!")
            return

        Job.make(self.calNumber, client_name = self.clientName, client_address_1 = self.clientAddress1, client_address_2 = self.clientAddress2)
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
        window = loadUI(".\\app\\gui\\add_equipment_page.ui", self)
        #window = loadUI("./app/gui/add_equipment_page.ui", self)        
        self.ui = window
        self.model = ""
        self.serial = ""
        self.id = ""
        self.job = None
        self.equipmentSubmitButton.pressed.connect(self.addNewEquip)
    
    def getNewEquipInfo(self):
        newEquip = {
            'Make/Model': self.model,
            'Serial Num': self.serial,
            'ID': self.id,
        }
        return pd.DataFrame(newEquip, index=[0]) 
    
    def addNewEquip(self):
        self.model = self.ui.modelLine.text()
        self.serial = self.ui.serialLine.text()
        # TODO: Check duplicated ID
        if len(self.model)==0 or len(self.serial)==0:
            QtWidgets.QMessageBox.about(self, "Warning", "Please fill in Make/Model and Serial!")
            return
        equip = self.job.add_equipment(model = self.model, serial = self.serial)
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
            event.accept()  
        else:
            event.ignore() 


class TableModel(QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        # May be required to change logic
        # if data.empty is False:
        #     self._display = data.drop(labels=['Address'], axis=1)
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            # Address is at the end of columns
            # if index.column() != self.columnNum - 1:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

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
            print("Add data...")
            print(newData)
            self._data = self._data.append(newData, ignore_index=True)
            print(self._data)
        else:
            pass

    def delData(self, idx):
        if idx:
            self._data = self._data.drop(idx)
            self._data.reset_index(drop=True, inplace=True)
            print(self._data)
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
    
    # def removeRows(self, position, rows=1, index=QModelIndex()):

    #     self.beginRemoveRows(QModelIndex(), position, position + rows - 1)  
    #     # print("Drop")     
    #     # print(self._data.drop(position))
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
    mainWindow = MainWindow()
    mainWindow.show()
    return app.exec_()

if __name__ == '__main__':
    ret = start_event_loop()
    sys.exit(ret)