"""
Utility functions
"""

from pathlib import Path

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
