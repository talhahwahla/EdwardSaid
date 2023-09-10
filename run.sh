#!/bin/bash

cd "<project_root>"

source venv/bin/activate

python3 every_other.py >> logfile.log 2>&1

deactivate
