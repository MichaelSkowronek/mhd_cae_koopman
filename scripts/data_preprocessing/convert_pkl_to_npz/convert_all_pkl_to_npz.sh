#!/bin/bash

# ==============================================================================
# This script converts all individual processed .pkl files into compressed
# .npz files for portable, archival storage.
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
CONVERTER_SCRIPT="${SCRIPT_DIR}/pkl_to_npz_converter.py"

# --- Sanity Checks ---
if [ "$DATA_DIR" == "/path/to/your/data_directory" ]; then
    echo "Error: Please edit this script and set the DATA_DIR variable to the correct path." >&2
    exit 1
fi

if [ ! -d "$DATA_DIR" ]; then
    echo "Error: The specified data directory does not exist: $DATA_DIR" >&2
    exit 1
fi

if [ ! -f "$CONVERTER_SCRIPT" ]; then
    echo "Error: The python helper script was not found at: $CONVERTER_SCRIPT" >&2
    exit 1
fi

FILE_NAMES=(
    "vxyz_jxyz_p_f"
    "du"
    "dv"
    "dw"
)

# --- Main Processing Loop ---
echo "================================================="
echo "Converting all .pkl files to compressed .npz"
echo "================================================="

for ha in "${HA_NUMBERS[@]}"; do
    echo ""
    echo "--- Processing for ha=$ha ---"
    
    for file_name in "${FILE_NAMES[@]}"; do
        
        # Define the input and output filenames
        BASE_PATH="${DATA_DIR}/re1000_ha${ha}/3d/pkl"
        INPUT_FILE="${BASE_PATH}/${file_name}.pkl"
        OUTPUT_FILE="${BASE_PATH}/${file_name}.npz"

        echo ""
        echo "Converting ${file_name}.pkl..."

        # Construct and run the command
        COMMAND="python $CONVERTER_SCRIPT $INPUT_FILE $OUTPUT_FILE"
        echo "Running command: $COMMAND"
        $COMMAND
    done
done

echo ""
echo "================================================="
echo "All conversions complete."
echo "================================================="
