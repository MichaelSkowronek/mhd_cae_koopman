#!/bin/bash

# ==============================================================================
# This script inspects all individual processed .npz files by loading them
# and printing their summary information.
# ==============================================================================

# Exit immediately if a command exits with a non-zero status.
set -e

# --- User Configuration ---
# IMPORTANT: Set this variable to the absolute path of your top-level data directory.
# This is the only line you should need to edit.
DATA_DIR="/home/skowronek/Documents/PhD/nuclear_fusion_cooling/data"

# --- Script Configuration ---
HA_NUMBERS=(300 500 700 1000)

# Get the absolute path of the directory where this script is located.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSPECT_SCRIPT="${SCRIPT_DIR}/inspect_npz_datasets.py"

# --- Sanity Checks ---
if [ "$DATA_DIR" == "/path/to/your/data_directory" ]; then
    echo "Error: Please edit this script and set the DATA_DIR variable to the correct path." >&2
    exit 1
fi

if [ ! -d "$DATA_DIR" ]; then
    echo "Error: The specified data directory does not exist: $DATA_DIR" >&2
    exit 1
fi

if [ ! -f "$INSPECT_SCRIPT" ]; then
    echo "Error: The python helper script was not found at: $INSPECT_SCRIPT" >&2
    exit 1
fi

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