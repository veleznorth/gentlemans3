// Caso de error: constante mayor que 32767
// Las líneas de comentario y en blanco también cuentan.

@R0
D=M
@i
M=1      // instrucción válida

@32768      // <- error (línea 9)
@i
M=M+1
