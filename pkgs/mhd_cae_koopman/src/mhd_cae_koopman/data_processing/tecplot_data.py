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
from tqdm import tqdm


def parse_tecplot_timeseries(
    file_path,
    *,
    dtype=np.float64,
):
    """
    Parses a large Tecplot ASCII timeseries file into a 3D NumPy array using a
    memory-efficient, snapshot-by-snapshot approach with a progress bar.

    This function reads the file line-by-line, converting each snapshot into a
    NumPy array before reading the next one. This avoids loading the entire
    file into a Python list, preventing out-of-memory errors for very large files.
    The entire dataset is loaded into a single 3D NumPy array with the
    following dimensions:
    1.  Time: The index of the snapshot.
    2.  Points: The index of the data point within a snapshot.
    3.  Variables: The index of the variable for that point.

    Args:
        file_path (pathlib.Path or str): The path to the Tecplot data file.
        dtype (type, optional): The target NumPy data type for the array.
                                Defaults to np.float64 (standard float).
                                Use np.float32 for reduced memory usage.

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

    all_snapshots_np = []
    current_snapshot_data = []
    headers = []
    snapshot_count = 0

    print(f"Starting memory-efficient parsing of: {file_path}")
    print(f"Using data type: {np.dtype(dtype).name}")

    # First pass to count lines for the progress bar
    print("Performing first pass to count lines for progress bar...")
    with file_path.open('r') as f:
        total_lines = sum(1 for line in f)

    with file_path.open('r') as file:
        # Wrap the file object with tqdm for a progress bar
        for line in tqdm(file, total=total_lines, desc="Reading Tecplot File", unit="lines"):
            line = line.strip()

            if not line:  # Skip empty lines
                continue

            # 'title' marks the beginning of a new snapshot. The data from the
            # previous snapshot is processed and stored.
            if re_title.match(line):
                if current_snapshot_data:
                    snapshot_count += 1
                    # Convert the completed snapshot to a NumPy array
                    snapshot_np = np.array(current_snapshot_data, dtype=dtype)
                    all_snapshots_np.append(snapshot_np)
                
                # Reset buffer for the new snapshot
                current_snapshot_data = []

            # 'variables' defines the data headers. This is parsed only once.
            elif re_variables.match(line):
                if not headers:
                    # Extracts all quoted strings from the line to form headers.
                    headers = [h.strip('"') for h in re.findall(r'"(.*?)"', line)]
                    print(f"\nFound headers: {headers}")

            # 'zone' lines are part of the Tecplot format but are not used here.
            elif re_zone.match(line):
                continue

            # Lines that are not keywords are treated as numerical data.
            else:
                try:
                    # Append row data as a list of floats
                    values = [float(v) for v in line.split()]
                    if headers and len(values) == len(headers):
                        current_snapshot_data.append(values)
                except (ValueError, IndexError):
                     # This will slow down the process, so it's commented out by default
                     # print(f"Warning: Skipping malformed data line: {line}")
                     pass


    # After the loop, append the final snapshot if it exists.
    if current_snapshot_data:
        snapshot_count += 1
        snapshot_np = np.array(current_snapshot_data, dtype=dtype)
        all_snapshots_np.append(snapshot_np)

    if not all_snapshots_np:
        print("Warning: No data was parsed.")
        return np.empty((0, 0, 0), dtype=dtype), []

    # Verify that all snapshots have a consistent number of points.
    first_snapshot_points = all_snapshots_np[0].shape[0]
    if not all(snap.shape[0] == first_snapshot_points for snap in all_snapshots_np):
        print("Warning: Snapshots have an inconsistent number of data points.")


    print("\nAll snapshots processed. Stacking into a final 3D array...")
    # FIX: Convert the tqdm iterator back to a list before passing to np.stack
    timeseries_array = np.stack(list(tqdm(all_snapshots_np, desc="Stacking Snapshots")))
    print("Stacking complete.")


    try:
        print(f"Data parsed successfully from path: {file_path.resolve(strict=True)}")
    except FileNotFoundError:
        print(f"Data parsed from non-resolvable path: {file_path}")

    return timeseries_array, headers
