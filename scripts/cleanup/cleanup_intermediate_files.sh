#!/bin/bash

# ==============================================================================
# WARNING: This script PERMANENTLY DELETES files. Review carefully.
#
# This script cleans up intermediate data files that are no longer needed
# after the final .npz datasets have been created and verified. It targets
# raw .dat, .zip, and intermediate .pkl files across all specified
# Hartmann numbers.
# ==============================================================================

# --- Configuration ---
# Exit immediately if a command exits with a non-zero status.
set -e

# --- User Configuration ---
# IMPORTANT: Set this variable to the absolute path of your top-level data directory.
# This is the only line you should need to edit.
DATA_DIR="/home/skowronek/Documents/PhD/nuclear_fusion_cooling/data"

# --- Script Configuration ---
# Get the absolute path of the directory where this script is located.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# --- Sanity Checks ---
if [ "$DATA_DIR" == "/path/to/your/data_directory" ]; then
    echo "Error: Please edit this script and set the DATA_DIR variable to the correct path." >&2
    exit 1
fi

if [ ! -d "$DATA_DIR" ]; then
    echo "Error: The specified data directory does not exist: $DATA_DIR" >&2
    exit 1
fi


# The Hartmann numbers to process.
HA_NUMBERS=(300 500 700 1000)

# List of file paths to delete, relative to the ".../re1000_ha<XXX>/3d/" directory.
FILES_TO_DELETE=(
    "du.dat"
    "dv.dat"
    "dw.dat"
    "du.zip"
    "dv.zip"
    "dw.zip"
    "vxyz_jxyz_p_f.dat"
    "vxyz_jxyz_p_f.zip"
    "pkl/du.pkl"
    "pkl/dv.pkl"
    "pkl/dw.pkl"
    "pkl/vxyz_jxyz_p_f.pkl"
)

# --- Safety Confirmation Prompt ---
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "!!! DANGER: This script will PERMANENTLY DELETE files.       !!!"
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "This script will attempt to delete the following file patterns:"
for pattern in "${FILES_TO_DELETE[@]}"; do
    echo "  - .../re1000_ha<XXX>/3d/${pattern}"
done
echo ""
echo "From the base directory: ${DATA_DIR}"
echo "For Hartmann numbers: ${HA_NUMBERS[*]}"
echo ""
read -p "Are you absolutely sure you want to proceed? Type 'yes' to continue: " CONFIRMATION

if [ "$CONFIRMATION" != "yes" ]; then
    echo "Aborting cleanup. No files were deleted."
    exit 1
fi

echo ""
echo "Confirmation received. Starting cleanup..."

# --- Main Processing Loop ---
for ha in "${HA_NUMBERS[@]}"; do
    HA_DIR="${DATA_DIR}/re1000_ha${ha}/3d"
    echo ""
    echo "--- Processing for ha=$ha in directory: $HA_DIR ---"

    for file_rel_path in "${FILES_TO_DELETE[@]}"; do
        FILE_TO_DELETE="${HA_DIR}/${file_rel_path}"

        if [ -f "$FILE_TO_DELETE" ]; then
            echo "Deleting: ${FILE_TO_DELETE}"
            rm -f "$FILE_TO_DELETE" # Use -f to avoid errors if file is missing
        else
            echo "Skipping (not found): ${FILE_TO_DELETE}"
        fi
    done
done

echo ""
echo "================================================="
echo "Cleanup script has finished."
echo "================================================="