from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QTableView, QItemDelegate
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel
import sys

from pandas.io.pytables import SeriesFixed
from utils import loadUI, getHomeTableData
import pandas as pd

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
        # load main window ui
        window = loadUI("main_window.ui", self)
        self.ui = window
        self.addClientWindow = AddClientWindow(self)

        #Home Page
        self.ui.homeButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.homePage))
        # View/Edit Client Info 
        self.ui.chooseClientButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.clientInfoPage))
        #compare page
        self.ui.chooseEquipmentButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.equipmentInfoPage))
        # Return to Home Page
        self.ui.returnButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.homePage))
        # Return to Client Info Page
        self.ui.returnButton_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.clientInfoPage))
        # Delete client
        self.ui.deleteClientButton.clicked.connect(self.deleteClient)
        
        #Dynamic search
        # calNumber = ["Cal Number1", "Cal Number2", "Cal Number3"] 
        # clientName = ["Adams", "Peter", "James"]
        # dataList = []
        # for i in range(len(calNumber)):
        #     dataList.append(['',calNumber[i],clientName[i]])

        self.clientModel = TableModel(data=getHomeTableData())
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(-1) # Search all columns.
        self.proxy_model.setSourceModel(self.clientModel)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.ui.searchBar.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.ui.homeTable.setModel(self.proxy_model)
        for i in range(3):
            self.ui.homeTable.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch) #column stretch to window size
        self.ui.homeTable.setItemDelegate(AlignDelegate()) # text alignment


        ## Table insertion

        # Change selection behaviour. User can only select rows rather than cells
        self.homeTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.homeTable.selectionModel().selectionChanged.connect(self.selection_changed)
        self._selectedRows = []

    def deleteClient(self):
        if self._selectedRows:
            # Indexes is a list of a single item in single-select mode.
            # Remove the item and refresh.
            self.clientModel.delData(self._selectedRows)
            # time.sleep(0.2)
            self.clientModel.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            self.ui.homeTable.clearSelection()
            print(self.clientModel._data)
        else:
            pass

    # Return the index of selected rows in an array
    def selection_changed(self):
        self._selectedRows = [idx.row() for idx in self.homeTable.selectionModel().selectedRows()]
        print(self._selectedRows)

    # define open window functions
    def openConstantsWindow(self):
        constantsWindow.show()
    
    def openAddClientWindow(self):
        
        self.addClientWindow.show()
    

    def openAddEquipmentWindow(self):
        addEquipmentWindow.show()

    def openImportWindow(self):
        importWindow.show()
    
    def openAnalysisWindow(self):
        analysisWindow.show()
    
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
        
        # load import page ui
        window = loadUI("import_page.ui", self)
        self.ui = window

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
        window = loadUI("constants_page.ui", self)
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
        window = loadUI("analyse_page.ui", self)
        self.ui = window

        ## Table and Graph insertion
        # self.ui.resultGraph
        # self.ui.run1Table
        # self.ui.run2Table  (This should be dynamic)
        # self.ui.resultTable

    def closeEvent(self, event):  
        reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()  
        else:
            event.ignore() 


class AddClientWindow(QMainWindow):

    def __init__(self, parent = None):
        super(AddClientWindow, self).__init__(parent)
        self.parent = parent
    
        # load add client page ui
        window = loadUI("add_client_page.ui", self)
        self.ui = window
        self.clientName = ""
        self.clientAddress = ""
        self.calNumber = ""

        self.submitButton.pressed.connect(self.setNewClientInfo)
        
    def closeEvent(self, event):  
        reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()  
        else:
            event.ignore() 
    
    def getNewClientInfo(self):

        newClient = {
            'status': False,
            'CAL Number': self.calNumber,
            'Client Name': self.clientName,
            'Client Address': self.clientAddress
        }
        return pd.DataFrame(newClient, index=[0])

    def setNewClientInfo(self):
        self.clientName = self.ui.clientNameLine.text()
        self.clientAddress = self.ui.clientAddressLine.text()
        self.calNumber = self.ui.calNumLine.text()

        print(self.getNewClientInfo())
        self.parent.clientModel.addData(self.getNewClientInfo())
        self.parent.clientModel.layoutChanged.emit()
        
        self.hide()
        # TODO: Display another window to confirm information


class AddEquipmentWindow(QMainWindow):
    def __init__(self, parent = None):
        super(AddEquipmentWindow, self).__init__(parent)
        
        # load add equipment page ui
        window = loadUI("add_equipment_page.ui", self)
        self.ui = window

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
        self.columnNum = self.columnCount()
        print(1)
        print(data)
    
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

        
    def setHeaderData(self, section, orientation, data, role=Qt.EditRole):
        if orientation == Qt.Horizontal and role in (Qt.DisplayRole, Qt.EditRole):
            try:
                self.horizontalHeaders[section] = data

                return True
            except:
                return False
        return super().setHeaderData(section, orientation, data, role)


class AlignDelegate(QItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignCenter
        QItemDelegate.paint(self, painter, option, index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    constantsWindow = ConstantsWindow()
    importWindow = ImportWindow()
    analysisWindow = AnalyseWindow()
    # addClientWindow = AddClientWindow()
    addEquipmentWindow = AddEquipmentWindow()
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())