#!/bin/bash
# Uso: ./ensamblador.sh ruta/Prog.asm   ->  genera ruta/Prog.hack
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/_python.sh"
if ! find_python; then
  echo "ERROR *** No se encontró Python 3.7 o superior (python3, python o py)."
  exit 1
fi
exec "$PYTHON" "$DIR/ensamblador/HackAssembler.py" "$@"
