// Caso de error: dos ;
// Las líneas de comentario y en blanco también cuentan.

@R0
D=M
@i
M=1      // instrucción válida

D;JGT;JMP      // <- error (línea 9)
@i
M=M+1
