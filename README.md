# Trabajo 3 - Organización de Computadores

Avance del ensamblador y desensamblador para la arquitectura Hack.
Implementado en Python 3, sin dependencias externas.

## Uso

```bash
python3 HackAssembler.py Prog.asm
```

Genera `Prog.hack` en la misma carpeta del archivo de entrada.
Para elegir otra salida:

```bash
python3 HackAssembler.py Prog.asm -o salida.hack
```

Si la salida ya existe, se puede reemplazar con `--force`.

## Avance

El ensamblador traduce instrucciones A y C, ignora comentarios y líneas
vacías, y resuelve etiquetas y variables con dos pasadas. Incluye los
símbolos predefinidos de Hack.

## Pendientes

- Implementar el desensamblador de `.hack` a `.asm`.
- Probar con Add, Max, Rect y Pong y verificar los resultados con las
  herramientas de Nand2Tetris.
- Documentar las pruebas y agregar las evidencias de ejecución.

Este trabajo funciona de forma independiente de los proyectos anteriores
en HDL del repositorio gentlemans.
