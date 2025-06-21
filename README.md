# MHD Data Preprocessing Pipeline

This repository contains a complete data processing pipeline for converting raw Magnetohydrodynamics (MHD) simulation data into analysis-ready and machine-learning-ready datasets. Its sole purpose is to handle the parsing, merging, and formatting of data, creating a standardized set of `.npz` files that can be consumed by downstream ML models or analysis tools.

## Overview

The pipeline is orchestrated through a series of shell scripts that call underlying Python worker scripts. It is designed to be robust and repeatable, processing data for multiple Hartmann numbers (`ha`) in a consistent manner.

The core philosophy is the separation of code (this repository) and data (stored elsewhere). All scripts are configured by setting a single `DATA_DIR` variable, which points to the absolute path of your data storage location.

## Prerequisites

1.  **Python Environment:** A Python environment with all necessary packages installed. The core logic is contained within the `mhd_cae_koopman` Python package located in `pkgs/`. It is recommended to install this in editable mode:
    ```bash
    pip install -e pkgs/mhd_cae_koopman/
    ```
2.  **Data Storage:** A directory containing the raw simulation data, organized by Hartmann number (e.g., `.../re1000_ha300/`, `.../re1000_ha500/`, etc.).

## Configuration

Before running any scripts, you **must** configure the data path. Each primary shell script (e.g., `merge_all_uncompressed.sh`) contains a `User Configuration` section at the top.

**Example:**
```shell
# --- User Configuration ---
# IMPORTANT: Set this variable to the absolute path of your top-level data directory.
# This is the only line you should need to edit.
DATA_DIR="/path/to/your/data_directory"
```

You must edit this line in each script you intend to use.

## Data Processing Workflow

The pipeline should be run in the following sequence. Each step is idempotent, meaning it can be re-run without causing issues.

### Step 1: Parse Raw Data (Manual Step)

The initial raw data (e.g., `du.dat`, `dv.dat`) must be converted into an intermediate `.pkl` format. This is done using the `store_duvw_as_pickle.py` script. This step is currently not orchestrated by a master shell script and should be run manually for each source file as needed.

### Step 2: Merge Data into Uncompressed NPZ

This is the main processing step. It takes the intermediate `.pkl` files for each Hartmann number and merges them into a single, large, **uncompressed** `.npz` file. Uncompressed `.npz` files are optimized for fast loading during ML training.

```bash
./scripts/data_preprocessing/merge_data/merge_all_uncompressed.sh
```
**Output:** `.../vxyz_jxyz_p_f_du_dv_dw_uncompressed.npz` for each `ha`.

### Step 3: Create Development Datasets

To facilitate rapid prototyping and debugging, this script creates a very small "development" dataset by slicing the first few snapshots from the full uncompressed file.

```bash
./scripts/data_preprocessing/create_dev_data/create_all_dev_data.sh
```
**Output:** `.../vxyz_jxyz_p_f_du_dv_dw_dev.npz` for each `ha`.

### Step 4: (Optional) Create Compressed Archives

For long-term storage or portability, you can create compressed versions of the merged `.npz` files.

```bash
./scripts/data_preprocessing/merge_data/compress_all.sh
```
**Output:** `.../vxyz_jxyz_p_f_du_dv_dw_compressed.npz` for each `ha`.

### Step 5: (Optional) Stage Data for Training

This script copies the final datasets (e.g., the development sets) to a high-performance storage location, such as a `/raid` drive, for use in training jobs.

```bash
# Stage data for a specific Hartmann number
./scripts/data_preprocessing/stage_data_to_raid.sh 300

# Stage data for all Hartmann numbers
./scripts/data_preprocessing/stage_data_to_raid.sh --all
```

### Step 6: (Optional) Cleanup Intermediate Files

Once you have verified that the final `.npz` files are correct, you can run this script to remove the intermediate `.dat` and `.pkl` files to save disk space.

**WARNING:** This action is irreversible.

```bash
./scripts/cleanup/cleanup_intermediate_files.sh
```

## Utility Scripts

The repository contains several inspection scripts (e.g., `inspect_merged_dataset.py`) that can be used to verify the contents and integrity of the datasets at various stages of the pipeline.
