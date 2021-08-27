from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QRadioButton, QWidget, QDesktopWidget, QTableWidgetItem, QHeaderView, QDockWidget, QTableWidget
from datetime import datetime
import datetime
import sys

# GUI FILE
from sprint1_john import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        def center(self):
            frameGm = self.frameGeometry()
            screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
            centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
            frameGm.moveCenter(centerPoint)
            self.move(frameGm.topLeft())

        # PAGES
        ########################################################################

        #Home Page
        self.ui.homeButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.home_page))
        # Add New Client
        self.ui.addButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.add_page))
        # View/Edit Client Info 
        self.ui.viewButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.viewclientinfo_page))
        #Add New Equipment
        self.ui.addnewequipmentButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.addequipment_page))
        # View/Edit Equipment
        self.ui.viewequipmentButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.viewequipment_page))

        #compare page
        self.ui.compareButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.compare_page))

        self.ui.importButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.import_page))

        self.ui.analyseButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.analyse_page))

        self.ui.constantButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.constants_page))




        ## Home Page Table UI Design
        # Stretch column to fix window size
        #can do a for loop next time -> length?
        header = self.ui.homeTable.horizontalHeader()      
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        clientHeader = self.ui.clientTable.horizontalHeader()
        clientHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        clientHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        clientHeader.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        compareHeader = self.ui.compareTable.horizontalHeader()
        compareHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        compareHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        compareHeader.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        compareHeader.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)

        analysisHeader = self.ui.analysisTable.horizontalHeader()
        analysisHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        analysisHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        summaryHeader = self.ui.summaryTable.horizontalHeader()
        summaryHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        summaryHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        summaryHeader.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        summaryHeader.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        summaryHeader.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        summaryHeader.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        summaryHeader.setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)
        summaryHeader.setSectionResizeMode(7, QtWidgets.QHeaderView.Stretch)
        summaryHeader.setSectionResizeMode(8, QtWidgets.QHeaderView.Stretch)


        constantsHeader = self.ui.constantTable.verticalHeader()
        constantsHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        constantsHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        constantsHeader.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        constantsHeader.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)        
        constantsHeader.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)         



        calNumber=["12123NN", "!@1233123"]
        clientName = ["John", "Winnie"]

        self.ui.homeTable.setRowCount(len(calNumber)) #have to do this else won't work
        self.ui.homeTable.setColumnCount(3)#have to do this else won't work | Use cal number as it will not be empty but client name will

        for i in range(len(calNumber)):
            self.ui.homeTable.setItem(i,1,QTableWidgetItem(calNumber[i]))
            self.ui.homeTable.setItem(i,2,QTableWidgetItem(clientName[i]))

        ## SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        ## ==> END ##




if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())