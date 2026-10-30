// Caso de error: hay dos errores; debe reportarse solo el primero (línea 4)
// aunque la etiqueta duplicada (línea 7) se detecte en la "primera pasada".
(A1)
D=D*2           // <- primer error (línea 4)
@A1
0;JMP
(A1)            // segundo error, no debe reportarse
