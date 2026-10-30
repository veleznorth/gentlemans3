// Caso de error: constante negativa
// Las líneas de comentario y en blanco también cuentan.

@R0
D=M
@i
M=1      // instrucción válida

@-1      // <- error (línea 9)
@i
M=M+1
