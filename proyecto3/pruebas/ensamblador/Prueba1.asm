// Prueba1.asm - programa sin simbolos.
// Calcula RAM[2] = RAM[0] + RAM[1].
@0
D=M
@1
D=D+M
@2
M=D
@6
0;JMP     // ciclo infinito de fin de programa
