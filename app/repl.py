"""
The file adds /app as the module search directory, so you can use `import models` 
rather than `import app.models`
"""

import sys
import os
import IPython

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

# Codes that handle module reloading (from https://stackoverflow.com/a/61019586)

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

    for module in set(modules.values()) - PRELOADED_MODULES:
        try:
            importlib.reload(module)
        except:
            # there are some problems that are swept under the rug here
            pass


if __name__ == '__main__':
    init()
    IPython.start_ipython(user_ns={
        'reload': reload,
    })
