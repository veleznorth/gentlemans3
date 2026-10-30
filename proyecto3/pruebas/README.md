# Pruebas del proyecto 3

Todas las pruebas se ejecutan de una vez desde `proyecto3/` con:

```bash
./pruebas/ejecutar_pruebas.sh
```

El script ejecuta cada caso, compara el resultado con lo esperado, verifica el
código de salida y que **no** se genere archivo de salida en los casos de error,
y al final borra los archivos generados. Resultado actual: **51 correctas, 0
fallidas**.

## Estructura

```
pruebas/
├── ensamblador/            programas .asm válidos
│   └── esperado/           .hack esperado de cada uno
├── desensamblador/         programas .hack válidos
│   └── esperado/           una salida ProgDis.asm correcta de cada uno
├── errores/                casos de error (ens_*.asm y des_*.hack)
│   └── esperados.txt       archivo|línea esperada (lo usa el script)
└── ejecutar_pruebas.sh
```

## 1. Ensamblador: programas válidos

Comando: `./ensamblador.sh pruebas/ensamblador/Prog.asm`.
Resultado esperado: se crea `pruebas/ensamblador/Prog.hack`, idéntico byte a
byte a `pruebas/ensamblador/esperado/Prog.hack`, y el código de salida es 0.

| Programa | Origen | Qué prueba | Salida esperada |
|---|---|---|---|
| `Producto.asm` | Propio | R2 = R0 × R1 por sumas sucesivas. Variables, etiquetas usadas antes de declararse, espacios y tabulaciones dentro de las instrucciones (`M = D + M`, `D ; JEQ`), comentarios al final de la línea. | `esperado/Producto.hack` (20 instrucciones) |
| `SintaxisCompleta.asm` | Propio | Los 28 cómputos, los 8 destinos, los 8 saltos y los 23 símbolos predefinidos; símbolos con `_ . $ :`; tres etiquetas en la misma dirección; etiqueta al final del programa; `@00016` con ceros a la izquierda; `@32767`; `AMD = M - 1 ; JNE`. **Fin de línea CRLF.** | `esperado/SintaxisCompleta.hack` (85 instrucciones; variables `var_1`=16, `var.2`=17, `$var3`=18, `:var4`=19) |
| `Fibonacci.asm` | Propio | Escribe los R0 primeros términos de Fibonacci desde RAM[100]. Punteros (`A=M`), 5 variables, saltos `JLE` y `JMP`. | `esperado/Fibonacci.hack` (43 instrucciones) |
| `Prueba1.asm` | Material de apoyo | Programa sin símbolos. | `esperado/Prueba1.hack` |
| `Prueba2.asm` | Material de apoyo | Etiquetas y variables. | `esperado/Prueba2.hack` |

Además, durante el desarrollo se verificó que el ensamblador produce archivos
idénticos a los del ensamblador oficial para Add, Max, MaxL, Rect, RectL,
Pong y PongL (Pong tiene 27 483 instrucciones y se ensambla en ~0,1 s). Estos
programas oficiales no se incluyen en la carpeta, como pide el enunciado.

## 2. Desensamblador: programas válidos

Comando: `./desensamblador.sh pruebas/desensamblador/Prog.hack`.
Resultado esperado: se crea `pruebas/desensamblador/ProgDis.asm`, código de
salida 0, y **al ensamblar `ProgDis.asm` se obtiene un archivo idéntico a
`Prog.hack`** (condición de corrección). En `esperado/` está la salida que
produce nuestra solución.

| Programa | Origen | Qué prueba | Salida esperada |
|---|---|---|---|
| `Contador.hack` | Propio | Cuenta regresiva desde R0. Dos saltos condicionales hacia atrás y uno incondicional. **CRLF.** | `esperado/ContadorDis.asm` (etiquetas L0, L1, L2) |
| `Bordes.hack` | Propio | Casos límite de la regla 9.1: salto en la dirección 0 (no tiene instrucción anterior); `@15` con n = 15 → la etiqueta se declara **al final del archivo**; tres saltos al mismo destino → **una sola etiqueta**; `@3` seguido de `M=D` (sin salto) → se queda en decimal aunque 3 sea destino; `@500` (v > n) seguido de salto → no se etiqueta; salto precedido de una instrucción C. **Sin salto de línea final.** | `esperado/BordesDis.asm` |
| `Tablas.hack` | Propio | Los 28 cómputos, los 8 destinos y los 8 saltos en el desensamblado (por ejemplo `MD=!M`, `AMD=D+M`). | `esperado/TablasDis.asm` |
| `Prueba3.hack` | Material de apoyo | R2 = max(R0, R1). | `esperado/Prueba3Dis.asm` (idéntico a `Prueba3Dis_ejemplo.asm`) |
| `Prueba4.hack` | Material de apoyo | Pinta R0 palabras de la pantalla. | `esperado/Prueba4Dis.asm` (idéntico a `Prueba4Dis_ejemplo.asm`) |

## 3. Casos de error

En todos los casos el resultado esperado es: se imprime en la salida estándar
exactamente la línea indicada, el código de salida es 1 y **no** se crea el
archivo de salida (`Prog.hack` o `ProgDis.asm`).

Los archivos `ens_*.asm` tienen comentarios, líneas en blanco e instrucciones
válidas antes de la línea con error, para comprobar que el número de línea
cuenta todas las líneas del archivo. Hay un caso por cada ejemplo de la tabla
10.1 y 10.2 del enunciado, más casos de "primer error" (hay dos errores y solo
debe reportarse el de menor línea) y de errores en archivos CRLF.

### Errores del ensamblador

| Archivo | Categoría | Línea inválida | Salida esperada (stdout) |
|---|---|---|---|
| `ens_A_sin_valor.asm` | Instrucción A | `@` | `ERROR *** Línea 9: instrucción A sin valor '@'` |
| `ens_A_fuera_de_rango.asm` | Instrucción A | `@32768` | `ERROR *** Línea 9: constante fuera de rango '@32768' (debe estar entre 0 y 32767)` |
| `ens_A_negativa.asm` | Instrucción A | `@-1` | `ERROR *** Línea 9: constante inválida '@-1' (solo se permiten valores entre 0 y 32767)` |
| `ens_A_empieza_digito.asm` | Instrucción A | `@1abc` | `ERROR *** Línea 9: símbolo inválido '1abc' (no puede empezar por un dígito)` |
| `ens_A_caracter_invalido.asm` | Instrucción A | `@VAR#1` | `ERROR *** Línea 9: símbolo inválido 'VAR#1' en instrucción A` |
| `ens_A_parentesis.asm` | Instrucción A | `@LOOP)` | `ERROR *** Línea 9: símbolo inválido 'LOOP)' en instrucción A` |
| `ens_etiqueta_sin_cierre.asm` | Etiquetas | `(LOOP` | `ERROR *** Línea 9: etiqueta sin paréntesis de cierre '(LOOP'` |
| `ens_etiqueta_sin_apertura.asm` | Etiquetas | `LOOP)` | `ERROR *** Línea 9: etiqueta sin paréntesis de apertura 'LOOP)'` |
| `ens_etiqueta_vacia.asm` | Etiquetas | `()` | `ERROR *** Línea 9: etiqueta vacía '()'` |
| `ens_etiqueta_nombre_invalido.asm` | Etiquetas | `(1LOOP)` | `ERROR *** Línea 9: nombre de etiqueta inválido '1LOOP'` |
| `ens_etiqueta_predefinida.asm` | Etiquetas | `(SCREEN)` | `ERROR *** Línea 9: la etiqueta 'SCREEN' usa el nombre de un símbolo predefinido` |
| `ens_destino_X.asm` | Destino | `X=D` | `ERROR *** Línea 9: destino inválido 'X'` |
| `ens_destino_DM.asm` | Destino | `DM=D+1` | `ERROR *** Línea 9: destino inválido 'DM'` |
| `ens_destino_ADM.asm` | Destino | `ADM=M` | `ERROR *** Línea 9: destino inválido 'ADM'` |
| `ens_destino_MA.asm` | Destino | `MA=1` | `ERROR *** Línea 9: destino inválido 'MA'` |
| `ens_destino_MM.asm` | Destino | `MM=0` | `ERROR *** Línea 9: destino inválido 'MM'` |
| `ens_destino_vacio.asm` | Destino | `=D` | `ERROR *** Línea 9: destino vacío antes de '='` |
| `ens_computo_vacio_dest.asm` | Cómputo | `D=` | `ERROR *** Línea 9: cómputo vacío` |
| `ens_computo_vacio_salto.asm` | Cómputo | `;JMP` | `ERROR *** Línea 9: cómputo vacío` |
| `ens_computo_multiplicacion.asm` | Cómputo | `D=D*A` | `ERROR *** Línea 9: cómputo inválido 'D*A'` |
| `ens_computo_A_mas_D.asm` | Cómputo | `D=A+D` | `ERROR *** Línea 9: cómputo inválido 'A+D'` |
| `ens_computo_M_mas_D.asm` | Cómputo | `M=M+D` | `ERROR *** Línea 9: cómputo inválido 'M+D'` |
| `ens_computo_M_mas_M.asm` | Cómputo | `D=M+M` | `ERROR *** Línea 9: cómputo inválido 'M+M'` |
| `ens_salto_vacio.asm` | Salto | `D;` | `ERROR *** Línea 9: salto vacío después de ';'` |
| `ens_salto_inexistente.asm` | Salto | `D;JXX` | `ERROR *** Línea 9: salto inválido 'JXX'` |
| `ens_salto_minusculas.asm` | Salto | `0;jmp` | `ERROR *** Línea 9: salto inválido 'jmp' (los mnemónicos distinguen mayúsculas)` |
| `ens_estructura_dos_iguales.asm` | Estructura | `D=M=A` | `ERROR *** Línea 9: instrucción C con más de un '=': 'D=M=A'` |
| `ens_estructura_dos_puntoycoma.asm` | Estructura | `D;JGT;JMP` | `ERROR *** Línea 9: instrucción C con más de un ';': 'D;JGT;JMP'` |
| `ens_estructura_texto.asm` | Estructura | `HOLA MUNDO` | `ERROR *** Línea 9: instrucción no reconocida 'HOLAMUNDO'` |
| `ens_etiqueta_duplicada.asm` | Etiquetas | `(LOOP)` | `ERROR *** Línea 8: la etiqueta 'LOOP' ya fue declarada en la línea 2` |
| `ens_primer_error.asm` | Primer error | `D=D*2` | `ERROR *** Línea 4: cómputo inválido 'D*2'` |
| `ens_crlf.asm` | CRLF | `D=D+Q` | `ERROR *** Línea 6: cómputo inválido 'D+Q'` |

### Errores del desensamblador

| Archivo | Categoría | Línea inválida | Salida esperada (stdout) |
|---|---|---|---|
| `des_longitud_corta.hack` | Longitud | `'000000000000001'` | `ERROR *** Línea 5: la instrucción tiene 15 caracteres; se esperaban exactamente 16` |
| `des_longitud_larga.hack` | Longitud | `'00000000000000010'` | `ERROR *** Línea 5: la instrucción tiene 17 caracteres; se esperaban exactamente 16` |
| `des_espacio_final.hack` | Longitud | `'0000000000000010 '` | `ERROR *** Línea 5: la instrucción tiene 17 caracteres; se esperaban exactamente 16 (revise espacios al final)` |
| `des_linea_vacia.hack` | Longitud | `''` | `ERROR *** Línea 5: línea vacía (se esperaba una instrucción de 16 bits)` |
| `des_caracter_invalido.hack` | Caracteres | `'0000000000000201'` | `ERROR *** Línea 5: carácter inválido '2' en la posición 14 (solo se permiten 0 y 1)` |
| `des_bits_14_13.hack` | Bits 14–13 | `'1010110000010000'` | `ERROR *** Línea 5: instrucción C con bits 14-13 = '01' (deben ser '11')` |
| `des_computo_invalido.hack` | Cómputo | `'1110000001010000'` | `ERROR *** Línea 5: código de cómputo inválido a=0 c1..c6=000001` |
| `des_primer_error.hack` | Primer error | `'1110000001010000'` | `ERROR *** Línea 2: código de cómputo inválido a=0 c1..c6=000001` |
| `des_crlf_caracter.hack` | CRLF | `'000000000000000x'` | `ERROR *** Línea 3: carácter inválido 'x' en la posición 16 (solo se permiten 0 y 1)` |
