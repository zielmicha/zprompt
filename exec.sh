#!/bin/sh
cd "$(dirname "$0")"
python -m zprompt.execute "$@"
