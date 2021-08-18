"""
Utility functions
"""

from pathlib import Path
from datetime import datetime
from typing import Iterable


def ensure_folder(path: Path) -> bool:
    """
    Ensure the folder in path exists. If it does not exist, create the folder

    Return whether the folder exists before invoking this function.
    """

    if not path.exists():
        path.mkdir()
        return False
    else:
        assert path.is_dir(), 'The path should be a folder'
        return True


def datetime_to_iso(time: datetime) -> str:
    """
    Converts a datetime object into ISO8601 format with current timezone, without microsecond
    """
    return time.astimezone().replace(microsecond=0).isoformat()


def iter_subfolders(folder: Path) -> Iterable[Path]:
    """
    Iterate through the folder, yield each subfolders
    """

    for file in folder.iterdir():
        if not file.is_dir():
            continue
        yield file
