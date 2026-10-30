#!/bin/bash
# Uso: ./desensamblador.sh ruta/Prog.hack   ->  genera ruta/ProgDis.asm
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/_python.sh"
if ! find_python; then
  echo "ERROR *** No se encontró Python 3.7 o superior (python3, python o py)."
  exit 1
fi
exec "$PYTHON" "$DIR/desensamblador/HackDisassembler.py" "$@"
