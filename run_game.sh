#!/bin/bash

# Block Blast Game Launcher
# This script activates the virtual environment and runs the game

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the project directory
cd "$DIR"

# Activate virtual environment
source venv/bin/activate

# Run the modular game
python main_modular.py