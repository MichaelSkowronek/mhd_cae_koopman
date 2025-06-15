# -*- coding: UTF-8 -*-


import re
from pathlib import Path
import numpy as np


def read_first_n_lines(
    file_path,
    n
):
    """
    Reads the first n lines from a file without loading the entire file into memory.

    Parameters:
        file_path (str): The path to the file.
        n (int): The number of lines to read from the beginning of the file.

    Returns:
        list: A list containing the first n lines of the file.
    """
    file_path = Path(file_path)
    lines = []
    
    with open(file_path, 'r') as file:
        for _ in range(n):
            line = file.readline()
            if not line:  # Stop if we reach EOF
                break
            lines.append(line.strip())
    
    return lines


def truncate_file_at_line(
        filepath,
        line_number,
        output_filepath=None,
):
    """
    Creates a truncated copy of a file at the specified line number.

    Args:
        filepath (str): The path to the original file.
        line_number (int): The line number at which to truncate the file.
        output_filepath (str, optional): The path for the truncated copy. 
                                          If not provided, a default name will be used.

    Returns:
        Path: The path of the truncated file.
    """
    filepath = Path(filepath)
    
    try:
        # Determine output file path
        if output_filepath is None:
            # Create a new filename for the truncated copy
            truncated_filepath = filepath.with_name(f"{filepath.stem}_truncated{filepath.suffix}")
        else:
            truncated_filepath = Path(output_filepath)

        with filepath.open('r') as f, truncated_filepath.open('w') as new_file:
            for current_line_number, line in enumerate(f):
                if current_line_number < line_number:
                    new_file.write(line)
                else:
                    break  # Stop reading when we've written enough lines

        # Print success message with resolved paths
        print(f"Truncated file created at\n"
              f"{truncated_filepath.resolve(strict=True)}\n"
              f"from original file at\n"
              f"{filepath.resolve(strict=True)}")

        return truncated_filepath.resolve(strict=True)  # Return the resolved path of the truncated file

    except FileNotFoundError:
        print(f"Error: File not found at {filepath.resolve(strict=True)}")
    except Exception as e:
        print(f"An error occurred: {e}")


def count_pattern_in_file(
        file_path,
        pattern,
):
    compiled_pattern = re.compile(pattern)  # Compile the provided regex pattern once
    count = 0
    
    with open(file_path, 'r') as file:
        for line in file:
            if compiled_pattern.match(line):  # Use the compiled pattern for matching
                count += 1
                
    return count
