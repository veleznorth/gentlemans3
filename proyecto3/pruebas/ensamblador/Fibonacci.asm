// Fibonacci.asm - prueba propia (grupo).
// Escribe en RAM[100], RAM[101], ... los primeros R0 términos de Fibonacci.
// Prueba: punteros, variables declaradas en distinto orden, saltos JLE/JGT.

    @100
    D=A
    @ptr
    M=D            // ptr = 100
    @a
    M=0            // a = 0
    @b
    M=1            // b = 1
    @R0
    D=M
    @n
    M=D            // n = R0
(LOOP)
    @n
    D=M
    @END
    D;JLE          // si n <= 0 terminar
    @a
    D=M
    @ptr
    A=M
    M=D            // RAM[ptr] = a
    @ptr
    M=M+1
    @a
    D=M
    @b
    D=D+M          // D = a + b
    @tmp
    M=D
    @b
    D=M
    @a
    M=D            // a = b
    @tmp
    D=M
    @b
    M=D            // b = tmp
    @n
    M=M-1
    @LOOP
    0;JMP
(END)
    @END
    0;JMP
