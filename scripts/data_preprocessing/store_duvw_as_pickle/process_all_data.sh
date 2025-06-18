#!/bin/bash

# ==============================================================================
# This script automates the processing of binary du, dv, and dw data files
# for a range of different Hartmann numbers (ha).
# It calls the main Python processing script with the correct parameters.
# ==============================================================================

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
HA_NUMBERS=(300 500 700 1000)
FILE_PREFIXES=("du" "dv" "dw")
DATA_DIR="../../../../../../data/"
PYTHON_SCRIPT="store_duvw_as_pickle.py"

# --- Main Processing Loop ---
echo "Starting data processing batch job..."

# Loop over each Hartmann number
for ha in "${HA_NUMBERS[@]}"; do
    echo ""
    echo "================================================="
    echo "Processing for Hartmann number (ha): $ha"
    echo "================================================="

    # Loop over each file prefix (du, dv, dw)
    for prefix in "${FILE_PREFIXES[@]}"; do
        FILE_NAME="${prefix}.dat"
        
        echo ""
        echo "--- Processing file: $FILE_NAME for ha=$ha ---"
        
        # Construct the full command
        COMMAND="python $PYTHON_SCRIPT --ha $ha --file_name $FILE_NAME --data_dir $DATA_DIR --verify --fast-mode"
        
        # Print the command for logging purposes
        echo "Running command: $COMMAND"
        echo ""
        
        # Execute the command
        $COMMAND
        
        echo ""
        echo "--- Finished processing $FILE_NAME for ha=$ha ---"
    done
done

echo ""
echo "================================================="
echo "All processing complete."
echo "================================================="