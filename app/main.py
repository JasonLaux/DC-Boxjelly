"""
The entry point of main program.
"""


from portalocker.exceptions import AlreadyLocked
import portalocker
from PyQt5.QtWidgets import QMessageBox, QApplication
import sys
import logging
from logging.handlers import RotatingFileHandler

from app.core.definition import JOBS_LOCK_PATH
from app.gui.main import start_event_loop


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(
        exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def main():

    std_out_log = logging.StreamHandler()
    std_out_log.setLevel(logging.DEBUG)

    file_log = RotatingFileHandler('dc.log')
    file_log.setLevel(logging.INFO)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            std_out_log,
            file_log,
        ])

    logger.info('Starting application')

    try:
        with portalocker.Lock(JOBS_LOCK_PATH, fail_when_locked=True):
            logger.info('Data lock acquired, starting event loop')
            ret = start_event_loop()

    except AlreadyLocked:
        logger.error('Multiple instance detected')

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
