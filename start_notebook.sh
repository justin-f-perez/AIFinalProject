#!/bin/sh

# This is just a shortcut to start the notebook server.
# It starts it up in the correct document directory, and assumes your conda
# environment is named 'ai-final'.

set -eu

notebook_dir="$(cd "$(dirname "$0")" && pwd)"/docs
conda run --no-capture-output --name=ai-final jupyter lab --notebook-dir="${notebook_dir}"
