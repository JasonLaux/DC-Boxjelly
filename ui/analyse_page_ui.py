# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\analyse_page.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_analyse_page(object):
    def setupUi(self, analyse_page):
        analyse_page.setObjectName("analyse_page")
        analyse_page.resize(1209, 865)
        self.centralwidget = QtWidgets.QWidget(analyse_page)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("SimSun-ExtB")
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout_6.addWidget(self.label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.graph_2 = QtWidgets.QGraphicsView(self.widget)
        self.graph_2.setObjectName("graph_2")
        self.horizontalLayout_2.addWidget(self.graph_2)
        self.tabWidget_2 = QtWidgets.QTabWidget(self.widget)
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.run_3 = QtWidgets.QWidget()
        self.run_3.setObjectName("run_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.run_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.run1_table_2 = QtWidgets.QTableView(self.run_3)
        self.run1_table_2.setObjectName("run1_table_2")
        self.gridLayout_4.addWidget(self.run1_table_2, 0, 0, 1, 1)
        self.tabWidget_2.addTab(self.run_3, "")
        self.run_4 = QtWidgets.QWidget()
        self.run_4.setObjectName("run_4")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.run_4)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.run2_table_2 = QtWidgets.QTableView(self.run_4)
        self.run2_table_2.setObjectName("run2_table_2")
        self.gridLayout_5.addWidget(self.run2_table_2, 0, 0, 1, 1)
        self.tabWidget_2.addTab(self.run_4, "")
        self.horizontalLayout_2.addWidget(self.tabWidget_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.result_table = QtWidgets.QTableView(self.widget)
        self.result_table.setObjectName("result_table")
        self.verticalLayout.addWidget(self.result_table)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.generate_pdf_button = QtWidgets.QPushButton(self.widget)
        self.generate_pdf_button.setStyleSheet("QPushButton{\n"
"background-color: rgb(211, 213, 213);\n"
"color:black;\n"
"border-style:outset;\n"
"border-width:2px;\n"
"border-radius:10px;\n"
"border-color: black;\n"
"font:bold 20px;\n"
"padding: 6;\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"background-color: rgb(83, 82, 82);\n"
"color: white;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"background-color: white;\n"
"}\n"
"")
        self.generate_pdf_button.setObjectName("generate_pdf_button")
        self.horizontalLayout_3.addWidget(self.generate_pdf_button)
        self.generate_dcc_button = QtWidgets.QPushButton(self.widget)
        self.generate_dcc_button.setStyleSheet("QPushButton{\n"
"background-color: rgb(211, 213, 213);\n"
"color:black;\n"
"border-style:outset;\n"
"border-width:2px;\n"
"border-radius:10px;\n"
"border-color: black;\n"
"font:bold 20px;\n"
"padding: 6;\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"background-color: rgb(83, 82, 82);\n"
"color: white;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"background-color: white;\n"
"}\n"
"")
        self.generate_dcc_button.setObjectName("generate_dcc_button")
        self.horizontalLayout_3.addWidget(self.generate_dcc_button)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.gridLayout_6.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)
        analyse_page.setCentralWidget(self.centralwidget)

        self.retranslateUi(analyse_page)
        self.tabWidget_2.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(analyse_page)

    def retranslateUi(self, analyse_page):
        _translate = QtCore.QCoreApplication.translate
        analyse_page.setWindowTitle(_translate("analyse_page", "Analysis"))
        self.label.setText(_translate("analyse_page", "Analysis"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.run_3), _translate("analyse_page", "Run 1"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.run_4), _translate("analyse_page", "Run 2"))
        self.generate_pdf_button.setText(_translate("analyse_page", "Generate PDF"))
        self.generate_dcc_button.setText(_translate("analyse_page", "Generate DCC"))