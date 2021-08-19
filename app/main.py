from portalocker.exceptions import AlreadyLocked
import portalocker
import PySimpleGUI as sg

from app.core.constraints import JOBS_LOCK_PATH
from app.gui.client_based_demo_pysimplegui import make_window as make_main_window


def main():
    try:
        with portalocker.Lock(JOBS_LOCK_PATH, fail_when_locked=True):
            make_main_window()
    except AlreadyLocked:
        sg.popup('Error: Multiple instance detected!',
                 'This program is already running on this device or other devices in the'
                 ' network that are accessing the same data folder. Please ensure other '
                 'instances are closed. If you are sure that this is an false alert and all '
                 f'instances are closed, please delete the file in {JOBS_LOCK_PATH.absolute()}')


if __name__ == '__main__':
    main()
