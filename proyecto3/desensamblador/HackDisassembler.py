"""Desensamblador para la plataforma Hack.

Uso:  python3 HackDisassembler.py ruta/Prog.hack
Genera ruta/ProgDis.asm, que al ensamblarse produce exactamente Prog.hack.

Etapas:
  1. read_words(): valida cada línea en orden (longitud, caracteres,
     bits 14-13 y código de cómputo) y decodifica la instrucción.
  2. find_labels(): aplica la regla 9.1 del enunciado. Si la instrucción i
     es C con salto y la i-1 es A con valor v <= n, v es un destino de salto
     y recibe una única etiqueta (L0, L1, ... en orden de dirección).
  3. disassemble(): emite el programa insertando (Lk) antes de la
     instrucción v (o al final si v = n) y escribiendo @Lk en la i-1.

Ante un error imprime en la salida estándar
    ERROR *** Línea N: <mensaje>
no genera el archivo de salida y termina con código 1.
"""

import os
import sys

# Tablas inversas de la especificación (sección 7.2 del enunciado).
COMP = {
    '0101010': '0', '0111111': '1', '0111010': '-1',
    '0001100': 'D', '0110000': 'A', '1110000': 'M',
    '0001101': '!D', '0110001': '!A', '1110001': '!M',
    '0001111': '-D', '0110011': '-A', '1110011': '-M',
    '0011111': 'D+1', '0110111': 'A+1', '1110111': 'M+1',
    '0001110': 'D-1', '0110010': 'A-1', '1110010': 'M-1',
    '0000010': 'D+A', '1000010': 'D+M',
    '0010011': 'D-A', '1010011': 'D-M',
    '0000111': 'A-D', '1000111': 'M-D',
    '0000000': 'D&A', '1000000': 'D&M',
    '0010101': 'D|A', '1010101': 'D|M',
}
DEST = {'000': '', '001': 'M', '010': 'D', '011': 'MD',
        '100': 'A', '101': 'AM', '110': 'AD', '111': 'AMD'}
JUMP = {'000': '', '001': 'JGT', '010': 'JEQ', '011': 'JGE',
        '100': 'JLT', '101': 'JNE', '110': 'JLE', '111': 'JMP'}


class HackError(Exception):
    def __init__(self, line, message):
        super().__init__(message)
        self.line = line
        self.message = message


class AInstruction:
    def __init__(self, value):
        self.value = value


class CInstruction:
    def __init__(self, dest, comp, jump):
        self.dest, self.comp, self.jump = dest, comp, jump

    def text(self):
        result = f'{self.dest}={self.comp}' if self.dest else self.comp
        return f'{result};{self.jump}' if self.jump else result


def split_lines(source):
    """Líneas del archivo con fin de línea LF o CRLF.

    Solo se quita el '\\r' final de cada línea y un único salto de línea al
    final del archivo (es opcional). Todo lo demás, incluidas líneas vacías y
    espacios, se conserva para que la validación lo detecte.
    """
    if source.startswith('\ufeff'):   # BOM de UTF-8 (Bloc de notas)
        source = source[1:]
    lines = [l[:-1] if l.endswith('\r') else l for l in source.split('\n')]
    if lines and lines[-1] == '':
        lines.pop()
    return lines


def decode(bits, line):
    """Valida una línea y la convierte en AInstruction o CInstruction."""
    if not bits:
        raise HackError(line, 'línea vacía (se esperaba una instrucción de 16 bits)')
    if len(bits) != 16:
        extra = ' (revise espacios al final)' if bits.rstrip() != bits else ''
        raise HackError(line, f'la instrucción tiene {len(bits)} caracteres; '
                              f'se esperaban exactamente 16{extra}')
    for position, char in enumerate(bits, 1):
        if char not in '01':
            raise HackError(line, f"carácter inválido {char!r} en la posición {position} "
                                  f"(solo se permiten 0 y 1)")
    if bits[0] == '0':
        return AInstruction(int(bits[1:], 2))
    if bits[1:3] != '11':
        raise HackError(line, f"instrucción C con bits 14-13 = '{bits[1:3]}' (deben ser '11')")
    comp_bits = bits[3:10]
    if comp_bits not in COMP:
        raise HackError(line, f"código de cómputo inválido a={comp_bits[0]} "
                              f"c1..c6={comp_bits[1:]}")
    return CInstruction(DEST[bits[10:13]], COMP[comp_bits], JUMP[bits[13:16]])


def read_words(source):
    """Valida todas las líneas en orden; el primer error detiene el proceso."""
    return [decode(bits, number) for number, bits in enumerate(split_lines(source), 1)]


def find_labels(words):
    """Regla 9.1. Devuelve (etiquetas por dirección, índices de @ que saltan)."""
    n = len(words)
    targets = set()         # direcciones destino (sin repetir)
    jump_sources = set()    # índices i-1 que deben escribirse como @Lk
    for i in range(1, n):
        current, previous = words[i], words[i - 1]
        if (isinstance(current, CInstruction) and current.jump
                and isinstance(previous, AInstruction) and previous.value <= n):
            targets.add(previous.value)
            jump_sources.add(i - 1)
    # Una única etiqueta por dirección, numeradas en orden de dirección
    # (L0 es el destino más bajo), así aparecen L0, L1, ... en el archivo.
    labels = {address: f'L{k}' for k, address in enumerate(sorted(targets))}
    return labels, jump_sources


def disassemble(source):
    words = read_words(source)
    labels, jump_sources = find_labels(words)
    out = []
    for index, word in enumerate(words):
        if index in labels:
            out.append(f'({labels[index]})')
        if isinstance(word, AInstruction):
            if index in jump_sources:
                out.append(f'@{labels[word.value]}')
            else:
                out.append(f'@{word.value}')
        else:
            out.append(word.text())
    if len(words) in labels:            # destino v = n: etiqueta al final
        out.append(f'({labels[len(words)]})')
    return out


def remove_if_exists(path):
    try:
        os.remove(path)
    except OSError:
        pass


def main(argv):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if len(argv) != 2:
        print('ERROR *** Uso: desensamblador.sh ruta/Prog.hack')
        return 2
    input_path = argv[1]
    base, extension = os.path.splitext(input_path)
    if extension.lower() != '.hack':
        print(f"ERROR *** El archivo de entrada debe tener extensión .hack: '{input_path}'")
        return 2
    output_path = base + 'Dis.asm'

    try:
        with open(input_path, 'rb') as file:
            source = file.read().decode('utf-8', errors='replace')
    except OSError as error:
        print(f"ERROR *** No se pudo leer el archivo '{input_path}': {error.strerror}")
        return 1

    try:
        lines = disassemble(source)
    except HackError as error:
        print(f'ERROR *** Línea {error.line}: {error.message}')
        remove_if_exists(output_path)   # nunca dejar una salida de una corrida anterior
        return 1

    with open(output_path, 'w', encoding='ascii', newline='\n') as file:
        file.write(''.join(line + '\n' for line in lines))
    print(f'{input_path} -> {output_path} ({len(lines)} líneas)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
