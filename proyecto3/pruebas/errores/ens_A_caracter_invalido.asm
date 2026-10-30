// Caso de error: carácter # en símbolo
// Las líneas de comentario y en blanco también cuentan.

@R0
D=M
@i
M=1      // instrucción válida

@VAR#1      // <- error (línea 9)
@i
M=M+1
