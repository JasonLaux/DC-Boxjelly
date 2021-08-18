from pathlib import Path

from .utils import ensure_folder

'''
The path of the data folder
'''
DATA_FOLDER = Path('data')
ensure_folder(DATA_FOLDER)

'''
The path of the job folder
'''
JOB_FOLDER = DATA_FOLDER / 'jobs'
ensure_folder(JOB_FOLDER)

'''
The name of the equipment folder. Altering this constraints changes the name of the
equipment folder in the job folder.

data/jobs/1/equipments/ABC_123
            ^
            |
        This one
'''
EQUIPMENT_FOLDER_NAME = 'equipments'