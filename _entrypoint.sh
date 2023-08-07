#!/usr/bin/env bash

set -ef -o pipefail
<<<<<<< HEAD

# source /venv/bin/activate
=======
#source /venv/bin/activate
python -c 'import torch; print("Hello World")'
>>>>>>> fc75bde83c5dfceef6ed5360a50ec8c5294380d2

exec "$@"
