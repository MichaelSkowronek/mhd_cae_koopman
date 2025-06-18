# -*- coding: utf-8 -*-
"""
This module provides functionality to parse the binary 'duvw' data files.
"""

import os
import numpy as np
from pathlib import Path
from typing import List, Tuple
from tqdm import tqdm


def _parse_memory_optimized(f, num_timesteps, nx, ny, nz, num_variables, header_size_bytes) -> np.ndarray:
    """Processes the file iteratively, optimizing for low memory usage."""
    print("  Processing with memory-optimized strategy (slower, less RAM).")
    timeseries_data = np.zeros(
        (num_timesteps, nx, ny, nz, num_variables), 
        dtype=np.float64,
    )
    
    f.seek(0)
    for i in tqdm(range(num_timesteps), desc="Processing timesteps iteratively"):
        f.seek(header_size_bytes, os.SEEK_CUR)
        temp_chunk = np.fromfile(f, dtype=np.float64, count=(nx * ny * nz * num_variables))
        
        grid_zyx_view = temp_chunk.reshape((nz, ny, nx, num_variables))
        grid_xyz_transposed_view = grid_zyx_view.transpose(2, 1, 0, 3)
        grid_xyz_C_ordered = np.ascontiguousarray(grid_xyz_transposed_view)
        
        timeseries_data[i] = grid_xyz_C_ordered
        
    return timeseries_data


def _parse_speed_optimized(f, num_timesteps, nx, ny, nz, num_variables, header_size_bytes) -> np.ndarray:
    """Processes the file in a single vectorized operation, optimizing for speed."""
    print("  Processing with speed-optimized strategy (faster, more RAM).")
    
    # Pre-allocate array to hold the raw, C-ordered (but logically z,y,x) data
    raw_timeseries = np.zeros(
        (num_timesteps, nz * ny * nx * num_variables),
        dtype=np.float64
    )
    
    # Read all data blocks into the array at once
    f.seek(0)
    for i in tqdm(range(num_timesteps), desc="Reading all data blocks"):
        f.seek(header_size_bytes, os.SEEK_CUR)
        f.readinto(raw_timeseries[i])
        
    # Perform the reordering on the entire dataset at once
    print("  Re-ordering all timesteps in a single operation...")
    grid_zyx_view_full = raw_timeseries.reshape((num_timesteps, nz, ny, nx, num_variables))
    grid_xyz_transposed_view_full = grid_zyx_view_full.transpose(0, 3, 2, 1, 4)
    timeseries_data = np.ascontiguousarray(grid_xyz_transposed_view_full)
    
    return timeseries_data


def parse_duvw_binary(file_path: Path, memory_optimized: bool = True) -> Tuple[np.ndarray, List[str]]:
    """
    Reads a binary data file containing one or more timesteps efficiently.

    This function can use two strategies:
    1. Memory-optimized (default): Processes the file timestep by timestep. This is
       slower but requires much less peak RAM, making it safe for very large
       files on typical systems.
    2. Speed-optimized: Reads the entire file into memory and performs one
       large re-ordering operation. This is significantly faster but requires
       at least 2x the file size in available RAM.

    Args:
        file_path (Path): The path to the binary .dat file.
        memory_optimized (bool, optional): If True (default), uses the low-memory
                                           strategy. If False, uses the faster,
                                           high-memory strategy.

    Returns:
        A tuple containing:
        - np.ndarray: C-contiguous NumPy array of shape (timesteps, nx, ny, nz, 6).
        - List[str]: A list of labels for the variables.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"Data file not found at: {file_path}")

    print(f"Optimized parsing of binary data from: {file_path}")
    try:
        with open(file_path, 'rb') as f:
            # --- Pre-computation Step (common for both strategies) ---
            dims = np.fromfile(f, dtype=np.int32, count=3)
            if dims.size == 0:
                raise ValueError("File is empty or contains no valid data blocks.")
            
            nx, ny, nz = dims
            print(f"  Grid dimensions: nx={nx}, ny={ny}, nz={nz}")

            num_points = nx * ny * nz
            num_variables = 6
            header_size_bytes = dims.nbytes
            data_size_bytes = num_points * num_variables * np.dtype(np.float64).itemsize
            block_size_bytes = header_size_bytes + data_size_bytes

            total_file_size_64 = np.int64(os.path.getsize(file_path))
            block_size_bytes_64 = np.int64(block_size_bytes)
            
            if total_file_size_64 % block_size_bytes_64 != 0:
                raise ValueError(
                    "File size is not a multiple of the calculated block size. "
                    "The file might be corrupt or have inconsistent block sizes."
                )
            num_timesteps = int(total_file_size_64 // block_size_bytes_64)
            print(f"  Detected {num_timesteps} timestep(s) based on file size.")

            # --- Strategy Selection ---
            if memory_optimized:
                timeseries_data = _parse_memory_optimized(f, num_timesteps, nx, ny, nz, num_variables, header_size_bytes)
            else:
                timeseries_data = _parse_speed_optimized(f, num_timesteps, nx, ny, nz, num_variables, header_size_bytes)
                
            print(f"  Successfully parsed and re-ordered {num_timesteps} timestep(s).")
            
            labels = ['x', 'y', 'z', 'var1', 'var2', 'var3']
            
            return timeseries_data, labels

    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")
        # Re-raise the exception to be handled by the calling script
        raise
