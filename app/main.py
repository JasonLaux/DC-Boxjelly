from portalocker.exceptions import AlreadyLocked
import portalocker
from PyQt5.QtWidgets import QMessageBox, QApplication
import sys

from app.core.definition import JOBS_LOCK_PATH
from app.gui.main import start_event_loop


def main():
    try:
        with portalocker.Lock(JOBS_LOCK_PATH, fail_when_locked=True):
            ret = start_event_loop()
    except AlreadyLocked:
        app = QApplication(sys.argv)
        msg = QMessageBox(QMessageBox.Icon.Critical,
                          'Error: Multiple instance detected!',
                          'This program is already running on this device or other devices in the'
                          ' network that are accessing the same data folder. Please ensure other '
                          'instances are closed. If you are sure that this is an false alert and all '
                          f'instances are closed, please delete the file {JOBS_LOCK_PATH.absolute()}'
                          )
        msg.show()
        app.exec()
        ret = 1

    sys.exit(ret)


if __name__ == '__main__':
    main()
