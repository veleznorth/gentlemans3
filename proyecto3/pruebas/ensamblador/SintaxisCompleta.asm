// SintaxisCompleta.asm - prueba propia (grupo). Archivo con fin de línea CRLF.
// Usa los 28 cómputos, los 8 destinos, los 8 saltos, todos los símbolos
// predefinidos, símbolos con _ . $ :, varias etiquetas en la misma dirección
// y una etiqueta al final del programa. No está pensado para ejecutarse.

// --- 28 cómputos (destino D) ---
D=0
D=1
D=-1
D=D
D=A
D=!D
D=!A
D=-D
D=-A
D=D+1
D=A+1
D=D-1
D=A-1
D=D+A
D=D-A
D=A-D
D=D&A
D=D|A
D=M
D=!M
D=-M
D=M+1
D=M-1
D=D+M
D=D-M
D=M-D
D=D&M
D=D|M
// --- 8 destinos ---
0
M=1
D=1
MD=1
A=1
AM=1
AD=1
AMD = M - 1 ; JNE      // ejemplo del enunciado: espacios en todas partes
// --- 8 saltos ---
@INICIO
D
@INICIO
D;JGT
@INICIO
D;JEQ
@INICIO
D;JGE
@INICIO
D;JLT
@INICIO
D;JNE
@INICIO
D;JLE
@FINAL
0;JMP
// --- símbolos predefinidos ---
@SP
@LCL
@ARG
@THIS
@THAT
@R0
@R1
@R2
@R3
@R4
@R5
@R6
@R7
@R8
@R9
@R10
@R11
@R12
@R13
@R14
@R15
@SCREEN
@KBD
// --- etiquetas múltiples y variables con caracteres especiales ---
(INICIO)
(otro.nombre)
(con$signo:y_guion)
@var_1
@var.2
@$var3
@:var4
@var_1          // ya existe: misma dirección (16)
@otro.nombre
@con$signo:y_guion
@32767
@0
@00016          // ceros a la izquierda: 16
(FINAL)
