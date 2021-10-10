"""
The entry point of repl. You can use this script to directely import models from
`core.models` and exporing available apis.

The file adds /app as the module search directory, so you can use `import core.models` 
rather than `import app.core.models`

Simple usage guide:

# Run the following command through command line prompt under project root to start repl.
pipenv run repl

# import classes from core.models
>>> from core.models import Job

# Add `?` after class or methods to view documents
>>> Job?
Init signature: Job(id: str) -> None
Docstring:
A model that represents a job.
...

# Directely run methods
>>> list(Job)
[Job(CAL00001), Job(CAL00002), Job(CAL00003), Job(CAL00004), Job(CAL0001)]

>>> job = Job['CAL0001']

>>> job.delete?
Signature: job.delete()
Docstring:
Remove the model, this process cannot be undone.
...

```
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
