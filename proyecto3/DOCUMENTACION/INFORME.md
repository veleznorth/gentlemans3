# Informe técnico – Proyecto 3: Ensamblador y desensamblador Hack

Organización de Computadores 2026-2 · Grupo **gentlemans**

## 1. Integrantes y aportes

| Integrante | Aportes |
|---|---|
| Sebastián Sánchez Gómez | Versión final del ensamblador y del desensamblador según el enunciado (validación de errores en orden de líneas, regla 9.1 de etiquetas, salida CRLF), `_python.sh`, programas de prueba propios y casos de error, `README.md` e `INFORME.md`. |
| Mathías Vélez Londoño | Primer avance del ensamblador en Python (tablas `COMP`/`DEST`/`JUMP`, análisis de instrucciones A y C, tabla de símbolos y dos pasadas) y pendientes iniciales del trabajo. |
| Cristóbal Machado Sánchez | Estructura de `proyecto3/` y primeros scripts de ejecución, primera versión del desensamblador con generación de etiquetas (reemplazada por la versión final), ajuste del formato de errores, revisión del código contra el enunciado, pruebas con el material de apoyo y publicación de la versión final en el repositorio. |

## 2. Arquitectura de la solución

La solución está escrita en Python 3, sin bibliotecas externas. Tiene dos
programas independientes, cada uno en un solo archivo, y tres scripts de Bash
que los invocan:

```
ensamblador.sh ──► ensamblador/HackAssembler.py      Prog.asm  ──► Prog.hack
desensamblador.sh ─► desensamblador/HackDisassembler.py  Prog.hack ──► ProgDis.asm
compilar.sh: verifica que exista Python 3 y que el código compile (sintaxis).
_python.sh: busca un intérprete válido (python3, python o py).
```

### 2.1 Módulos del ensamblador (`HackAssembler.py`)

Sigue la división propuesta en Nand2Tetris:

| Módulo | Responsabilidad |
|---|---|
| **Code** (`COMP`, `DEST`, `JUMP`) | Diccionarios mnemónico → bits con *solo* las entradas de la especificación (28 cómputos, 8 destinos y 8 saltos). Un mnemónico que no está en el diccionario es un error. |
| **Parser** (`clean`, `parse_a`, `parse_label`, `parse_c`) | `clean` quita el comentario (`//` hasta el final) y todos los espacios y tabulaciones. Luego, según el primer carácter (`@`, `(` u otro), la línea se analiza como instrucción A, etiqueta o instrucción C. El resultado es una tupla: `('A', valor\|símbolo)`, `('L', nombre)` o `('C', dest, comp, jump)`. |
| **SymbolTable** | Diccionario de símbolos (ver sección 3). |
| **assemble()** | Coordina las dos pasadas. |
| **main()** | Lee el archivo, maneja los errores, escribe la salida y define el código de salida. |

### 2.2 Flujo de las dos pasadas

```
             ┌──────────────────────── Primera pasada ─────────────────────────┐
Prog.asm ──► │ para cada línea N (1, 2, 3, …):                                 │
             │   texto = clean(línea)                ; vacía → se ignora        │
             │   instr = parse_line(texto, N)        ; error → AsmError(N)      │
             │   si es etiqueta: tabla.add_label(nombre, dirección_ROM, N)      │
             │   si no: programa.append((N, instr)); dirección_ROM += 1         │
             └──────────────────────────────────────────────────────────────────┘
             ┌──────────────────────── Segunda pasada ─────────────────────────┐
             │ para cada (N, instr) en programa:                                │
             │   A con número  → 0 + 15 bits                                    │
             │   A con símbolo → tabla.resolve(símbolo) (crea variable si falta)│
             │   C             → 111 + COMP[comp] + DEST[dest] + JUMP[jump]     │
             └───────────────────────────────────────────────────► Prog.hack ──┘
```

**Decisión de diseño importante.** En la versión inicial, la primera pasada
solo miraba las etiquetas y la sintaxis de las instrucciones A y C se validaba
en la segunda. Esto violaba la regla "reportar el primer error en orden de
líneas": con un `D=D*2` en la línea 4 y una etiqueta duplicada en la línea 7,
se reportaba primero la línea 7. Ahora **la primera pasada analiza y valida
todas las líneas en orden**, así que el primer error que se lanza siempre es
el de menor número de línea. La segunda pasada ya trabaja sobre instrucciones
válidas: solo resuelve los símbolos y codifica.

El resultado se escribe al final, y solo si no hubo errores, con fin de línea
CRLF, igual que los `.hack` del ensamblador oficial y del material de apoyo
(por eso las salidas son idénticas byte a byte).

### 2.3 Desensamblador (`HackDisassembler.py`)

```
Prog.hack ─► split_lines ─► decode() línea por línea ─► find_labels() ─► disassemble() ─► ProgDis.asm
             (LF/CRLF)      valida y decodifica          regla 9.1        emite texto
```

- `AInstruction(value)` y `CInstruction(dest, comp, jump)` representan las
  instrucciones decodificadas.
- Las tablas inversas `COMP`, `DEST` y `JUMP` usan los mismos mnemónicos de la
  especificación (por ejemplo `MD` y `AMD`, nunca `DM` ni `ADM`).
- La instrucción C se escribe como `dest=comp;jump`, omitiendo `dest=` y
  `;jump` cuando están vacíos.

## 3. Tabla de símbolos

**Estructura de datos:** un diccionario de Python (`dict`, tabla hash) que
asocia cada nombre con una dirección. Buscar e insertar cuesta O(1) en promedio,
así que todo el ensamblado es O(n). Pong.asm (27 483 instrucciones) se ensambla
en unos 0,1 s.

| Contenido | Cuándo se agrega | Valor |
|---|---|---|
| 23 símbolos predefinidos | Al crear la tabla (`PREDEFINED`) | `SP`…`THAT` = 0…4, `R0`…`R15` = 0…15, `SCREEN` = 16384, `KBD` = 24576 |
| Etiquetas `(X)` | Primera pasada (`add_label`) | Dirección ROM de la siguiente instrucción (el contador de instrucciones A/C vistas hasta ese momento) |
| Variables | Segunda pasada (`resolve`) | 16, 17, 18, … en el orden de primera aparición |

Además, `label_lines` guarda en qué línea se declaró cada etiqueta, para dar un
mensaje útil cuando se declara dos veces.

**Asignación de variables.** En la segunda pasada, al encontrar `@símbolo`:
si el símbolo está en la tabla (porque es predefinido o una etiqueta, aunque
la etiqueta se declare más abajo en el archivo, pues todas se registraron en la
primera pasada), se usa su valor. Si no está, es una variable nueva: se le asigna
`next_variable` (que empieza en 16) y el contador se incrementa. Por eso, en
`SintaxisCompleta.asm`, `var_1`→16, `var.2`→17, `$var3`→18 y `:var4`→19, y la
segunda aparición de `@var_1` vuelve a dar 16.

Las etiquetas se registran en la primera pasada precisamente para que un salto
hacia adelante (`@FIN` antes de `(FIN)`) no se confunda con una variable.

## 4. Generación de etiquetas en el desensamblador

### 4.1 Algoritmo (regla 9.1)

```
n ← número de instrucciones
destinos ← ∅ ; fuentes ← ∅
para i = 1 … n-1:
    si instr[i] es C con salto ≠ vacío  y  instr[i-1] es A con valor v ≤ n:
        destinos ← destinos ∪ {v}
        fuentes  ← fuentes ∪ {i-1}
etiqueta[v] ← "L" + k   para cada v de destinos en orden creciente (k = 0, 1, 2, …)

para cada dirección d = 0 … n-1:
    si d ∈ destinos: escribir "(etiqueta[d])"
    si instr[d] es A:  escribir "@etiqueta[valor]" si d ∈ fuentes, si no "@valor"
    si instr[d] es C:  escribir dest=comp;jump
si n ∈ destinos: escribir "(etiqueta[n])" al final
```

Propiedades que garantizan la condición de corrección:

- Cada destino recibe **una sola** etiqueta, porque `destinos` es un conjunto.
- La etiqueta `(Lk)` se escribe justo antes de la instrucción `v`, así que el
  ensamblador le asigna exactamente el valor `v`. Si `v = n`, se escribe al
  final y también vale `n`. Por lo tanto `@Lk` vuelve a codificarse como el
  mismo `0vvvvvvvvvvvvvvv`.
- Las etiquetas no ocupan dirección de ROM, así que no desplazan a las demás
  instrucciones.
- Los nombres `L0, L1, …` son símbolos válidos, no se repiten y no son
  predefinidos (los predefinidos son `R0…R15`, `SP`, etc.).
- La condición `v ≤ n` es necesaria: si `v > n`, no hay ningún lugar del
  archivo donde una etiqueta tome ese valor, y `@Lk` quedaría sin declarar.
  El ensamblador lo trataría como una variable (dirección 16, 17, …) y el
  binario cambiaría.
- Las demás instrucciones A se escriben en decimal aunque su valor coincida
  con un destino.

Se numeran por dirección creciente (no por orden de aparición del salto), así
L0, L1, … aparecen en orden en el archivo. Con esto, las salidas de
`Prueba3.hack` y `Prueba4.hack` son idénticas a los `…Dis_ejemplo.asm` del
material de apoyo.

### 4.2 Ejemplo (`pruebas/desensamblador/Bordes.hack`, n = 15)

| Dir. | Binario | Decodificado | ¿Regla 9.1? | Salida |
|---|---|---|---|---|
| 0 | `1110101010000111` | `0;JMP` | No hay instrucción −1 | `0;JMP` |
| 1 | `0000000000001111` | `@15` | Sí: 15 ≤ n, la sigue `0;JEQ` | `@L2` |
| 2 | `1110101010000010` | `0;JEQ` | | `0;JEQ` |
| 3 | `0000000000000011` | `@3` | Sí, la sigue `D;JGT` | `(L0)` `@L0` |
| 4 | | `D;JGT` | | `D;JGT` |
| 5 | | `@3` | Sí, la sigue `D;JLT` (mismo destino) | `@L0` |
| 6 | | `D;JLT` | | `D;JLT` |
| 7 | | `@3` | **No**: la sigue `M=D` (sin salto) | `@3` |
| 8 | | `M=D` | | `M=D` |
| 9 | | `@500` | **No**: 500 > n | `@500` |
| 10 | | `D;JNE` | | `D;JNE` |
| 11 | | `D=D-1` | | `D=D-1` |
| 12 | | `D;JMP` | **No**: la anterior es C | `D;JMP` |
| 13 | | `@14` | Sí | `@L1` |
| 14 | | `0;JMP` | | `(L1)` `0;JMP` |
| 15 = n | — | — | Destino de la dir. 1 | `(L2)` al final |

Destinos = {3, 14, 15} → L0 = 3, L1 = 14, L2 = 15. Al ensamblar el resultado
se obtiene un archivo idéntico a `Bordes.hack`.

## 5. Manejo de errores

### 5.1 Mecanismo común

- Cada programa define una excepción (`AsmError` / `HackError`) con el número
  de línea y el mensaje. Se lanza en el primer problema encontrado y se
  captura en `main()`, que imprime en la **salida estándar** exactamente
  `ERROR *** Línea N: <mensaje>`, devuelve el código de salida 1 y no escribe
  el archivo de salida.
- La salida se escribe solo después de procesar todo el archivo sin errores.
  Además, si hay un error y existe un archivo de salida de una ejecución
  anterior, se borra, para no dejar un `.hack` o `Dis.asm` que no corresponde
  a la entrada.
- La salida estándar se reconfigura a UTF-8 y los scripts exportan
  `PYTHONIOENCODING=utf-8`. Así "Línea" se imprime con tilde correctamente en
  Git Bash (por defecto, Python en Windows usaría cp1252 al escribir a una tubería).
- Errores que no tienen línea (sin argumento, archivo inexistente o extensión
  incorrecta) se reportan como `ERROR *** <mensaje>` con código distinto de 0.

### 5.2 Cálculo del número de línea

El archivo se lee en binario, se decodifica como UTF-8 (sin fallar ante bytes
inválidos) y se divide **solo por `\n`**. A cada línea se le quita el `\r`
final, lo que soporta CRLF y LF. Las líneas se numeran con `enumerate(…, 1)`
sobre esa lista completa, **antes** de descartar comentarios o líneas vacías,
por lo que N es la línea física del archivo. No se usa `str.splitlines()`
porque también corta en caracteres como `\x0b`, `\x0c` o ` `, lo que
desplazaría la numeración.

Como cada línea se valida en orden y la primera excepción detiene el proceso,
siempre se reporta el error de menor número de línea.

### 5.3 Detección por categoría – ensamblador

| Categoría | Cómo se detecta |
|---|---|
| Instrucción A | `parse_a`: valor vacío → "sin valor"; solo dígitos → `int` y se verifica ≤ 32767; empieza por dígito sin ser número (`1abc`) → error; `+`/`-` seguido de dígitos → constante inválida; si no, debe coincidir con la expresión regular de símbolo `[A-Za-z_.$:][A-Za-z0-9_.$:]*` (rechaza `VAR#1` y `LOOP)`). |
| Etiquetas | `parse_label`: debe terminar en `)`; el nombre no puede ser vacío y debe cumplir la expresión regular de símbolo. `add_label` rechaza nombres predefinidos y nombres ya declarados (informa la línea de la primera declaración). Una línea que termina en `)` sin `(` (`LOOP)`) se informa como etiqueta sin apertura. |
| Destino | Si hay `=`: la parte izquierda vacía → "destino vacío"; si no está en `DEST` (solo M, D, MD, A, AM, AD, AMD) → "destino inválido". Así se rechazan `X`, `DM`, `ADM`, `MA` y `MM`. |
| Cómputo | La parte entre `=` y `;` vacía → "cómputo vacío" (`D=`, `;JMP`); si no está en `COMP` (exactamente los 28) → "cómputo inválido" (`D*A`, `A+D`, `M+D`, `M+M`). |
| Salto | Si hay `;`: la parte derecha vacía → "salto vacío"; si no está en `JUMP` → "salto inválido" (`JXX`, `jmp`; para minúsculas se añade una pista). |
| Estructura | Más de un `=` o más de un `;`; `=` después de `;`; texto sin `=` ni `;` que no es un cómputo válido → "instrucción no reconocida" (`HOLA MUNDO`). |
| Tamaño | Más de 32 768 instrucciones o más variables que direcciones de 15 bits. |

Como los espacios se eliminan antes de analizar, `AMD = M - 1 ; JNE` es válida
y `HOLA MUNDO` se analiza como `HOLAMUNDO`.

### 5.4 Detección por categoría – desensamblador

Cada línea se revisa en este orden (`decode`):

| Categoría | Cómo se detecta |
|---|---|
| Longitud | Línea vacía → "línea vacía"; `len ≠ 16` → error con la longitud encontrada (si sobran espacios al final, el mensaje lo indica). Solo se tolera **un** salto de línea al final del archivo; cualquier otra línea vacía, en medio o al final, es error. |
| Caracteres | Cualquier carácter distinto de `0`/`1` → error con el carácter y su posición. |
| Bits 14–13 | Si el bit 15 es 1 y los bits 14–13 no son `11` → error. |
| Cómputo | Los 7 bits `a c1…c6` deben estar en la tabla inversa `COMP`; si no (p. ej. `0000001`), error. Los campos dest y jump siempre son válidos (las 8 combinaciones de 3 bits existen). |

## 6. Pruebas realizadas y resultados

El detalle de cada caso y su resultado esperado está en
[`pruebas/README.md`](../pruebas/README.md). Todo se ejecuta con
`./pruebas/ejecutar_pruebas.sh`.

| Grupo de pruebas | Casos | Resultado |
|---|---|---|
| Ensamblador – programas oficiales: Add, Max, MaxL, Rect, RectL, Pong, PongL (más Fill), comparados con los `.hack` oficiales de Nand2Tetris | 8 | 8 idénticos byte a byte |
| Ensamblador – Pong con fin de línea CRLF y en una ruta con espacios | 1 | Idéntico |
| Ensamblador – propios (Producto, SintaxisCompleta, Fibonacci) y material de apoyo (Prueba1, Prueba2) | 5 | 5 idénticos al esperado |
| Desensamblador – condición de corrección en los propios (Contador, Bordes, Tablas), el material de apoyo (Prueba3, Prueba4) y los oficiales (Add, Max, Rect, Pong, Fill, Prueba1, Prueba2) | 12 | 12 cumplen `ensamblar(ProgDis.asm) = Prog.hack`. Prueba3 y Prueba4 son además idénticos a los ejemplos del docente. Pong genera 290 etiquetas. |
| Errores del ensamblador (todas las líneas de ejemplo de la tabla 10.1, primer error y CRLF) | 32 | 32 con el formato, la línea, el código de salida y sin archivo de salida |
| Errores del desensamblador (todas las categorías de la tabla 10.2, primer error y CRLF) | 9 | 9 correctos |
| Robustez: sin argumentos, archivo inexistente, extensión incorrecta, archivo vacío, ejecución desde otra carpeta, salida previa que debe borrarse | 6 | Correcto |

**Nota sobre Rect y Pong de la 2.ª edición.** Las versiones de `Rect.asm` y
`Pong.asm` del IDE web de Nand2Tetris (2.ª edición) usan el destino `DM`. Según
la sección 7.2 del enunciado (sintaxis de la 1.ª edición), `DM` es un error, y
nuestro ensamblador lo reporta. Las versiones de la 1.ª edición usan `MD` y
producen exactamente el mismo binario.

## 7. Análisis (RA4)

### 7.1 ¿Qué información del programa original se pierde al ensamblar?

El `.hack` solo conserva lo que la CPU necesita para ejecutar: una secuencia de
palabras de 16 bits. Se pierde:

- **Comentarios, líneas en blanco, sangría y espacios**: `clean()` los elimina
  antes de traducir.
- **Nombres de etiquetas** y **dónde estaban declaradas**: `(LOOP)` no genera
  ninguna instrucción; solo deja su valor numérico dentro de las `@LOOP`.
- **Nombres de variables**: `@contador` se convierte en `@16`, y el binario no
  guarda el nombre ni el hecho de que era una variable.
- **El uso de símbolos predefinidos**: `@SCREEN`, `@KBD`, `@R5`, `@SP`, etc.
- **La forma textual de los números**: `@007` y `@7` dan el mismo binario.
- **Etiquetas redundantes**: varias etiquetas en la misma dirección (`(A)`,
  `(B)` seguidas) son indistinguibles de una sola, o de ninguna si no se usan.
- La **intención** del programador (qué valores son direcciones, contadores o
  constantes).

### 7.2 ¿Por qué el desensamblado no es único?

Porque el ensamblado es una función **muchos a uno** (no inyectiva): muchos
programas fuente distintos producen el mismo binario, así que la "inversa" no
es una función. El desensamblador debe escoger un representante entre todos
los programas equivalentes. Por ejemplo, `0000000000000000` puede escribirse
como `@0`, `@SP`, `@R0` o `@000`, o como el nombre de una variable o etiqueta
que valga 0. Los nombres de las etiquetas son arbitrarios (`L0`, `LOOP`,
`x.1`…), se pueden añadir comentarios o etiquetas sin uso, y la misma
instrucción C se puede escribir con espacios distintos. Todas esas variantes
cumplen `ensamblar(ProgDis.asm) = Prog.hack`. El enunciado fija una forma
canónica (decimal, más etiquetas solo según la regla 9.1) para que la salida
sea determinista, pero los nombres siguen siendo libres.

### 7.3 ¿Por qué el binario no distingue una variable de una constante o de un símbolo predefinido?

Una instrucción A es simplemente `0` seguido de 15 bits con un número. No hay
ningún bit que diga de dónde salió ese número: la tabla de símbolos existe solo
durante el ensamblado y se descarta. `@R1`, `@LCL` y `@1` producen
`0000000000000001`; si la primera variable del programa es `i`, `@i` produce
`0000000000010000`, igual que `@16`. Para la CPU, además, el valor solo es un
número que se carga en el registro A. Que sea una dirección de RAM (si luego se
usa `M`), una dirección de ROM (si luego hay un salto) o un dato (si luego se
hace `D=A`) depende de las instrucciones siguientes, no de la codificación. Y
puede ser varias cosas a la vez: después de `@SCREEN`, `D=A` usa una dirección
como dato. Por eso la especificación no exige recuperar nombres de variables ni
de símbolos predefinidos.

### 7.4 ¿Qué saltos no puede etiquetar la regla 9.1 y por qué?

La regla solo mira la instrucción inmediatamente anterior (`i−1`) y exige que
sea `@v` con `v ≤ n`. No etiqueta:

1. **Saltos cuyo destino se cargó antes de la instrucción `i−1`.** Por ejemplo
   `@FIN` / `D=D-1` / `D;JEQ`: entre la `@` y el salto hay una instrucción C que
   no modifica A. El destino es `FIN`, pero la regla no lo ve.
2. **Saltos indirectos o calculados**: el valor de A sale de la memoria o de una
   operación, por ejemplo `@R15` / `A=M` / `0;JMP` (el retorno de función que
   usa el código de la máquina virtual en Pong), o `A=D` / `0;JMP`. El destino
   solo se conoce al ejecutar; estáticamente no se puede saber.
3. **`@v` con `v > n`**: se sale del programa. No hay ninguna posición del
   archivo donde una etiqueta tome ese valor (una etiqueta vale como máximo n,
   si está al final). Si se escribiera `@Lk`, el ensamblador lo trataría como
   una variable y cambiaría el binario, así que debe quedar en decimal.
4. **Un salto en la dirección 0**: no hay instrucción `i−1`.
5. **Valores que son destinos de salto pero se cargan para otros usos**: por
   ejemplo, una dirección de retorno que se guarda en la pila con
   `@RET` / `D=A` / `@SP` … y luego se usa en un salto indirecto. La regla no
   lo considera salto, así que queda en decimal.

En general, saber con certeza todos los destinos de salto de un programa
requeriría analizar el flujo de datos del registro A, y en el caso indirecto
(destinos en RAM) es indecidible estáticamente. La regla 9.1 es una aproximación
simple y **segura**: nunca etiqueta algo de forma que cambie el binario, aunque
no encuentre todos los saltos.
