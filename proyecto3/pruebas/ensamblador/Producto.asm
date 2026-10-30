// Producto.asm - prueba propia (grupo).
// Calcula R2 = R0 * R1 mediante sumas sucesivas (R0, R1 >= 0).
// Prueba: variables, etiquetas usadas antes de declararse, comentarios al
// final de línea, espacios dentro de las instrucciones y tabulaciones.

	@R2
	M = 0              // R2 = 0
	@R1
	D = M
	@contador
	M = D              // contador = R1
(CICLO)
	@contador
	D = M
	@FIN
	D ; JEQ            // si contador == 0 terminar
	@R0
	D = M
	@R2
	M = D + M          // R2 = R2 + R0
	@contador
	M = M - 1          // contador--
	@CICLO
	0 ; JMP
(FIN)
	@FIN
	0;JMP
