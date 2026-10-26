#!/bin/bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "$DIR/desensamblador/HackDisassembler.py" "$@"
