#!/bin/bash
# Ejecuta todas las pruebas del proyecto. Uso (desde proyecto3/):
#   ./pruebas/ejecutar_pruebas.sh
# Al final borra los archivos generados para dejar la carpeta limpia.
cd "$(dirname "$0")/.." || exit 1
pass=0; fail=0
check() {
  if [ "$1" = ok ]; then pass=$((pass + 1)); echo "  OK     $2"
  else fail=$((fail + 1)); echo "  FALLA  $2"; fi
}
# Compara dos archivos ignorando CRLF/LF y el salto de línea final.
same_lines() {
  diff -q <(awk '{sub(/\r$/, ""); print}' "$1") <(awk '{sub(/\r$/, ""); print}' "$2") >/dev/null
}

echo "== Ensamblador: programas válidos (salida idéntica a esperado/)"
for asm in pruebas/ensamblador/*.asm; do
  name=$(basename "$asm" .asm)
  r=x
  ./ensamblador.sh "$asm" >/dev/null &&
    cmp -s "pruebas/ensamblador/$name.hack" "pruebas/ensamblador/esperado/$name.hack" && r=ok
  check $r "$name.asm"
done

echo "== Desensamblador: condición de corrección ensamblar(ProgDis.asm) = Prog.hack"
for hack in pruebas/desensamblador/*.hack; do
  name=$(basename "$hack" .hack)
  case "$name" in *Dis) continue ;; esac
  r=x
  ./desensamblador.sh "$hack" >/dev/null &&
    ./ensamblador.sh "pruebas/desensamblador/${name}Dis.asm" >/dev/null &&
    same_lines "pruebas/desensamblador/${name}Dis.hack" "$hack" && r=ok
  check $r "$name.hack"
done

echo "== Casos de error (mensaje, número de línea, código de salida y sin archivo de salida)"
while IFS='|' read -r file line; do
  case "$file" in ''|\#*) continue ;; esac
  path="pruebas/errores/$file"
  if [[ "$file" == *.asm ]]; then
    out=$(./ensamblador.sh "$path"); rc=$?; gen="${path%.asm}.hack"
  else
    out=$(./desensamblador.sh "$path"); rc=$?; gen="${path%.hack}Dis.asm"
  fi
  r=ok
  [[ "$out" == "ERROR *** Línea $line: "* ]] || r=x
  [ "$rc" -ne 0 ] || r=x
  [ -e "$gen" ] && r=x
  check $r "$file -> $out"
done < pruebas/errores/esperados.txt

# Limpieza de archivos generados
rm -f pruebas/ensamblador/*.hack pruebas/desensamblador/*Dis.asm pruebas/desensamblador/*Dis.hack

echo
echo "Resultado: $pass correctas, $fail fallidas"
[ "$fail" -eq 0 ]
