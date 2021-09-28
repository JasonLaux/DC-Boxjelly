"""
This file contains the models representing a job, an equipment and a run.

Each model controls a folder in /data.

Data consistency is not guaranteed if a folder is access by multiple instences
(such as multiple devices accessing the same folder) at the same time.
"""

from pathlib import Path
from typing import Dict, Iterable, Iterator, Optional, Tuple
from datetime import datetime
import shutil
import os
import errno

from .mixins import DeleteFolderMixin, WithMetaMixin, assign_properties, meta_property
from .definition import RAW_META_SECTION_NAME, JOB_FOLDER, MEX_FOLDER_NAME, MEX_RAW_CLIENT_FILE_NAME, MEX_RAW_FOLDER_NAME, MEX_RAW_LAB_FILE_NAME, RAW_MEASUREMENT_SECTION_NAME
from .utils import count_iter_items, datetime_to_iso, ensure_folder, iter_subfolders


class _JobMetaClass(type):
    def __iter__(cls) -> Iterator['Job']:
        """
        Return an iterator of Job object in the job folder
        """
        for file in iter_subfolders(JOB_FOLDER):
            yield cls(file.name)

    def __getitem__(cls, id) -> 'Job':
        """
        Get a job by id, it is case insensitive on windows
        @id: The id of the job

        If the job does not exist, it raises a KeyError
        """
        obj = cls(id)
        if not obj._folder.is_dir():
            raise KeyError(f'Job with id={id} does not exist')
        return obj

    def __delitem__(cls, id):
        """
        Delete a job by its id.

        If the job with id does not exist, it raises KeyError
        """
        cls[id].delete()

    def __len__(self):
        """
        Get the number of all jobs
        """
        return count_iter_items(iter_subfolders(JOB_FOLDER))

    def __contains__(self, id) -> bool:
        """
        Return whether a job exists by id.

        The id is case insensitive on windows.
        """
        folder = JOB_FOLDER / str(id)
        return folder.is_dir()

    def make(cls, id: str, **kwargs) -> 'Job':
        """
        Create a new job with optional properties.

        If the job with given id exists, it raises an AssertionError
        """
        if id in Job:
            raise ValueError(f'The Job with id={id} has already existed')

        obj = cls(id)
        assert not obj._ensure_folder_with_meta(), 'The job folder should not exist'
        assign_properties(obj, kwargs)
        return obj


class Job(WithMetaMixin, DeleteFolderMixin, metaclass=_JobMetaClass):
    """
    A model that represents a job.

    Use following methods to list, iterate, make, and get jobs:
    ```
    # list jobs
    list(Job)

    # iterate through all jobs
    for job in Job:
        print(job)

    # get job number
    len(Job)

    # create new job
    Job.make(1, client_name="A client")

    # get job by id
    Job[1]

    # check job existence
    1 in Job # => a boolean
    'string_job_id_1' in Job # string works too
    ```

    In additions to the given methods, it supports basic python operations like below:

    ```
    job = Job[5]

    # iterate through each equipments
    for equipment in job:
        print(equipment)

    # get an equipment by its id
    job['AAA_123']

    # delete an equipment
    del job['AAA_123']

    # get the total number of equipments
    len(job)

    # check equipment existence
    'AAA_123' in job # => a boolean
    ```

    Read, write and delete meta data like below:
    ```
    job = Job[5]
    print(job.client_name)             # get client name
    job.client_name = 'Another client' # set client name
    del job.client_name                # remove client name (next time, job.client_name is None)
    ```
    """

    def __init__(self, id: str) -> None:
        """
        The private constructor of Job.

        **This is not meant to be used outside of `core.models`!**
        - If you want to create a new job, use `Job.make`
        - If you want to get an existing job, use `Job[_id_]`
        """
        self._id = str(id)
        self._folder = JOB_FOLDER / self._id

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
        return count_iter_items(iter_subfolders(self._folder))

    @property
    def id(self):
        return self._id

    # meta properties
    client_name = meta_property('client_name', 'Client identifier string')
    client_address_1 = meta_property(
        'client_address_1', 'The first line of client address')
    client_address_2 = meta_property(
        'client_address_2', 'The second line of client address')
    operator = meta_property('operator', 'Name of operator')

    def add_equipment(self, model, serial) -> 'Equipment':
        """
        Add an equipment with the given model and serial

        If equipment exists, raise ValueError
        """
        return Equipment(self, model=model, serial=serial)

    @property
    def meta(self) -> Dict[str, str]:
        """
        Export job meta data into a dict
        """
        return {
            'job_id': self.id,
            'client_name': self.client_name,
            'client_address_1': self.client_address_1,
            'client_address_2': self.client_address_2,
        }


class Equipment(WithMetaMixin, DeleteFolderMixin):
    """
    A model that represents an equipment.

    Use `equipment.mex` to get the set of mex runs of this equipment
    """

    def __init__(self, parent: Job,
                 id: Optional[str] = None,
                 model: Optional[str] = None,
                 serial: Optional[str] = None) -> None:
        """
        Init an equipment, either id or (model, serial) should be not None.
        **This constructor is not meant to be used outside of `core.models`!**
        - If you want to create a new equipment, use `job.add_equipment('AAA', '123')`
        - If you want to get an existing equipment by id, use `job['AAA_123']`

        @partent: which job this equipment belongs to.
        @id: a string representing the id of an equipment
        @model, serial: the model and serial of the equipment

        Create equipment like below:
        ```
        # Create a reference to an existing equipment:
        Equipment(job, id='AAA_123')
        # Create a new equipment
        Equipment(job, model='AAA', serial='123')
        ```
        """

        self._parent = parent

        if id:
            assert (parent._folder / str(id)
                    ).is_dir(), 'Equipment folder exists'

            self._id = id
            self._folder = parent._folder / self._id
            assert self._meta_exists()
        else:
            assert model, 'model should be provided'
            assert serial, 'serial should be provided'

            self._id = f'{model}_{serial}'
            self._folder = parent._folder / self._id

            if self._folder.exists():
                raise ValueError(f'The model ({model}) and serial {serial} in '
                                 '{parent} should not exist at creation')

            self._ensure_folder_with_meta({
                'model': model,
                'serial': serial,
            })

        self.mex = MexMeasurements(self)

    def __repr__(self) -> str:
        return f'Equipment({self._id}, parent={self._parent})'

    def __str__(self):
        return f'Equipment({self._id})'

    @property
    def id(self):
        return self._id

    model = meta_property('model', 'The model of the equipment', readonly=True)
    serial = meta_property(
        'serial', 'The serial of the equipment', readonly=True)

    @property
    def meta(self) -> Dict[str, str]:
        """
        Export equipment meta data into a dict
        """
        return {
            'equipment_model': self.model,
            'equipment_serial': self.serial,
        }


class MexMeasurements:
    """
    A mex measurement belongs to an equipment.

    In additions to the given methods, it supports basic python operations like below:

    ```
    job = Job[5]
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
        """
        Init MexMeasurements.

        **This constructor is not meant to be used outside of `core.models`!**
        - You can use `equipment.mex` to access MEX measurements
        """
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
            yield MexRun(self, int(file.name))

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
        return count_iter_items(iter_subfolders(self._folder))

    def add(self) -> 'MexRun':
        """
        Add a new MEX run
        """
        return MexRun(self)


class MexRun(WithMetaMixin, DeleteFolderMixin):
    """
    This model represents a run in mex analysis.
    """

    def __init__(self, parent: MexMeasurements, id: Optional[int] = None) -> None:
        """
        Initialize a MexRun instance.

        **This constructor is not meant to be used outside of `core.models`!**
        - If you want to create a new run, use `equipment.mex.add()`
        - If you want to get an existing run by id, use `equipment.mex[_id_]`

        If id exists, it reads the data from the existing run.
        If it does not exist, this process creates new run in the parent folder.
        """

        self._parent = parent

        if not id:
            id = max(run.id for run in parent) + 1 \
                if len(parent) > 0 else 1
        else:
            assert (parent._folder / str(id)).is_dir(), 'MEX run folder exists'

        self._id = int(id)
        self._folder = parent._folder / str(id)

        self._raw = self._folder / MEX_RAW_FOLDER_NAME
        self._client = self._raw / MEX_RAW_CLIENT_FILE_NAME
        self._lab = self._raw / MEX_RAW_LAB_FILE_NAME

        self.raw_client = MexRawFile(self, self._client)
        self.raw_lab = MexRawFile(self, self._lab)

        self._ensure_folder_with_meta({
            'added_at': datetime_to_iso(datetime.now()),
            'edited_at': datetime_to_iso(datetime.now()),
        })
        ensure_folder(self._raw)

    def __repr__(self) -> str:
        return f'MexRun({self._id}, parent={self._parent})'

    def __str__(self):
        return f'MexRun({self._id})'

    @property
    def id(self) -> int:
        return self._id

    operator = meta_property('operator', 'Who did the measurement')
    added_at = meta_property(
        'added_at', 'The datetime when this run is created', readonly=True)
    edited_at = meta_property('edited_at', 'The datetime when this run is edited (changing RAW data)',
                              setter=lambda time: datetime_to_iso(time) if type(time) is datetime else str(time))

    @property
    def meta(self) -> Dict[str, str]:
        """
        Export run meta data into a dict
        """
        return {
            'run_id': str(self.id),
            'operator': self.operator,
            'run_added_at': self.added_at,
            'run_edited_at': self.edited_at,
        }


class MexRawFile:
    """
    Representing a raw file
    """

    def __init__(self, parent: MexRun, path: Path) -> None:
        """
        Create a raw file object.

        ** This constructor is not meant to be used outside of models.py! **
        - Please access it through MexRun
        """

        self._path = path
        self._parent = parent

    @property
    def path(self) -> Optional[Path]:
        """
        Get the path to the raw file.

        If file does not exist, return None
        """
        return self._path if self._path.exists() else None

    def upload_from(self, source: Path):
        """
        Save the raw data from `source` path.

        It just copies the file into the run/raw folder.

        If the source file does not exist, it raises ValueError
        """
        if not Path(source).is_file():
            raise ValueError(f'Source path {source} is not a file')

        with source.open(encoding='ISO-8859-1') as f:
            lines = f.readlines()

        if lines[0].strip() == RAW_META_SECTION_NAME:
            beg = [i for i, line in enumerate(lines)
                   if line.strip().startswith(RAW_MEASUREMENT_SECTION_NAME)]
            assert len(beg) == 1
            lines = lines[beg[0]:]

        with self._path.open('w', encoding='ISO-8859-1') as f:
            f.writelines(lines)

        self._update_edit_time()

    def remove(self):
        """
        Remove the raw data file.

        If the file does not exist, it does nothing. An OSError may be
        raised if errors such as no permission is encountered.
        """
        try:
            os.remove(self._path)
        except OSError as e:
            if e.errno != errno.ENOENT:  # no such file or directory
                raise

        self._update_edit_time()

    def export_to(self, path: Path):
        """
        Export raw data into path.

        Please ensure the parent folder of path exists.
        """
        assert path.parent.is_dir()

        if not self._path.exists():
            raise FileNotFoundError('The raw file does not exist!')

        with self._path.open() as f:
            lines = f.readlines()

        run = self._parent
        equipment = run._parent._parent
        job = equipment._parent

        meta_section = [
            RAW_META_SECTION_NAME + '\n',
            *_meta_dict_to_csv_line(job),
            *_meta_dict_to_csv_line(equipment),
            *_meta_dict_to_csv_line(run),
        ]

        with path.open('w') as f:
            f.writelines(meta_section)
            f.writelines(lines)

    def _update_edit_time(self):
        self._parent.edited_at = datetime.now()


def _meta_dict_to_csv_line(obj):
    return ['{k},{v}\n'.format(k=k, v=v if v else '') for k, v in obj.meta.items()]
