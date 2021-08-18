"""
The file adds /app as the module search directory, so you can use `import models` 
rather than `import app.models`
"""

from traitlets.config import Config
import sys
import os
import IPython

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

if __name__ == '__main__':
    c = Config()
    c.InteractiveShellApp.extensions = [
        'autoreload',
    ]
    c.InteractiveShellApp.exec_lines = [
        r'%autoreload 2',
    ]
    IPython.start_ipython(config=c)
