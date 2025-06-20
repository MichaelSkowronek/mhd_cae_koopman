#!/bin/bash

# ==============================================================================
# This script converts all individual processed .pkl files into compressed
# .npz files for portable, archival storage.
# ==============================================================================

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
HA_NUMBERS=(300 500 700 1000)
DATA_DIR="../../../../../../data/"
CONVERTER_SCRIPT="pkl_to_npz_converter.py"
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
