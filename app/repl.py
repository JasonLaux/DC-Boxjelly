"""
The file adds /app as the module search directory, so you can use `import models` 
rather than `import app.models`
"""

import sys
import os 
import IPython

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

if __name__ == '__main__':
    IPython.start_ipython()