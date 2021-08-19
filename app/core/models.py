"""
This file contains the models representing a job, an equipment and a run.

Each model controls a folder in /data.

Data consistency is not guaranteed if a folder is access by multiple instences
(such as multiple devices accessing the same folder) at the same time.
"""

from typing import Iterable, Tuple
from datetime import datetime

from .mixins import DeleteFolderMixin, WithMetaMixin
from .constraints import JOB_FOLDER, EQUIPMENT_FOLDER_NAME, MEX_FOLDER_NAME, MEX_RAW_CLIENT_FILE_NAME, MEX_RAW_FOLDER_NAME, MEX_RAW_LAB_FILE_NAME
from .utils import datetime_to_iso, ensure_folder, iter_subfolders


def iter_jobs() -> Iterable['Job']:
    """
    Return an iterator of Job object in the job folder
    """
    for file in JOB_FOLDER.iterdir():
        if not file.is_dir():
            continue
        yield Job(file.name)


class Job(WithMetaMixin, DeleteFolderMixin, object):
    """
    A model that represents a job.

    In additions to the given methods, it supports basic python operations like below:

    job = Job(5)

    # iterate through each equipments
    for e in job:
        print(e)

    # get an equipment by its id
    job['AAA_123']

    # delete an equipment
    del job['AAA_123']
    """

    def __init__(self, id: str, *,
                 name='Please enter client name',
                 address='Please enter client address',
                 ) -> None:
        """
        id: The id of the job
        name: Client name, only used in creating new Job
        address: Client address, only used in creating new Job

        If the folder does not exist, it is automatically created using provided
        id, name and address.
        """
        self._id = str(id)
        self._folder = JOB_FOLDER / self._id

        self._ensure_folder_with_meta({
            'id': self._id,
            'name': name,
            'address': address,
        })

        self._equipment_folder = self._folder / EQUIPMENT_FOLDER_NAME
        ensure_folder(self._equipment_folder)

    def __repr__(self) -> str:
        return f'Job({self._id})'
    __str__ = __repr__

    def __iter__(self) -> Iterable['Equipment']:
        """
        Get all equipments belongs to the job
        """
        for file in iter_subfolders(self._equipment_folder):
            yield Equipment(self, id=file.name)

    def __contains__(self, id) -> bool:
        """
        Return whether this job contains equipment identified by id
        """
        folder = self._equipment_folder / str(id)
        return folder.is_dir()

    def __getitem__(self, id):
        """
        Get one equipment by id. It verifies whether the folder exists.
        """
        if id not in self:
            raise KeyError(
                f'The equipment identified by {id} is not a folder!')

        return Equipment(self, id=id)

    def __delitem__(self, id):
        """
        Delete an equipment by the id provided
        """
        equipment = self[id]
        equipment.delete()

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

    def add_equipment(self, model, serial) -> 'Equipment':
        """
        Add an equipment with the given model and serial
        """

        return Equipment(self, model_serial=(model, serial))


class Equipment(WithMetaMixin, DeleteFolderMixin, object):
    """
    A model that represents an equipment.

    Use `equipment.mex` to get the set of mex runs of this equipment
    """

    def __init__(self, parent: Job, *,
                 id: str = None, model_serial: Tuple[str, str] = None) -> None:
        """
        Init an equipment, either id or model_serial should be not None.

        partent: which job this equipment belongs to.
        id: a string representing the id of an equipment
        model_serial: a tuple like ('AAA', '123') representing the model and serial of an equipment
        """

        if not id and not model_serial:
            raise ValueError(
                'At least one of the id and model_serial should be provided')

        if id and model_serial:
            raise ValueError(
                'Only one of the id and model_serial should be provided')

        self._parent = parent

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
        else:
            assert (parent._equipment_folder / str(id)
                    ).is_dir(), 'Equipment folder exists'

        self._id = id
        self._folder = parent._equipment_folder / id

        model_serial = self._id.split('_')
        self._ensure_folder_with_meta({
            'id': self._id,
            'model': model_serial[0],
            'serial': model_serial[1],
        })

        self.mex = MexAssessment(self)

    def __repr__(self) -> str:
        return f'Equipment({self._id}, parent={self._parent})'

    def __str__(self):
        return f'Equipment({self._id})'


class MexAssessment:
    """
    The mex assessment belongs to an equipment.

    In additions to the given methods, it supports basic python operations like below:

    job = Job(5)
    e = job['AAA_123'] # a equipment

    # iterate through each MexRun's
    for run in e.mex:
        print(e)

    # get a mex run by its id
    e.mex[1]

    # delete a mex run
    del e.mex[1]

    # get the total number of mex runs
    len(e.mex)
    """

    def __init__(self, parent: Equipment) -> None:
        self._parent = parent
        self._folder = parent._folder / MEX_FOLDER_NAME
        ensure_folder(self._folder)

    def __str__(self) -> str:
        return f'MexAssessment({self._parent})'

    def __repr__(self) -> str:
        return f'MexAssessment({self._parent.__repr__()})'

    def __iter__(self) -> Iterable['MexRun']:
        """
        Iterate through all MEX runs
        """
        for file in iter_subfolders(self._folder):
            yield MexRun(self, file.name)

    def __contains__(self, id) -> bool:
        """
        Check if the equipment has the MEX run with given id
        """
        folder = self._folder / str(id)
        return folder.is_dir()

    def __getitem__(self, id) -> 'MexRun':
        """
        Get a mex run by id.

        If run does not exist, raise KeyError
        """
        if id not in self:
            raise KeyError(f'{self} does not contains MEX run with id={id}')
        return MexRun(self, id)

    def __delitem__(self, id):
        """
        Delete a mex run by id.

        If run does not exist, raise KeyError
        """
        self[id].delete()

    def add(self) -> 'MexRun':
        """
        Add a new MEX run
        """
        return MexRun(self)

    def __len__(self):
        return len(list(iter_subfolders(self._folder)))


class MexRun(WithMetaMixin, DeleteFolderMixin, object):
    """
    This model represents a run in mex analysis.
    """

    def __init__(self, parent: MexAssessment, id=None) -> None:
        """
        Initialize a MexRun instance.

        If id exists, it reads the data from the existing run.
        If it does not exist, this process creates new run in the parent folder.
        """

        self._parent = parent

        if not id:
            id = max(int(run._id) for run in parent) + 1 \
                if len(parent) > 0 else 1
        else:
            assert (parent._folder / str(id)).is_dir(), 'MEX run folder exists'

        self._id = str(id)
        self._folder = parent._folder / self._id
        self._raw = self._folder / MEX_RAW_FOLDER_NAME
        self._client = self._raw / MEX_RAW_CLIENT_FILE_NAME
        self._lab = self._raw / MEX_RAW_LAB_FILE_NAME

        self._ensure_folder_with_meta({
            'added_at': datetime_to_iso(datetime.now())
        })
        ensure_folder(self._raw)

    def __repr__(self) -> str:
        return f'MexRun({self._id}, parent={self._parent})'

    def __str__(self):
        return f'MexRun({self._id})'
