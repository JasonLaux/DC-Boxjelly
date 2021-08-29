from pathlib import Path
import configparser
import shutil
from typing import Any, Callable, Dict, Optional

from .constraints import META_FILE_NAME
from .utils import ensure_folder


class WithMetaMixin:
    """
    A mixin representing a model contains a meta file

    It assume that the object contains a field called _folder, which represents the folder
    the model has.
    """

    _folder: Path

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

    def _ensure_folder_with_meta(self, initial: Optional[Dict[str, str]] = None) -> bool:
        """
        Ensure the folder exists, if not, create the folder with an empty meta file.

        @initial: a dict contains the initial meta data if a new meta file is created

        Returns True if the folder already exists.
        """
        if ensure_folder(self._folder):
            assert self._meta_exists()
            return True
        else:
            self._meta.touch()
            if initial:
                for k, v in initial.items():
                    self._set_meta(k, v)

            return False

    def _get_meta(self, field: str, section='DEFAULT') -> Optional[str]:
        """
        Return a dict represents the meta data of the folder
        """
        config = configparser.ConfigParser()
        config.read(self._meta)
        return config.get(section, field, fallback=None)

    def _set_meta(self, field: str, value: str, section='DEFAULT'):
        """
        Set a value into the meta data field.

        If it is setted as None, it is equivalent to invoking `_del_meta`
        """

        if value is None:
            self._del_meta(field, section)

        config = configparser.ConfigParser()
        config.read(self._meta)

        try:
            config.set(section, field, value)
        except configparser.NoSectionError:
            config[section] = {field: value}

        with open(self._meta, 'w') as fr:
            config.write(fr)

    def _del_meta(self, field: str, section='DEFAULT'):
        """
        Remove a field from meta
        """
        config = configparser.ConfigParser()
        config.read(self._meta)
        try:
            config.remove_option(section, field)
            with open(self._meta, 'w') as fr:
                config.write(fr)
        except configparser.NoSectionError:
            pass


def meta_property(name: str, docstring: Optional[str] = None, *,
                  readonly=False,
                  setter: Callable[[Any], str] = None) -> property:
    """
    Create a property that reads and writes a field in meta file. Please ensure the class
    has `WithMetaMixin`

    @readonly: if it is True, only reading is available
    @setter: if it is provided, use it to transform input before writing meta data 

    Usage:
    ```
    class MyModel(WithMetaMixin, object):
        def __init__(self, id):
            ...

            self.my_field = self._make_meta_property(self, 'my_field', 'A description of my_field')

    # in other code
    m = MyModel(1)
    m.my_field = '123' # write
    print(m.my_field)  # read, if field does not exist, return None
    del m.my_field     # clear the field
    ```
    """

    def getx(self):
        return self._get_meta(name)

    def setx(self, value):
        if setter:
            value = setter(value)
        return self._set_meta(name, value)

    def delx(self):
        return self._del_meta(name)

    if readonly:
        return property(getx, doc=docstring)
    else:
        return property(getx, setx, delx, docstring)


def assign_properties(obj, kwargs: Dict[str, str]):
    for key, value in kwargs.items():
        setattr(obj, key, value)


class DeleteFolderMixin:
    """
    A mixin that adds operation to delete the folder this instance represents.

    The class must contains a _folder field.
    """

    _folder: Path

    def delete(self):
        """
        Remove the model, this process cannot be undone.

        After calling this method, invoking other methods are invalid.
        """
        shutil.rmtree(self._folder)
