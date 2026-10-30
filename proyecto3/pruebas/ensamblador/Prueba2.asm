// Prueba2.asm - programa con etiquetas y variables.
// Calcula R1 = 1 + 2 + ... + R0 (si R0 <= 0, R1 = 0).
    @i
    M=1          // i = 1
    @suma
    M=0          // suma = 0
(CICLO)
    @i
    D=M
    @R0
    D=D-M
    @GUARDAR
    D;JGT        // si i > R0, terminar
    @i
    D=M
    @suma
    M=D+M        // suma = suma + i
    @i
    M=M+1        // i = i + 1
    @CICLO
    0;JMP
(GUARDAR)
    @suma
    D=M
    @R1
    M=D
(FIN)
    @FIN
    0;JMP
