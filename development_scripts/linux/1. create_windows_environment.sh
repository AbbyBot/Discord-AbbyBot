#!/bin/bash

# Set script path
script_path="$(dirname "$(realpath "$0")")/../../"

python3 -m venv "${script_path}venv"

source "${script_path}venv/bin/activate"

pip install -r "${script_path}/discord_abbybot/requirements.txt"

deactivate

echo "Environment and requirements successfully installed!"
