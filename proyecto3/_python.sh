#!/bin/bash
# Busca un intérprete de Python 3 que funcione realmente.
# En Windows, "python3" puede ser el alias de la Microsoft Store (no ejecuta
# nada), por eso se prueba cada candidato antes de usarlo.
find_python() {
  local cand
  for cand in python3 python py; do
    if command -v "$cand" >/dev/null 2>&1 &&
       "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)' >/dev/null 2>&1; then
      PYTHON="$cand"
      return 0
    fi
  done
  return 1
}
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1
export PYTHONDONTWRITEBYTECODE=1
