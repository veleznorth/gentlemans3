// Caso de error: símbolo que empieza por dígito
// Las líneas de comentario y en blanco también cuentan.

@R0
D=M
@i
M=1      // instrucción válida

@1abc      // <- error (línea 9)
@i
M=M+1
