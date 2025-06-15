# -*- coding: UTF-8 -*-
"""Python Utils.
"""


import pickle
from pathlib import Path
import numpy as np


def save_object(obj, file_path):
    """
    Save a Python object to a file, creating parent directories if necessary.
    
    :param obj: The Python object to save
    :param file_path: The path of the file where the object will be stored (can be a string or Path)
    """
    file_path = Path(file_path)

    # Ensure parent directories exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Save the object using pickle
    with file_path.open('wb') as file:
        pickle.dump(obj, file)
    print(f"Object successfully saved to {file_path.resolve(strict=True)}")
        

def load_object(file_path):
    """
    Load a Python object from a file.
    
    :param file_path: The path of the file where the object is stored
    :return: The loaded Python object
    """
    file_path = Path(file_path)
    try:
        with file_path.open('rb') as file:
            obj = pickle.load(file)
        print(f"Object successfully loaded from {file_path.resolve(strict=True)}")
        return obj
    except Exception as e:
        print(f"An error occurred while loading the object: {e}")
        return None
