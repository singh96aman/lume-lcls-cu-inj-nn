#!/usr/bin/env bash

set -ef -o pipefail
#source /venv/bin/activate
python -c 'import torch; print("Hello World")'

exec "$@"
