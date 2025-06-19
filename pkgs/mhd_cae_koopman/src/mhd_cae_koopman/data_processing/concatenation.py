# -*- coding: UTF-8 -*-
"""
Data Loading and Concatenation Utilities
=========================================

This module provides a high-level function to load, validate, and concatenate
multiple 3D timeseries datasets stored in the 5D format
(timesteps, nx, ny, nz, variables).
"""

import gc
import numpy as np
from tqdm import tqdm
from mhd_cae_koopman.utils.pickle_io import load_object


def load_and_concatenate_data(
    path_vxyz_jxyz_p_f,
    path_du,
    path_dv,
    path_dw,
):
    """Loads, validates, and concatenates four 5D timeseries datasets.

    This function uses a highly memory-efficient, two-pass strategy. It first
    scans each file to gather metadata without holding them all in memory,
    then pre-allocates the final array, and finally copies data from each
    file one by one. It includes validation of grid dimensions and coordinates.

    Args:
        path_vxyz_jxyz_p_f (str or Path): Path to the base dataset file.
        path_du (str or Path): Path to the 'du' dataset file.
        path_dv (str or Path): Path to the 'dv' dataset file.
        path_dw (str or Path): Path to the 'dw' dataset file.

    Returns:
        dict: A dictionary containing the concatenated data, with two keys:
            - 'timeseries' (numpy.ndarray): The merged 5D NumPy array.
            - 'labels' (list): The merged list of variable labels.
    """
    datasets_to_process = {
        'vxyz_jxyz_p_f': path_vxyz_jxyz_p_f,
        'du': path_du,
        'dv': path_dv,
        'dw': path_dw
    }
    base_name = 'vxyz_jxyz_p_f'
    
    # --- Pass 1: Metadata Scan (Memory-Safe) ---
    print("--- Pass 1: Scanning files for metadata ---")
    metadata = {}
    base_coords_t0 = None
    for name, path in tqdm(datasets_to_process.items(), desc="Scanning files"):
        data = load_object(path)
        if data is None:
            raise ValueError(f"File '{name}' at {path} could not be loaded.")
        
        metadata[name] = {
            'shape': data['timeseries'].shape,
            'labels': data['labels']
        }
        
        # If this is the base file, store its first-timestep coordinates for later validation
        if name == base_name:
            base_coords_t0 = data['timeseries'][0, ..., :3].copy()
        
        del data
        gc.collect()

    # --- Step 2: Validation and Pre-allocation ---
    print("\n--- Starting Validation ---")
    base_meta = metadata[base_name]
    base_shape = base_meta['shape']
    
    if len(base_shape) != 5:
        raise ValueError(f"Base dataset '{base_name}' is not 5D. Shape: {base_shape}")
        
    base_timesteps, base_nx, base_ny, base_nz, _ = base_shape
    print(f"Base dataset ('{base_name}') shape: {base_shape}")

    total_variables = 0
    for name, meta in metadata.items():
        if name == base_name:
            total_variables += meta['shape'][4]
        else:
            # Grid dimension validation
            if (meta['shape'][0] != base_timesteps or meta['shape'][1] != base_nx or \
                meta['shape'][2] != base_ny or meta['shape'][3] != base_nz):
                raise ValueError(f"Dimension mismatch in '{name}'. Expected consistent grid, got {meta['shape']}")
            total_variables += meta['shape'][4] - 3 # Exclude x, y, z

    final_shape = (base_timesteps, base_nx, base_ny, base_nz, total_variables)
    print(f"Pre-allocating final array with shape: {final_shape}")
    final_timeseries = np.zeros(final_shape, dtype=np.float64) # Assuming float64
    
    # --- Pass 2: Data Copying and Coordinate Validation (Memory-Safe) ---
    print("\n--- Pass 2: Merging data into final array ---")
    current_var_index = 0
    
    for name, path in tqdm(datasets_to_process.items(), desc="Merging datasets"):
        data = load_object(path)
        timeseries = data['timeseries']
        
        if name == base_name:
            num_vars_to_copy = timeseries.shape[4]
            final_timeseries[..., :num_vars_to_copy] = timeseries
        else:
            # Coordinate value validation
            if not np.allclose(timeseries[0, ..., :3], base_coords_t0):
                raise ValueError(f"Coordinate values at t=0 do not match between base and '{name}'.")
            
            num_vars_to_copy = timeseries.shape[4] - 3
            final_timeseries[..., current_var_index : current_var_index + num_vars_to_copy] = timeseries[..., 3:]
        
        current_var_index += num_vars_to_copy
        del data, timeseries
        gc.collect()

    # --- Finalization ---
    final_labels = metadata[base_name]['labels'] + \
                   metadata['du']['labels'][3:] + \
                   metadata['dv']['labels'][3:] + \
                   metadata['dw']['labels'][3:]
    
    print(f"\nFinal concatenated timeseries shape: {final_timeseries.shape}")
    print(f"Final concatenated labels count: {len(final_labels)}")
    print("\n--- Concatenation Complete ---")
    
    return {
        'timeseries': final_timeseries,
        'labels': final_labels
    }
