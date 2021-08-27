import sys, os.path
import pathlib
import shutil
import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *

# setup the relative path under the ui folder
dir = os.path.dirname(__file__)
main_window_ui = os.path.join(dir, 'main_window.ui')

class Window(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Digital Calibration")
    self.ui = loadUi(main_window_ui, self)

    # set the left current page with client
    self.ui.stackedWidget.setCurrentWidget(self.ui.client)
    # set the right current page with pre-analysis
    self.ui.stackedWidget_2.setCurrentWidget(self.ui.pre_analysis)

    # left current page selection with menubar actions
    # register the QMenuBar, QMenu, QActions
    self.menubar = QMenuBar()
    self.menufiles = self.menubar.addMenu(QMenu())
    self.ui.btn_call_client.triggered.connect(self.show_client)
    self.ui.btn_call_jobs.triggered.connect(self.show_jobs)
    self.ui.btn_open.triggered.connect(self.open_file)
    self.ui.btn_call_files.triggered.connect(self.show_files)

    # right current page selection with buttons
    self.ui.btn_compare.clicked.connect(self.show_test_results)
    self.ui.btn_compare.clicked.connect(self.plot_graph)
    self.ui.btn_back_to_comparison.clicked.connect(self.show_pre_analysis)

    # other buttons inside the menubars
    self.ui.btn_output_pdf.triggered.connect(self.output_pdf) # haven't hooked the function
    self.ui.btn_output_dcc.triggered.connect(self.output_dcc) # haven't hooked the function

    # The file explorer
    self.model = QFileSystemModel()
    # TODO: specify the directory under the analysis directory
    # TODO: only show the name of the directory, and files
    self.model.setRootPath(QDir.currentPath())
    self.ui.treeView.setModel(self.model)
    # TODO: get the file path and loading the file into the GUI
    # reference: https://stackoverflow.com/questions/45046874/qfilesystemmodel-retrieve-filepath-of-clicked-file

    # TODO: the file paths can be brought into the calculator -> note
    # TODO: the CAL_number is for looking up the client -> put multiple equipments

    # keep only the name of the directory, and files
    for i in range(1, 4):
      self.ui.treeView.hideColumn(i)

    self.ui.treeView.setRootIndex(self.model.index(QDir.currentPath()))

    try:
      self.data_storage = pathlib.Path(r'data')
      self.data_storage.mkdir(parents=True, exist_ok=False) # create the specific directory if doesn't exist
      self.cal_number_storage = pathlib.Path(r'data/CAL00001')
      self.cal_number_storage.mkdir(parents=True, exist_ok=False)
    except:
      print("The directory already exists")
    
    # pyqtgraph with QGraphicView
    self.ui.graphicsView = pg.PlotWidget()

  def show_client(self):
    self.ui.stackedWidget.setCurrentWidget(self.ui.client)
  
  def show_jobs(self):
    self.ui.stackedWidget.setCurrentWidget(self.ui.jobs)

  def show_test_results(self):
    self.ui.stackedWidget_2.setCurrentWidget(self.ui.analysis_result)
  
  def show_pre_analysis(self):
    self.ui.stackedWidget_2.setCurrentWidget(self.ui.pre_analysis)

  def show_files(self):
    self.ui.stackedWidget.setCurrentWidget(self.ui.files)

  def open_file(self):
    '''when the user open a csv file, the file would be save inside the specific folder (database)'''
    file_path, _ = QFileDialog.getOpenFileName(self, 'Data File (*.csv *.xlsx)') # can specify the default path
    # the second variable is the specified file format

    # homedir = pathlib.Path(r'data') # the parent folder inside the current folder
    # print(homedir) # print "data"
    # could specify the relative folder

    try:
      shutil.copy(file_path, self.cal_number_storage)
    except:
      print("The file already exists")
    # copy the data inside the folder based on the unique CAL_number -> might be parsed to create one if doesn't exist
    # referece: https://stackoverflow.com/questions/33625931/copy-file-with-pathlib-in-python

    # should set the current widget to the tree structure on the left panel
    self.show_files()

  def plot_graph(self):
    hour = [1,2,3,4,5,6,7,8,9,10]
    temperature = [30,32,34,32,33,31,29,32,35,45]
    self.ui.graphicsView.plot(hour, temperature)
    self.ui.graphicsView.show()

  def output_pdf(self):
    pass

  def output_dcc(self):
    pass
  

if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = Window()
  window.show()
  sys.exit(app.exec_())