from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QRadioButton, QWidget, QDesktopWidget, QTableWidgetItem, QHeaderView, QDockWidget, QTableWidget
from datetime import datetime
import datetime
import sys

# GUI FILE
from main_window_ui import Ui_MainWindow
from import_page_ui import Ui_import_page
from constants_page_ui import Ui_constants_page
from analyse_page_ui import Ui_analyse_page
from add_client_page_ui import Ui_add_client_page
from add_equipment_page_ui import Ui_add_equipment_page

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Home Page
        self.ui.homeButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.home_page))
        # View/Edit Client Info 
        self.ui.viewButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.viewclientinfo_page))
        #compare page
        self.ui.compareButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.compare_page))
        # Return to Home Page
        self.ui.returnButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.home_page))
        # Return to Client Info Page
        self.ui.returnButton_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.viewclientinfo_page))
        
        ## Table insertion

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
        self.ui = Ui_import_page()
        self.ui.setupUi(self)
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
        self.ui = Ui_constants_page()
        self.ui.setupUi(self)

        ## Table insertion


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
        self.ui = Ui_analyse_page()
        self.ui.setupUi(self)

        ## Table insertion


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
        self.ui = Ui_add_client_page()
        self.ui.setupUi(self)
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
        self.ui = Ui_add_equipment_page()
        self.ui.setupUi(self)
    def closeEvent(self, event):  
        reply = QtWidgets.QMessageBox.question(self, u'Warning', u'Close window?', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()  
        else:
            event.ignore() 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    constantsWindow = ConstantsWindow()
    importWindow = ImportWindow()
    analysisWindow = AnalyseWindow()
    addClientWindow = AddClientWindow()
    addEquipmentWindow = AddEquipmentWindow()
    sys.exit(app.exec_())