# -*- coding: utf-8 -*-
"""
This module provides functionality to parse the binary 'duvw' data files.
"""

import os
import numpy as np
from pathlib import Path
from typing import List, Tuple
from tqdm import tqdm


def parse_duvw_binary(file_path: Path) -> Tuple[np.ndarray, List[str]]:
    """
    Reads a binary data file containing one or more timesteps efficiently.

    The binary file format is based on a Fortran routine that appends
    data for each timestep. Each block consists of:
    1. Three integer*4 values: nx, ny, nz
    2. A series of records, each with 6 double-precision values:
       x, y, z, and three other variables (e.g., du/dx, du/dy, du/dz).

    This function reads the data, which is already in C-contiguous order
    due to the Fortran loop structure (k, j, i), and loads it efficiently.

    Args:
        file_path (Path): The path to the binary .dat file.

    Returns:
        A tuple containing:
        - np.ndarray: C-contiguous NumPy array of shape (timesteps, points, 6),
                      where points is nx*ny*nz.
        - List[str]: A list of labels for the variables.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"Data file not found at: {file_path}")

    print(f"Optimized parsing of binary data from: {file_path}")
    try:
        with open(file_path, 'rb') as f:
            # --- Pre-computation Step ---
            # (1) Read the header of the first block to get dimensions.
            dims = np.fromfile(f, dtype=np.int32, count=3)
            if dims.size == 0:
                raise ValueError("File is empty or contains no valid data blocks.")
            
            nx, ny, nz = dims
            print(f"  Grid dimensions: nx={nx}, ny={ny}, nz={nz}")

            # (2) Calculate the size of a single timestep block in bytes.
            num_points = nx * ny * nz
            num_variables = 6
            header_size_bytes = dims.nbytes
            data_size_bytes = num_points * num_variables * np.dtype(np.float64).itemsize
            block_size_bytes = header_size_bytes + data_size_bytes

            # (3) Determine total number of timesteps from total file size.
            # Explicitly cast to 64-bit integers to prevent overflow on the modulo operation.
            total_file_size_64 = np.int64(os.path.getsize(file_path))
            block_size_bytes_64 = np.int64(block_size_bytes)
            
            if total_file_size_64 % block_size_bytes_64 != 0:
                raise ValueError(
                    "File size is not a multiple of the calculated block size. "
                    "The file might be corrupt or have inconsistent block sizes."
                )
            num_timesteps = int(total_file_size_64 // block_size_bytes_64)
            print(f"  Detected {num_timesteps} timestep(s) based on file size.")

            # --- Pre-allocation Step ---
            # (4) Pre-allocate the final NumPy array in C-order (the default).
            print("  Pre-allocating C-ordered memory for the full timeseries...")
            timeseries_data = np.zeros(
                (num_timesteps, num_points, num_variables), 
                dtype=np.float64,
            )
            
            # --- Filling Step ---
            # (5) Reset file pointer and loop through, filling the array.
            f.seek(0)
            for i in tqdm(range(num_timesteps), desc="Processing timesteps"):
                # Read and discard the header for this block
                f.seek(header_size_bytes, os.SEEK_CUR)

                # Read the data for one timestep directly into the final array's slice.
                # This is efficient as it avoids creating a large temporary chunk in memory.
                f.readinto(timeseries_data[i])

            print(f"  Successfully parsed {num_timesteps} timestep(s).")
            
            # Generate generic labels. The calling script can make these more specific.
            labels = ['x', 'y', 'z', 'var1', 'var2', 'var3']
            
            return timeseries_data, labels

    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")
        # Re-raise the exception to be handled by the calling script
        raise
