// Caso de error: paréntesis en símbolo
// Las líneas de comentario y en blanco también cuentan.

@R0
D=M
@i
M=1      // instrucción válida

@LOOP)      // <- error (línea 9)
@i
M=M+1
