#!/bin/bash

# Build sub-packages
echo "Building sub-packages..."
./build_subpackages.sh

# Build the main application
echo "Installing main application dependencies..."
pip install -r schema-conversion-orchestrator/requirements.txt