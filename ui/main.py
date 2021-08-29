from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QTableView, QItemDelegate
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel
import sys
from utils import loadUI

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
        # load main window ui
        window = loadUI("main_window.ui", self)
        self.ui = window

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
        
        #Dynamic search
        calNumber = ["Cal Number1", "Cal Number2", "Cal Number3"] 
        clientName = ["Adams", "Peter", "James"]
        dataList = []
        for i in range(len(calNumber)):
            dataList.append(['',calNumber[i],clientName[i]])

        self.model = TableModel(dataList)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(-1) # Search all columns.
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.ui.searchBar.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.ui.homeTable.setModel(self.proxy_model)
        for i in range(3):
            self.ui.homeTable.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch) #column stretch to window size
        self.ui.homeTable.setItemDelegate(AlignDelegate()) # text alignment


        ## Table insertion
        # self.ui.jobsTable
        # self.ui.equipmentsTable
        # self.ui.runsTable

    # define open window functions
    def openConstantsWindow(self):
        constantsWindow.show()
    
    def openAddClientWindow(self):
        addClientWindow.show()

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
        
        # load add client page ui
        window = loadUI("add_client_page.ui", self)
        self.ui = window

    def closeEvent(self, event):  
        reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()  
        else:
            event.ignore() 


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
        super().__init__()
        self._data = data
        self.horizontalHeaders = [''] * 3
        self.setHeaderData(0, Qt.Horizontal, "SELECT")
        self.setHeaderData(1, Qt.Horizontal, "CAL NUMBER")
        self.setHeaderData(2, Qt.Horizontal, "CLIENT NAME")

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return self.horizontalHeaders[section]
            except:
                pass
        return super().headerData(section, orientation, role)

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
    addClientWindow = AddClientWindow()
    addEquipmentWindow = AddEquipmentWindow()
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())