#!/usr/bin/env bash
set -euo pipefail
cd /workspace/mymcp-4-codexcloud
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
python3 plugin/lody4dot/scripts/install.py --prefix /workspace/.tools/lody4dot --json
python3 plugin/lody4dot/scripts/doctor.py --prefix /workspace/.tools/lody4dot --profile inspect --json
# Dependencies only: do not authenticate, register machines or start daemons here.
