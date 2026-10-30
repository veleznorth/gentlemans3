// Caso de error: destino repetido
// Las líneas de comentario y en blanco también cuentan.

@R0
D=M
@i
M=1      // instrucción válida

MM=0      // <- error (línea 9)
@i
M=M+1
