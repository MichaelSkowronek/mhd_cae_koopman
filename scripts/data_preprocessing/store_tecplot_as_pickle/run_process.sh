#!/bin/bash

# -----------------------------------------------------------------------------
# Specific Purpose Python Runner Script (Environment Agnostic)
#
# This script runs a specific Python script with a hardcoded set of arguments.
#
# It is "environment agnostic," meaning it does NOT handle Python environment
# activation (e.g., for Conda or venv). It assumes that the correct Python
# interpreter is already available in the shell's PATH.
#
# --- PRE-REQUISITE ---
# You MUST activate your Python environment BEFORE running this script.
#
# For Conda:
#   conda activate your_env_name
#
# For venv:
#   source venv/bin/activate
#
# --- USAGE ---
# ./run_process.sh
# -----------------------------------------------------------------------------

# --- Configuration ---
# 1. Set the full path to the Python script you want to run.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/store_tecplot_as_pickle.py"


# 2. Set the hardcoded arguments for the Python script.
ARGUMENTS="--ha 300 --file_name vxyz_jxyz_p_f.dat --data_dir ../../../../../../data --verify"
# --- End of Configuration ---


# --- Script Body ---
echo "--- Initializing Runner Script ---"

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script not found at '$PYTHON_SCRIPT'"
    echo "Please update the PYTHON_SCRIPT variable in this script."
    exit 1
fi

# Check if 'python' command is available. This is a basic sanity check.
if ! command -v python &> /dev/null
then
    echo "Error: 'python' command could not be found."
    echo "Please make sure your Python environment (Conda, venv, etc.) is activated first."
    exit 1
fi

echo "Using Python interpreter at: $(command -v python)"
echo "Executing script: $PYTHON_SCRIPT"
echo "With hardcoded arguments: $ARGUMENTS"
echo "------------------------------------"

# Execute the python script with the hardcoded arguments.
# We don't quote $ARGUMENTS here to allow the shell to split it into separate arguments.
python "$PYTHON_SCRIPT" $ARGUMENTS

echo "------------------------------------"
echo "--- Script execution finished ---"
