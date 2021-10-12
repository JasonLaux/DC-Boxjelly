from pathlib import Path
from stat import S_IREAD

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

'''
The name of meta section in exported csv file
'''
RAW_META_SECTION_NAME = '[DC_META]'

'''
The name of the measurement meta data in raw file
'''
RAW_MEASUREMENT_SECTION_NAME = '[COMET X-RAY MEASUREMENT]'

'''
The name of the data section in raw file
'''
RAW_DATA_SECTION_NAME = '[DATA]'

# constrains

'''
The location of the template constant file.

When a new constant file is added, this file is copied to the location.
'''
TEMPLATE_CONSTANT_FILE = Path(__file__).parent / 'template_constant.xlsx'
TEMPLATE_CONSTANT_FILE.chmod(S_IREAD) # make the file read only

'''
The folder that contains constant files
'''
CONSTANT_FOLDER = DATA_FOLDER / 'constants'
if not ensure_folder(CONSTANT_FOLDER):
    (CONSTANT_FOLDER / META_FILE_NAME).touch()

CONSTANT_FILE_NAME = 'constant.xlsx'

'''
The path of the Operation Manual
'''
OPS_MANUAL = Path(__file__).parent.parent / 'gui' / 'resources' / 'Operation Manual CAA 081021 1837hrs.docx'
OPS_MANUAL.chmod(S_IREAD) # make the file read only