from pathlib import Path
import configparser
import shutil

from .constraints import META_FILE_NAME
from .utils import ensure_folder


class WithMetaMixin:
    """
    A mixin representing a model contains a meta file

    It assume that the object contains a field called _folder, which represents the folder
    the model has.
    """

    @property
    def _meta(self) -> Path:
        """
        Get the path of the meta file
        """
        return self._folder / META_FILE_NAME

    def _meta_exists(self) -> bool:
        """
        Check if the meta file exists
        """
        return self._meta.is_file()

    def _ensure_folder_with_meta(self, meta: dict):
        """
        Ensure folder and meta file exists.

        If folder does not exist, create it with meta file with data provided
        """
        if not ensure_folder(self._folder):
            self._overwrite_meta_data(meta)
        else:
            assert self._meta_exists()

    def _overwrite_meta_data(self, meta: dict):
        """
        Override the meta.ini with whatever meta dict provides
        """
        config = configparser.ConfigParser()
        config['meta'] = meta
        with open(self._meta, 'w') as fr:
            config.write(fr)

    def _read_meta(self, section='meta'):
        """
        Return a dict represents the meta data of the folder
        """
        config = configparser.ConfigParser()
        config.read(self._meta)
        return config[section]

    def _set_meta_data(self, field, value, section='meta'):
        """
        Set a value into the meta data field.
        """
        config = configparser.ConfigParser()
        config.read(self._meta)
        config[section][field] = value
        with open(self._meta, 'w') as fr:
            config.write(fr)


class DeleteFolderMixin:
    """
    A mixin that adds operation to delete the folder this instance represents.

    The class must contains a _folder field.
    """

    def delete(self):
        """
        Remove the model, this process cannot be undone.

        After calling this method, invoking other methods are invalid.
        """
        shutil.rmtree(self._folder)
