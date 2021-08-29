from PyQt5 import QtWidgets, QtGui, QtCore, uic

import sys
import resources

try:
    # Include in try/except block if you're also targeting Mac/Linux
    from PyQt5.QtWinExtras import QtWin
    myappid = 'com.learnpyqt.examples.counter'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)    
except ImportError:
    pass


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Load the UI
        # fileh = QtCore.QFile(':/ui/mainwindow.ui')
        # fileh.open(QtCore.QFile.ReadOnly)
        uic.loadUi('resources/mainwindow.ui', self)
        # fileh.close()

        # Set value of counter
        self.counter = 0
        self.update_counter()

        # Bind
        self.btn_inc.clicked.connect(self.inc)
        self.btn_dec.clicked.connect(self.dec)
        self.btn_reset.clicked.connect(self.reset)
        #self.btn_clear.clicked.connect(self.clear_text)
    
    def update_counter(self):
        self.label.setText(str(self.counter))
    
    def clear_text(self):
        self.label_test.setText('')

    def inc(self):
        self.counter += 1
        self.update_counter()

    def dec(self):
        self.counter -= 1
        self.update_counter()

    def reset(self):
        self.counter = 0
        self.update_counter()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(':/icons/counter.ico'))
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
 