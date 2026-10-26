#!/bin/bash
set -e
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR *** python3 no esta instalado o no esta en el PATH." >&2
  exit 1
fi
DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$DIR/ensamblador.sh" "$DIR/desensamblador.sh"
echo "Listo. python3 detectado (lenguaje interpretado, no requiere compilacion)."
