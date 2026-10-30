#!/bin/bash
# Python es interpretado: no hay compilación. Este script verifica que haya
# un Python 3 utilizable y que el código fuente no tenga errores de sintaxis.
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/_python.sh"
if ! find_python; then
  echo "ERROR *** No se encontró Python 3.7 o superior (python3, python o py)."
  exit 1
fi
"$PYTHON" - "$DIR/ensamblador/HackAssembler.py" "$DIR/desensamblador/HackDisassembler.py" <<'PY' || exit 1
import sys
for path in sys.argv[1:]:
    with open(path, encoding='utf-8') as f:
        compile(f.read(), path, 'exec')
PY
chmod +x "$DIR/ensamblador.sh" "$DIR/desensamblador.sh" 2>/dev/null
echo "Listo: $("$PYTHON" --version 2>&1) ($PYTHON). Lenguaje interpretado, no requiere compilación."
