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
