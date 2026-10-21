#!/usr/bin/env bash
set -euo pipefail
cd /workspace/mymcp-4-codexcloud
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
python3 plugin/lody4dot/scripts/bootstrap.py --prefix /workspace/.tools/lody4dot --prepare --json
# Dependencies only: do not authenticate, register machines or start daemons here.
