import sys, os
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu

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
    # register the QMenuBar and QMenu
    self.menubar = QMenuBar()
    self.menufiles = self.menubar.addMenu(QMenu())
    self.ui.btn_call_client.triggered.connect(self.show_client)
    self.ui.btn_call_jobs.triggered.connect(self.show_jobs)

    # right current page selection with buttons
    self.ui.btn_compare.clicked.connect(self.show_test_results)
    self.ui.btn_back_to_comparison.clicked.connect(self.show_pre_analysis)

    # other buttons inside the menubars
    self.ui.btn_output_pdf.triggered.connect(self.output_pdf) # haven't hook the function
    self.ui.btn_output_dcc.triggered.connect(self.output_dcc) # haven't hook the function
  
  def show_client(self):
    self.ui.stackedWidget.setCurrentWidget(self.ui.client)
  
  def show_jobs(self):
    self.ui.stackedWidget.setCurrentWidget(self.ui.jobs)

  def show_test_results(self):
    self.ui.stackedWidget_2.setCurrentWidget(self.ui.analysis_result)
  
  def show_pre_analysis(self):
    self.ui.stackedWidget_2.setCurrentWidget(self.ui.pre_analysis)

  def output_pdf(self):
    pass

  def output_dcc(self):
    pass
  

if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = Window()
  window.show()
  sys.exit(app.exec_())