// Caso de error: cómputo vacío antes de ;
// Las líneas de comentario y en blanco también cuentan.

@R0
D=M
@i
M=1      // instrucción válida

;JMP      // <- error (línea 9)
@i
M=M+1
