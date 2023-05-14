#!/bin/sh
cd "$(dirname "$0")"
python3 -m zprompt.expand "$@"
#echo '{"point": 1, "delete": 0, "text": "hello"}'
