"""
This file contains the models representing a job, an equipment and a run.

Each model controls a folder in /data.

Data consistency is not guaranteed if a folder is access by multiple instences
(such as multiple devices accessing the same folder) at the same time.
"""

from typing import Tuple

from .mixins import WithMetaMixin
from .constraints import JOB_FOLDER, EQUIPMENT_FOLDER_NAME
from utils import ensure_folder

class Job(WithMetaMixin, object):
    """
    A model that represents a job.
    """

    def __init__(self, id: str) -> None:
        """
        id: The id of the job
        """
        self._id = str(id)
        self._folder = JOB_FOLDER / self._id

        if not ensure_folder(self._folder):
            self._save_meta_data({
                'id': self._id,
                'name': 'Please enter client name',
                'address': 'Please enter client address',
            })
        
        self._equipment_folder = self._folder / EQUIPMENT_FOLDER_NAME
        ensure_folder(self._equipment_folder)

    def __repr__(self) -> str:
        return f'Job({self._id})'

    def get_client_name(self):
        return self._read_meta()['name']

    def get_client_address(self):
        return self._read_meta()['address']

    def get_id(self):
        return self._id

    def set_client_name(self, name):
        self._set_meta_data('name', name)

    def set_client_address(self, address):
        self._set_meta_data('address', address)

    def get_equipments(self):
        for file in self._equipment_folder.iterdir():
            if not file.is_dir():
                continue
            yield Equipment(self, id=file.name)

class Equipment(WithMetaMixin, object):
    """
    A model that represents an equipment.
    """
    
    def __init__(self, parent: Job, id: str=None, model_serial: Tuple[str, str]=None) -> None:
        """
        Init an equipment, either id or model_serial should be not None.

        partent: which job this equipment belongs to.
        id: a string representing the id of an equipment
        model_serial: a tuple like ('AAA', '123') representing the model and serial of an equipment
        """

        if not id and not model_serial:
            raise ValueError('At least one of the id and model_serial should be provided')

        if id and model_serial:
            raise ValueError('Only one of the id and model_serial should be provided')

        # generate an id from model and serial
        if model_serial:
            model, serial = model_serial
            folder = parent._equipment_folder

            if (folder / f'{model}_{serial}').exists():
                idx = 2
                while (folder / f'{model}_{serial}_{idx}').exists():
                    idx += 1
                id = f'{model}_{serial}_{idx}'
            else:
                id = f'{model}_{serial}'

        self._id = id
        self._folder = parent._equipment_folder / id

        # ensure equipment folder and meta data
        if not ensure_folder(self._folder):
            model_serial = self._id.split('_')
            self._save_meta_data({
                'id': self._id,
                'model': model_serial[0],
                'serial': model_serial[1],
            })

        self._mex = self._folder / 'MEX'
        ensure_folder(self._mex)

    def __repr__(self) -> str:
        return f'Equipment({self._id})'