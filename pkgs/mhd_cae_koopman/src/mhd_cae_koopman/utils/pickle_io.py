# -*- coding: UTF-8 -*-
"""
Pickle I/O Utilities
====================

This module provides general-purpose functions for saving and loading
any Python object using the pickle serialization protocol.
"""

import pickle
from pathlib import Path


def save_object(obj, file_path: Path):
    """
    Save a Python object to a file using pickle.

    Args:
        obj: The Python object to save.
        file_path (Path): The path for the output .pkl file.
    """
    file_path = Path(file_path)

    # Ensure parent directories exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Save the object using pickle
        with file_path.open('wb') as f:
            pickle.dump(obj, f)
        print(f"Object successfully saved to {file_path.resolve(strict=True)}")
    except Exception as e:
        print(f"An error occurred during saving to {file_path}: {e}")
        raise


def load_object(file_path: Path):
    """
    Loads a Python object from a pickle file.

    Args:
        file_path (Path): The path to the input .pkl file.

    Returns:
        The loaded Python object, or None if an error occurs.
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        print(f"Error: File not found at {file_path}")
        return None

    try:
        with file_path.open('rb') as f:
            obj = pickle.load(f)
        print(f"Object successfully loaded from {file_path.resolve(strict=True)}")
        return obj
    except Exception as e:
        print(f"An error occurred during loading from {file_path}: {e}")
        return None
