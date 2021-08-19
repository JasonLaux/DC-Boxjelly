"""
This file contains the models representing a job, an equipment and a run.

Each model controls a folder in /data.

Data consistency is not guaranteed if a folder is access by multiple instences
(such as multiple devices accessing the same folder) at the same time.
"""

from typing import Iterable, Iterator, Optional, Tuple
from datetime import datetime

from .mixins import DeleteFolderMixin, WithMetaMixin, meta_property
from .constraints import JOB_FOLDER, MEX_FOLDER_NAME, MEX_RAW_CLIENT_FILE_NAME, MEX_RAW_FOLDER_NAME, MEX_RAW_LAB_FILE_NAME
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

    ```
    job = Job(5)

    # iterate through each equipments
    for e in job:
        print(e)

    # get an equipment by its id
    job['AAA_123']

    # delete an equipment
    del job['AAA_123']

    # get the total number of jobs
    len(e.mex)
    ```
    """

    def __init__(self, id: str, *,
                 client_name='Please enter client name',
                 client_address='Please enter client address',
                 ) -> None:
        """
        id: The id of the job
        client_name: Client name, only used in creating new Job
        client_address: Client address, only used in creating new Job

        If the folder does not exist, it is automatically created using provided
        id, name and address.
        """
        self._id = str(id)
        self._folder = JOB_FOLDER / self._id

        if not self._ensure_folder_with_meta():
            self.client_name = client_name
            self.client_address = client_address

    def __repr__(self) -> str:
        return f'Job({self._id})'
    __str__ = __repr__

    def __iter__(self) -> Iterator['Equipment']:
        """
        Get all equipments belongs to the job
        """
        for file in iter_subfolders(self._folder):
            yield Equipment(self, id=file.name)

    def __contains__(self, id) -> bool:
        """
        Return whether this job contains equipment identified by id
        """
        folder = self._folder / str(id)
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

    def __len__(self):
        """
        Get the number of equipments in this job
        """
        return len(list(iter_subfolders(self._folder)))

    @property
    def id(self):
        return self._id

    # meta properties
    client_name = meta_property('client_name')
    client_address = meta_property('client_address')

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
                 id: Optional[str] = None,
                 model_serial: Optional[Tuple[str, str]] = None) -> None:
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
            folder = parent._folder

            if (folder / f'{model}_{serial}').exists():
                idx = 2
                while (folder / f'{model}_{serial}_{idx}').exists():
                    idx += 1
                self._id = f'{model}_{serial}_{idx}'
            else:
                self._id = f'{model}_{serial}'

            self._folder = parent._folder / self._id
            self._ensure_folder_with_meta()
            self.model = model
            self.serial = serial

        else:
            assert(id)
            assert (parent._folder / str(id)
                    ).is_dir(), 'Equipment folder exists'

            self._id = id
            self._folder = parent._folder / self._id
            assert self._meta_exists()

        self.mex = MexAssessment(self)

    def __repr__(self) -> str:
        return f'Equipment({self._id}, parent={self._parent})'

    def __str__(self):
        return f'Equipment({self._id})'

    model = meta_property('model', 'The model of the equipment')
    serial = meta_property('serial', 'The serial of the equipment')


class MexAssessment:
    """
    The mex assessment belongs to an equipment.

    In additions to the given methods, it supports basic python operations like below:

    ```
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
    ```
    """

    def __init__(self, parent: Equipment) -> None:
        self._parent = parent
        self._folder = parent._folder / MEX_FOLDER_NAME
        ensure_folder(self._folder)

    def __str__(self) -> str:
        return f'MexAssessment({self._parent})'

    def __repr__(self) -> str:
        return f'MexAssessment({self._parent.__repr__()})'

    def __iter__(self) -> Iterator['MexRun']:
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

    def __len__(self):
        return len(list(iter_subfolders(self._folder)))

    def add(self) -> 'MexRun':
        """
        Add a new MEX run
        """
        return MexRun(self)


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

        if not self._ensure_folder_with_meta():
            self._set_meta('added_at', datetime_to_iso(datetime.now()))
        ensure_folder(self._raw)

    def __repr__(self) -> str:
        return f'MexRun({self._id}, parent={self._parent})'

    def __str__(self):
        return f'MexRun({self._id})'
