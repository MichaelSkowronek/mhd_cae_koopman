#!/bin/bash

# ==============================================================================
# This script creates small development datasets from the full, uncompressed
# merged datasets. It extracts the first N snapshots for rapid testing.
# ==============================================================================

# Exit immediately if a command exits with a non-zero status.
set -e

# --- User Configuration ---
# IMPORTANT: Set this variable to the absolute path of your top-level data directory.
# This is the only line you should need to edit.
DATA_DIR="/home/skowronek/Documents/PhD/nuclear_fusion_cooling/data"

# --- Script Configuration ---
HA_NUMBERS=(300 500 700 1000)
NUM_SNAPSHOTS=2

# Get the absolute path of the directory where this script is located to robustly find other scripts.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_SCRIPT="${SCRIPT_DIR}/create_dev_dataset.py"

# --- Sanity Checks ---
if [ "$DATA_DIR" == "/path/to/your/data_directory" ]; then
    echo "Error: Please edit this script and set the DATA_DIR variable to the correct path." >&2
    exit 1
fi

if [ ! -d "$DATA_DIR" ]; then
    echo "Error: The specified data directory does not exist: $DATA_DIR" >&2
    exit 1
fi

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: The python helper script was not found at: $PYTHON_SCRIPT" >&2
    exit 1
fi

# --- Main Processing Loop ---
echo "================================================="
echo "Creating Development Datasets"
echo "================================================="

for ha in "${HA_NUMBERS[@]}"; do
    echo ""
    echo "--- Creating dev set for ha=$ha ---"
    
    # Define the input and output filenames
    BASE_PATH="${DATA_DIR}/re1000_ha${ha}/3d/pkl"
    INPUT_FILE="${BASE_PATH}/vxyz_jxyz_p_f_du_dv_dw_uncompressed.npz"
    OUTPUT_FILE="${BASE_PATH}/vxyz_jxyz_p_f_du_dv_dw_dev.npz"

    # Construct and run the command to create the dev set
    COMMAND="python $PYTHON_SCRIPT --input_file $INPUT_FILE --output_file $OUTPUT_FILE --snapshots $NUM_SNAPSHOTS"
    echo "Running command: $COMMAND"
    $COMMAND
done

echo ""
echo "================================================="
echo "All development datasets created successfully."
echo "================================================="