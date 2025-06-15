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


def print_timeseries_info(
    timeseries,
    labels,
    *,
    coord_indices=(0, 1, 2)
):
    """Prints a summary of a loaded timeseries dataset.

    This function provides a human-readable overview of a timeseries array,
    displaying its dimensions, the names of its variables, the calculated
    grid dimensions, and a small preview of the data.

    Args:
        timeseries (numpy.ndarray): A 3D NumPy array with dimensions
            representing (time, points, variables).
        labels (list): A list of strings for each variable.
        coord_indices (tuple, optional): A tuple of three integers representing
            the column indices of the x, y, and z coordinate variables.
            Defaults to (0, 1, 2).
    """
    # Validate that the input array is a non-empty 3D array.
    if not isinstance(timeseries, np.ndarray) or timeseries.ndim != 3 or timeseries.size == 0:
        print("Cannot display info: Data is empty or not a valid 3D NumPy array.")
        return

    print("\n" + "="*30)
    print("Timeseries Data Summary")
    print("="*30)

    # Extract dimensions for clarity.
    num_snapshots, num_points, num_variables = timeseries.shape

    print(f"Number of snapshots (time steps): {num_snapshots}")
    print(f"Number of points per snapshot:    {num_points}")
    print(f"Number of variables:              {num_variables}")

    # Calculate and print grid dimensions.
    grid_dims = get_grid_dimensions(timeseries, coord_indices=coord_indices)
    if grid_dims:
        nx, ny, nz = grid_dims
        print(f"Calculated grid dimensions:       {nx} x {ny} x {nz} (using indices {coord_indices})")


    print("\n--- Variable Labels ---")
    print(labels)

    # Display a small segment of the data for a quick quality check.
    print("\n--- Data Preview (First 5 points of first snapshot) ---")
    preview_count = min(5, num_points)

    if preview_count == 0:
        print("No data points to preview.")
    else:
        for i in range(preview_count):
            print(f"  Point {i+1:<2}: {timeseries[0, i, :]}")
    print("="*30)


def get_grid_dimensions(
    timeseries,
    *,
    coord_indices=(0, 1, 2),
):
    """Calculates the number of unique points along specified coordinate axes.

    This function assumes the data represents a structured grid and counts the
    number of unique values for each specified coordinate in the first time
    step to determine the grid's dimensions.

    Args:
        timeseries (numpy.ndarray): A 3D NumPy array with dimensions
            representing (time, points, variables).
        coord_indices (tuple, optional): A tuple of three integers representing
            the column indices of the x, y, and z coordinate variables.
            Defaults to (0, 1, 2).

    Returns:
        tuple or None: A tuple containing the number of unique points on the
        x, y, and z axes (nx, ny, nz). Returns None if the data is invalid
        or if coordinate indices are out of bounds.
    """
    # Validate that the input array is a non-empty 3D array.
    if not isinstance(timeseries, np.ndarray) or timeseries.ndim != 3 or timeseries.size == 0:
        # Silently fail for internal call, parent function will print error.
        return None

    if len(coord_indices) != 3:
        print(f"Error (get_grid_dimensions): Expected 3 coordinate indices, but got {len(coord_indices)}.")
        return None

    # Check if indices are valid for the given timeseries array.
    num_variables = timeseries.shape[2]
    if not all(0 <= i < num_variables for i in coord_indices):
        print(f"Error (get_grid_dimensions): One or more coordinate indices {coord_indices} are out of bounds for the number of variables ({num_variables}).")
        return None

    x_idx, y_idx, z_idx = coord_indices

    # We only need to inspect the first snapshot to determine grid dimensions,
    # assuming the grid structure is constant over time.
    first_snapshot_data = timeseries[0, :, :]

    # Extract the coordinate columns using the identified indices.
    x_coords = first_snapshot_data[:, x_idx]
    y_coords = first_snapshot_data[:, y_idx]
    z_coords = first_snapshot_data[:, z_idx]

    # Count the number of unique values in each coordinate column.
    nx = len(np.unique(x_coords))
    ny = len(np.unique(y_coords))
    nz = len(np.unique(z_coords))

    return (nx, ny, nz)
