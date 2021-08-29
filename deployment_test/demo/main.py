from os import error
import sys
from typing import Any, List
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QModelIndex
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
import numpy as np
from datetime import datetime
import pathlib
import time
from functools import partial


qt_creator_file = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)

class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data=None):
        super(TableModel, self).__init__()
        self.header_labels = ['Edit Date', 'Client File', 'Lab File']
        self._data = data
    
    def data(self, index: QModelIndex, role: Any) -> Any:
        # If View request DisplayRole, then return data
        if role == Qt.DisplayRole:
            value = self._data[index.row(), index.column()]
            if isinstance(value, datetime):
                return value.strftime('%Y-%m-%d')
            return str(value)
        
        if role == Qt.DecorationRole:
            print('Decoration:', index.row(), index.column())
            value = self._data[index.row(), index.column()]
            if isinstance(value, datetime):
                return QtGui.QIcon('calendar.jpg')

    def rowCount(self, _):
        return self._data.shape[0]

    def columnCount(self, _):
        return self._data.shape[1]

    def headerData(self, section: int, orientation: Qt.Orientation, role: Any) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return super().headerData(section, orientation, role=role)
    
    def addModelData(self, newData:List) -> None:
        self._data = np.vstack([self._data, newData])
        print(self._data)

    def removeModelData(self, index:List) -> None:
        self._data = np.delete(self._data, index, axis=0)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self._selectedRows = []
        self._color = ['r', 'b', 'g']
        self.setupUi(self)

        # Data to plot. Not good practice. Only 
        self.data_plot = [
            [[1,2,3,4,5], [1,4,9,16,25]],
            [[1,2,3,4,5], [1,2,3,4,5]],
            [[1,2,3,4,5], [5,4,3,2,1]]
        ]

        #Test data. Not good practice
        test = [
          [1, 2, 3],
          [4, 5, 6],
          [datetime(2021,8,26), 'abc', 'qwer'],
          [7, 8, 9],
          [10,11, 12]
        ]
        data = np.array(test)

        self.fileListModel = TableModel(data=data)
        self.fileView.setModel(self.fileListModel)

        self.btn_addToList.pressed.connect(self.add)
        self.btn_delItem.pressed.connect(self.delete)
        self.btn_clientSelect.pressed.connect(partial(self.open, 'client'))
        self.btn_labSelect.pressed.connect(partial(self.open, 'lab'))
        self.btn_plot.pressed.connect(self.plot)
        self.btn_clear.pressed.connect(self.graphWidget.clear)

        # Change selection behavior. Focus on rows.
        self.fileView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.fileView.selectionModel().selectionChanged.connect(self.selection_changed)

        # Graph widget settings
        self.graphWidget.setBackground('w')
        #self.plot([1,2,3,4,5], [1,4,9,16,25])

    # Return the index of selected rows in an array
    def selection_changed(self):
        self._selectedRows = [idx.row() for idx in self.fileView.selectionModel().selectedRows()]
        print(self._selectedRows)

    def add(self):
        """
        Add the client and lab file to the file list, then clean the input box
        """

        # Simple add text to table. 
        clientFilePath = self.edit_clientFile.text()
        labFilePath = self.edit_labFile.text()

        try:
            current_date = datetime.strptime(self.edit_date.text(), '%Y-%m-%d')
        except ValueError:
            # TODO: Pop out a window indicating the datetime format is wrong
            print("The datetime format is wrong!")

        if clientFilePath and labFilePath and current_date: # Don't add empty strings.

            self.fileListModel.addModelData([current_date, clientFilePath, labFilePath])
            # Trigger refresh. 
            self.fileListModel.layoutChanged.emit()
            # Empty the input
            self.edit_clientFile.setText("")
            self.edit_labFile.setText("")
            self.edit_date.setText("")
            print('Current content:')
            print(self.fileListModel._data)
        else:
            # TODO: Pop up another window
            print("All three fields need to be filled up!")
 
    def delete(self):
        indexes = self._selectedRows
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            # Remove the item and refresh.
            self.fileListModel.removeModelData(indexes)
            # time.sleep(0.2)
            self.fileListModel.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            self.fileView.clearSelection()
        else:
            pass
    
    def open(self, *args):

        (fileName, _) = QFileDialog.getOpenFileName(self, "Open File", pathlib.Path().resolve().__str__(), "Excel Files (*.csv)")
        if fileName:
            if args[0] == 'client':
                self.edit_clientFile.setText(fileName)
                print(fileName)
            elif args[0] == 'lab':
                self.edit_labFile.setText(fileName)
                print(fileName)
        else:
            pass
        print(fileName)
        return fileName

    def plot(self):
        print('Plot data')
        self.graphWidget.clear()
        if self._selectedRows:
            for (_, item) in enumerate(self._selectedRows):
                self.graphWidget.plot(self.data_plot[item % 3][0], self.data_plot[item % 3][1], pen=pg.mkPen(color=self._color[item % 3], width=15))
        else:
            pass

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()