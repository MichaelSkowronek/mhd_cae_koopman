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
from typing import Tuple, List


def _pre_scan_tecplot(file_path: Path) -> Tuple[int, int, int, int, List[str]]:
    """Performs a quick first pass to determine the file's complete structure."""
    num_snapshots = 0
    headers = []
    
    re_title = re.compile(r'title', re.IGNORECASE)
    re_variables = re.compile(r'variables', re.IGNORECASE)

    # First, find total snapshots and headers
    with file_path.open('r') as f:
        for line in f:
            if re_title.match(line):
                num_snapshots += 1
            elif re_variables.match(line) and not headers:
                headers = [h.strip('"') for h in re.findall(r'"(.*?)"', line)]

    if num_snapshots == 0:
        return 0, 0, 0, 0, []

    # Second, read all points of the first snapshot to determine grid dimensions
    first_snapshot_points = []
    in_first_snapshot = False
    with file_path.open('r') as f:
        for line in f:
            line = line.strip()
            if re_title.match(line):
                if not in_first_snapshot:
                    in_first_snapshot = True
                else:
                    break  # End of first snapshot
            
            if in_first_snapshot and line and not re.match(r'title|variables|zone', line, re.IGNORECASE):
                try:
                    values = [float(v) for v in line.split()]
                    if headers and len(values) == len(headers):
                        first_snapshot_points.append(values)
                except ValueError:
                    continue
    
    if not first_snapshot_points:
        return num_snapshots, 0, 0, 0, headers

    # Calculate grid dimensions from the collected points
    first_snapshot_arr = np.array(first_snapshot_points)
    nx = len(np.unique(first_snapshot_arr[:, 0]))
    ny = len(np.unique(first_snapshot_arr[:, 1]))
    nz = len(np.unique(first_snapshot_arr[:, 2]))

    if nx * ny * nz != len(first_snapshot_arr):
        raise ValueError(
            "The data does not form a complete structured grid. "
            f"Calculated dimensions {nx}x{ny}x{nz}={nx*ny*nz} do not match "
            f"the number of points found ({len(first_snapshot_arr)})."
        )

    return num_snapshots, nx, ny, nz, headers


def parse_tecplot_timeseries(
    file_path: Path,
    *,
    dtype=np.float64,
) -> Tuple[np.ndarray, List[str]]:
    """
    Parses a large Tecplot ASCII timeseries file into a 5D NumPy array using a
    memory-efficient, pre-allocation approach. It automatically determines
    the grid dimensions from the first snapshot.

    Args:
        file_path (pathlib.Path or str): The path to the Tecplot data file.
        dtype (type, optional): The target NumPy data type for the array.
                                Defaults to np.float64.

    Returns:
        tuple: A tuple containing:
            - numpy.ndarray: A 5D array of shape (timesteps, nx, ny, nz, variables).
            - list: A list of strings containing the variable headers.
    """
    file_path = Path(file_path)

    print("Pre-scanning Tecplot file to determine structure...")
    num_snapshots, nx, ny, nz, headers = _pre_scan_tecplot(file_path)
    
    if num_snapshots == 0 or not headers:
        print("Warning: Could not determine file structure. No data will be parsed.")
        return np.empty((0, 0, 0, 0, 0), dtype=dtype), []

    num_points = nx * ny * nz
    num_variables = len(headers)
    print(f"  Found {num_snapshots} snapshots and {num_variables} variables.")
    print(f"  Determined grid dimensions: {nx} x {ny} x {nz} ({num_points} points/snapshot).")
    print(f"  Found headers: {headers}")

    print("Pre-allocating memory for the full 5D timeseries...")
    timeseries_data = np.zeros((num_snapshots, nx, ny, nz, num_variables), dtype=dtype)
    
    # Create a temporary buffer to hold one snapshot's flat data
    snapshot_buffer = np.zeros(num_points * num_variables, dtype=dtype)
    
    current_snapshot_index = -1
    current_point_index = 0
    
    re_title = re.compile(r'title', re.IGNORECASE)
    re_non_data = re.compile(r'title|variables|zone', re.IGNORECASE)

    with file_path.open('r') as file:
        total_lines = sum(1 for line in file)
        file.seek(0)
        
        for line_num, line in enumerate(tqdm(file, total=total_lines, desc="Reading Tecplot File", unit="lines")):
            line = line.strip()
            if not line:
                continue

            if re_title.match(line):
                # If we have finished a snapshot, process it
                if current_snapshot_index > -1:
                    # Reorder the flat buffer into the final grid structure
                    grid_zyx_view = snapshot_buffer.reshape((nz, ny, nx, num_variables))
                    grid_xyz_transposed_view = grid_zyx_view.transpose(2, 1, 0, 3)
                    timeseries_data[current_snapshot_index] = np.ascontiguousarray(grid_xyz_transposed_view)

                # Start new snapshot
                current_snapshot_index += 1
                current_point_index = 0
                continue
            
            if re_non_data.match(line):
                continue

            try:
                # Read values directly into the flat buffer
                start = current_point_index * num_variables
                end = start + num_variables
                snapshot_buffer[start:end] = np.fromstring(line, dtype=dtype, sep=' ')
                current_point_index += 1
            except (ValueError, IndexError) as e:
                # Raise an error for malformed lines instead of silently passing
                raise ValueError(
                    f"Error parsing data on line {line_num + 1}: '{line}'\n"
                    f"Expected {num_variables} values, but could not parse.\n"
                    f"Original error: {e}"
                )

    # Process the very last snapshot after the loop finishes
    if current_snapshot_index > -1:
        grid_zyx_view = snapshot_buffer.reshape((nz, ny, nx, num_variables))
        grid_xyz_transposed_view = grid_zyx_view.transpose(2, 1, 0, 3)
        timeseries_data[current_snapshot_index] = np.ascontiguousarray(grid_xyz_transposed_view)

    print("\nData parsing complete.")
    try:
        print(f"Data parsed successfully from path: {file_path.resolve(strict=True)}")
    except FileNotFoundError:
        print(f"Data parsed from non-resolvable path: {file_path}")

    return timeseries_data, headers
