#!/bin/sh
cd "$(dirname "$0")"
python -m zprompt.expand "$@"
#echo '{"point": 1, "delete": 0, "text": "hello"}'
