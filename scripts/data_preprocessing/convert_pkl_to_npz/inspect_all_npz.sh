#!/bin/bash

# ==============================================================================
# This script inspects all individual processed .npz files by loading them
# and printing their summary information.
# ==============================================================================

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
HA_NUMBERS=(300 500 700 1000)
# This path should be relative to the location of THIS script.
# It points to the top-level 'data' directory for the project.
DATA_DIR="../../../../../../data"
INSPECT_SCRIPT="inspect_npz_datasets.py" # Assumes it's in the same directory

# These are the base names of the files that were converted to .npz
FILE_NAMES_NPZ=(
    "vxyz_jxyz_p_f.npz"
    "du.npz"
    "dv.npz"
    "dw.npz"
)

# --- Main Processing Loop ---
echo "================================================="
echo "Inspecting all processed .npz files"
echo "================================================="

for ha in "${HA_NUMBERS[@]}"; do
    echo ""
    echo "--- Processing for ha=$ha ---"
    
    for file_name_npz in "${FILE_NAMES_NPZ[@]}"; do
        
        echo ""
        echo "Inspecting ${file_name_npz} for ha=${ha}..."

        COMMAND="python $INSPECT_SCRIPT --ha $ha --data_dir $DATA_DIR --file_name $file_name_npz"
        echo "Running command: $COMMAND"
        $COMMAND
    done
done

echo ""
echo "================================================="
echo "All inspections complete."
echo "================================================="