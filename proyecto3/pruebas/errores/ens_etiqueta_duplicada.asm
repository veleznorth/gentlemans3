// Caso de error: etiqueta declarada dos veces.
(LOOP)
@LOOP
0;JMP

(FIN)
@FIN
(LOOP)          // <- error (línea 8): LOOP ya se declaró en la línea 2
0;JMP
