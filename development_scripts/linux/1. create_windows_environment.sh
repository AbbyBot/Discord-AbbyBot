#!/bin/bash

# Set script path
script_path="$(dirname "$(realpath "$0")")/../../"

# Create new environment called "venv"
python3 -m venv "${script_path}venv"

# Activate virtual environment
source "${script_path}venv/bin/activate"

# Install requirements.txt
pip install -r "${script_path}requirements.txt"

# Deactivate environment
deactivate

echo "Environment and requirements successfully installed!"
