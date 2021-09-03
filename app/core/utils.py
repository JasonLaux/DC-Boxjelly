"""
Utility functions
"""

from pathlib import Path
from datetime import datetime
from typing import Iterator
import itertools
from collections import deque


def ensure_folder(path: Path) -> bool:
    """
    Ensure the folder in path exists. If it does not exist, create the folder

    Return whether the folder exists.
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


def iter_subfolders(folder: Path) -> Iterator[Path]:
    """
    Iterate through the folder, yield each subfolders
    """

    for file in folder.iterdir():
        if not file.is_dir():
            continue
        yield file


def count_iter_items(iterable):
    # from https://stackoverflow.com/a/15112059
    """
    Consume an iterable not reading it into memory; return the number of items.
    """
    counter = itertools.count()
    deque(zip(iterable, counter), maxlen=0)  # (consume at C speed)
    return next(counter)
