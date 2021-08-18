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

'''
The name of the folder that stores MEX analysis
'''
MEX_FOLDER_NAME = 'MEX'

'''
The name of the folder in a MEX run that stores raw data
'''
MEX_RAW_FOLDER_NAME = 'raw'

'''
The name of the client raw file of MEX analysis
'''
MEX_RAW_CLIENT_FILE_NAME = 'client.csv'

'''
The name of the lab raw file of MEX analysis
'''
MEX_RAW_LAB_FILE_NAME = 'lab.csv'

'''
The name of the file that contains meta data such as client name or created time.
'''
META_FILE_NAME = 'meta.ini'

JOBS_LOCK_PATH = DATA_FOLDER / 'jobs.lock'
