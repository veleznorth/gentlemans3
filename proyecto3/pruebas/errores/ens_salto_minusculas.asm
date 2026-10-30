// Caso de error: salto en minúsculas
// Las líneas de comentario y en blanco también cuentan.

@R0
D=M
@i
M=1      // instrucción válida

0;jmp      // <- error (línea 9)
@i
M=M+1
