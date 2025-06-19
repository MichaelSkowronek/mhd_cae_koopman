# -*- coding: UTF-8 -*-
"""
NumPy I/O Utilities
===================

This module provides memory-efficient functions for saving and loading
dictionaries containing large NumPy arrays using NumPy's native .npz format.
This is significantly more performant than using pickle for this purpose.
"""
import numpy as np
from pathlib import Path


def save_numpy_object(
    obj: dict,
    file_path: Path,
    compressed: bool = True,
):
    """
    Saves a dictionary containing NumPy arrays to an .npz file.

    Args:
        obj (dict): The dictionary to save. Keys will be used as names inside
                    the archive. Non-array values (like lists of labels) are
                    supported.
        file_path (Path): The path for the output .npz file.
        compressed (bool, optional): If True (default), saves as a smaller,
                                     compressed .npz file. If False, saves as a
                                     larger, uncompressed file for faster I/O.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Choose the save function based on the compression flag
        if compressed:
            np.savez_compressed(file_path, **obj)
        else:
            np.savez(file_path, **obj)
            
        print(f"Object successfully saved to {file_path.resolve(strict=True)}")
    except Exception as e:
        print(f"An error occurred during saving to {file_path}: {e}")
        raise


def load_numpy_object(file_path: Path) -> dict:
    """
    Loads data from a .npz file into a dictionary.

    Args:
        file_path (Path): The path to the input .npz file.

    Returns:
        dict: The reconstructed dictionary.
    """
    file_path = Path(file_path)
    
    try:
        # np.load for .npz files returns a lazy-loading NpzFile object.
        # We must explicitly reconstruct the dictionary.
        with np.load(file_path, allow_pickle=True) as data:
            reconstructed_obj = {}
            for key in data.files:
                # .item() is used to extract scalar/object arrays (like our list of labels)
                if data[key].shape == ():
                    reconstructed_obj[key] = data[key].item()
                else:
                    reconstructed_obj[key] = data[key]
        print(f"Object successfully loaded from {file_path.resolve(strict=True)}")
        return reconstructed_obj
    except Exception as e:
        print(f"An error occurred during loading from {file_path}: {e}")
        raise
