// Caso de error: cómputo no incluido en la tabla
// Las líneas de comentario y en blanco también cuentan.

@R0
D=M
@i
M=1      // instrucción válida

D=M+M      // <- error (línea 9)
@i
M=M+1
