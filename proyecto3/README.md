# Proyecto 3 – Ensamblador y desensamblador Hack

Organización de Computadores 2026-2 · Grupo **gentlemans**

Ensamblador (`.asm` → `.hack`, Proyecto 6 de Nand2Tetris) y desensamblador
(`.hack` → `Dis.asm`) para la plataforma Hack, con detección de errores.

## Integrantes

| Nombre | Usuario Git |
|---|---|
| _Nombre completo 1_ | _usuario1_ |
| _Nombre completo 2_ | _usuario2_ |
| _Nombre completo 3_ | _usuario3_ |

## Compilación y ejecución

### Lenguaje y dependencias

- **Lenguaje:** Python 3 (probado con Python 3.13; funciona con 3.7 o superior).
- **Dependencias:** ninguna fuera de la biblioteca estándar de Python. No se
  usa ningún ensamblador ni desensamblador externo.
- **Entorno:** Windows con Git Bash (también funciona en Linux y macOS).

Instalación de Python en Windows: descargar el instalador desde
<https://www.python.org/downloads/> y marcar **"Add python.exe to PATH"**.
Para comprobarlo, en Git Bash: `python --version`.

Los scripts buscan automáticamente un Python 3 que funcione probando, en orden,
`python3`, `python` y `py`. Así funcionan aunque en Windows `python3` sea el
alias vacío de la Microsoft Store.

### Comandos

Desde la carpeta `proyecto3/`:

```bash
./compilar.sh
./ensamblador.sh pruebas/ensamblador/Prog.asm
./desensamblador.sh pruebas/desensamblador/Prog.hack
```

- `compilar.sh`: Python es interpretado, así que no se compila nada. El script
  verifica que haya un Python 3 utilizable y que el código no tenga errores
  de sintaxis.
- `ensamblador.sh ruta/Prog.asm` genera `ruta/Prog.hack` (una instrucción de 16
  bits por línea, con fin de línea CRLF igual que el ensamblador oficial).
- `desensamblador.sh ruta/Prog.hack` genera `ruta/ProgDis.asm`.
- Ambos reciben un único argumento: una ruta relativa o absoluta. Funcionan con
  rutas con espacios (por ejemplo, carpetas de OneDrive).
- Si la entrada tiene errores, se imprime `ERROR *** Línea N: <mensaje>` en la
  salida estándar, no se genera el archivo de salida y el código de salida es 1.
  Si no hay errores, el código de salida es 0.

Para ejecutar todas las pruebas propias (ver `pruebas/README.md`):

```bash
./pruebas/ejecutar_pruebas.sh
```

Si Git Bash dice `Permission denied` al ejecutar un script, ejecute primero
`bash compilar.sh` (que les da permiso de ejecución) o use `bash ensamblador.sh ...`.

## Estructura del código

```
proyecto3/
├── compilar.sh             verifica Python y la sintaxis del código
├── ensamblador.sh          lanza ensamblador/HackAssembler.py
├── desensamblador.sh       lanza desensamblador/HackDisassembler.py
├── _python.sh              función común que localiza un Python 3 válido
├── ensamblador/
│   └── HackAssembler.py    tablas (Code), SymbolTable, Parser, dos pasadas
├── desensamblador/
│   └── HackDisassembler.py validación/decodificación, etiquetas (regla 9.1)
├── pruebas/                programas válidos, casos de error y su README
└── DOCUMENTACION/
    └── INFORME.md          informe técnico
```

- **`HackAssembler.py`**
  - Las tablas `COMP`, `DEST` y `JUMP` contienen solo los mnemónicos exactos del enunciado.
  - `SymbolTable` guarda los símbolos predefinidos, las etiquetas y las variables.
  - `parse_a`, `parse_label` y `parse_c` validan cada tipo de línea.
  - `assemble()` hace la primera pasada (valida todas las líneas en orden y registra las etiquetas) y la segunda (asigna las variables desde la RAM 16 y codifica).
- **`HackDisassembler.py`**
  - `decode()` valida cada línea (longitud, caracteres, bits 14–13 y cómputo) y la decodifica.
  - `find_labels()` aplica la regla 9.1 para hallar los destinos de salto.
  - `disassemble()` escribe el programa con `(Lk)` antes de cada destino y `@Lk` en las instrucciones A que preceden a un salto.

El detalle del diseño, la tabla de símbolos, el algoritmo de etiquetas, el
manejo de errores y el análisis están en
[`DOCUMENTACION/INFORME.md`](DOCUMENTACION/INFORME.md).
