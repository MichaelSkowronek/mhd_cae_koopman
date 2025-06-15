# -*- coding: UTF-8 -*-
"""
Data Loading and Concatenation Utilities
=========================================

This module provides a high-level function to load, validate, and concatenate
multiple 3D timeseries datasets. It is designed to work with Python objects
stored in files, where each object is a dictionary containing 'timeseries'
and 'labels'.

The primary function ensures consistency in dimensions (timesteps, points) and
spatial coordinates across the datasets before merging them into a single,
comprehensive dataset.
"""

import numpy as np

from mhd_cae_koopman.utils import load_object


def load_and_concatenate_data(
    path_vxyz_jxyz_p_f,
    path_du,
    path_dv,
    path_dw,
):
    """Loads, validates, and concatenates four timeseries datasets.

    This function orchestrates the process of merging four datasets. It treats
    the first dataset as the base and validates the others against it to ensure
    that the number of timesteps, the number of data points, and the coordinate
    data for the first time entry are identical.

    Once validated, it concatenates the datasets along the variable axis,
    ensuring that the shared coordinate variables ('x', 'y', 'z') are included
    only once in the final merged dataset.

    Args:
        path_vxyz_jxyz_p_f (str): Path to the base dataset file.
        path_du (str): Path to the 'du' dataset file.
        path_dv (str): Path to the 'dv' dataset file.
        path_dw (str): Path to the 'dw' dataset file.

    Returns:
        dict: A dictionary containing the concatenated data, with two keys:
            - 'timeseries' (numpy.ndarray): The merged 3D NumPy array.
            - 'labels' (list): The merged list of variable labels.

    Raises:
        ValueError: If any data file cannot be loaded, or if the datasets
            are inconsistent in their dimensions or coordinate data.
    """
    print("--- Starting Data Loading ---")
    datasets_to_load = {
        'vxyz_jxyz_p_f': path_vxyz_jxyz_p_f,
        'du': path_du,
        'dv': path_dv,
        'dw': path_dw
    }
    
    loaded_data = {
        name: load_object(path) for name, path in datasets_to_load.items()
    }

    if any(data is None for data in loaded_data.values()):
        raise ValueError("One or more data files could not be loaded. Aborting.")

    print("\n--- Starting Validation ---")
    
    base_name = 'vxyz_jxyz_p_f'
    base_data = loaded_data[base_name]
    base_timeseries = base_data['timeseries']
    base_labels = base_data['labels']
    base_timesteps, base_points, _ = base_timeseries.shape

    print(f"Base dataset ('{base_name}') shape: {base_timeseries.shape}")

    # --- Validation Checks ---
    other_datasets = loaded_data.copy()
    del other_datasets[base_name]

    for name, data in other_datasets.items():
        current_timeseries = data['timeseries']
        current_labels = data['labels']
        print(f"Validating dataset: '{name}' with shape {current_timeseries.shape}")

        if (current_timeseries.shape[0] != base_timesteps or
                current_timeseries.shape[1] != base_points):
            raise ValueError(
                f"Dimension mismatch in '{name}'. "
                f"Expected ({base_timesteps}, {base_points}, N), "
                f"but got {current_timeseries.shape}."
            )

        if base_labels[:3] != current_labels[:3]:
            raise ValueError(
                f"Coordinate labels do not match between '{base_name}' "
                f"({base_labels[:3]}) and '{name}' ({current_labels[:3]})."
            )

        if not np.allclose(base_timeseries[0, :, :3], current_timeseries[0, :, :3]):
            raise ValueError(
                f"Coordinate values at t=0 do not match between "
                f"'{base_name}' and '{name}'."
            )
        
        print(f"Validation passed for '{name}'.")

    print("\n--- All validations successful. Starting Concatenation ---")

    # --- Concatenation ---
    timeseries_list = [base_timeseries]
    labels_list = [base_labels]
    
    for data in other_datasets.values():
        timeseries_list.append(data['timeseries'][:, :, 3:])
        labels_list.append(data['labels'][3:])

    final_timeseries = np.concatenate(timeseries_list, axis=2)
    print(f"Concatenated timeseries shape: {final_timeseries.shape}")

    final_labels = [label for sublist in labels_list for label in sublist]
    print(f"Concatenated labels count: {len(final_labels)}")
    
    print("\n--- Concatenation Complete ---")
    
    return {
        'timeseries': final_timeseries,
        'labels': final_labels
    }
