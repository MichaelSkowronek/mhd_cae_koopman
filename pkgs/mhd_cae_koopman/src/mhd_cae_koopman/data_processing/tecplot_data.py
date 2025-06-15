# -*- coding: UTF-8 -*-
"""
Data Processing Utilities for 3D Timeseries Data
=================================================

This module provides functions for parsing and inspecting timeseries data from
Tecplot ASCII files. It is designed to handle files where each time step
(snapshot) contains a list of data points, and coordinates (x, y, z) are
treated as standard variables alongside other physical quantities.
"""

import re
import numpy as np
from pathlib import Path


def parse_tecplot_timeseries(
    file_path,
    *,
    dtype=float,
):
    """Parses a Tecplot ASCII timeseries file into a 3D NumPy array.

    This function reads a Tecplot data file structured with distinct time steps,
    often referred to as snapshots or zones. It assumes that each snapshot begins
    with a 'TITLE' line and contains a block of numerical data. The variables,
    including any coordinates like 'x', 'y', and 'z', are extracted from a
    'VARIABLES' line.

    The entire dataset is loaded into a single 3D NumPy array with the
    following dimensions:
    1.  Time: The index of the snapshot.
    2.  Points: The index of the data point within a snapshot.
    3.  Variables: The index of the variable for that point.

    Args:
        file_path (pathlib.Path or str): The path to the Tecplot data file.
        dtype (type, optional): The target NumPy data type for the array.
            Defaults to float.

    Returns:
        tuple: A tuple containing:
            - numpy.ndarray: A 3D array of shape (time, points, variables).
              Returns an empty array if no data is found.
            - list: A list of strings containing the variable headers.
    """
    file_path = Path(file_path)

    # Precompile case-insensitive regex patterns for parsing Tecplot keywords.
    re_title = re.compile(r'title', re.IGNORECASE)
    re_variables = re.compile(r'variables', re.IGNORECASE)
    re_zone = re.compile(r'zone', re.IGNORECASE)

    all_snapshots = []
    current_snapshot_data = []
    headers = []

    with file_path.open('r') as file:
        for line in file:
            line = line.strip()

            if not line:  # Skip empty lines
                continue

            # 'title' marks the beginning of a new snapshot. The data from the
            # previous snapshot is stored, and the buffer is cleared.
            if re_title.match(line):
                if current_snapshot_data:
                    all_snapshots.append(current_snapshot_data)
                current_snapshot_data = []  # Reset for the new snapshot

            # 'variables' defines the data headers. This is parsed only once.
            elif re_variables.match(line):
                if not headers:
                    # Extracts all quoted strings from the line to form headers.
                    headers = [h.strip('"') for h in re.findall(r'"(.*?)"', line)]

            # 'zone' lines are part of the Tecplot format but are not used here.
            elif re_zone.match(line):
                continue

            # Lines that are not keywords are treated as numerical data.
            else:
                try:
                    values = [dtype(v) for v in line.split()]
                    # Ensure the number of values matches the number of headers.
                    if headers and len(values) == len(headers):
                        current_snapshot_data.append(values)
                    elif headers:
                        print(f"Warning: Skipping line with mismatched number of values: {line}")
                except ValueError:
                    print(f"Warning: Could not convert line to data type '{dtype.__name__}': {line}")

    # After the loop, append the final snapshot if it exists.
    if current_snapshot_data:
        all_snapshots.append(current_snapshot_data)

    if not all_snapshots:
        return np.empty((0, 0, 0), dtype=dtype), []

    # Verify that all snapshots have a consistent number of points.
    first_snapshot_points = len(all_snapshots[0])
    if not all(len(snap) == first_snapshot_points for snap in all_snapshots):
        print("Warning: Snapshots have an inconsistent number of data points.")

    try:
        print(f"Data parsed successfully from path: {file_path.resolve(strict=True)}")
    except FileNotFoundError:
        print(f"Data parsed from non-resolvable path: {file_path}")


    # Stack the list of 2D snapshot arrays into a single 3D array.
    timeseries_array = np.array(all_snapshots, dtype=dtype)

    return timeseries_array, headers


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
