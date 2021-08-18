"""
The file adds /app as the module search directory, so you can use `import models` 
rather than `import app.models`
"""

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from traitlets.config import Config
import sys
import os
import IPython

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

####################################################
# Codes that handle module reloading (from https://stackoverflow.com/a/61019586)
####################################################

PRELOADED_MODULES = set()


def init():
    # local imports to keep things neat
    from sys import modules
    import importlib

    global PRELOADED_MODULES

    # sys and importlib are ignored here too
    PRELOADED_MODULES = set(modules.values())


def reload():
    from sys import modules
    import importlib
    from pathlib import Path
    from IPython.lib import deepreload

    for module in set(modules.values()) - PRELOADED_MODULES:

        # only reloads py code in app folder
        if not hasattr(module, '__file__'):
            continue
        if Path(module.__file__) not in Path(dir_path).parents:
            continue

        try:
            importlib.reload(module)
            print(f'{module} reloaded')
        except:
            # there are some problems that are swept under the rug here
            pass


####################################################
# Auto reloading
####################################################


class AutoReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        _, ext = os.path.splitext(event.src_path)
        if ext != '.py':
            return

        print('File changes detected, reloading...')
        reload()
        print('Reloading done')

####################################################
# Main code
####################################################


def run_main():
    """
    Start main.py
    """
    import main  # local import to prevent it from including in PRELOADED_MODULES
    main.main()


observer = Observer()


def force_exit():
    observer.stop()
    observer.join()
    sys.exit()


if __name__ == '__main__':
    # init()

    # observer.schedule(AutoReloadHandler(), dir_path, recursive=True)
    # observer.start()

    c = Config()
    c.InteractiveShellApp.extensions = [
        'autoreload',
    ]
    c.InteractiveShellApp.exec_lines = [
        r'%autoreload 2',
    ]
    IPython.start_ipython(user_ns={
        'reload': reload,
        'main': run_main,
        'exit': force_exit,
    }, config=c)

    # observer.stop()
    # observer.join()
