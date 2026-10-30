"""Ensamblador para la plataforma Hack (Proyecto 6 de Nand2Tetris).

Uso:  python3 HackAssembler.py ruta/Prog.asm
Genera ruta/Prog.hack (una instrucción de 16 bits por línea).

Estructura (módulos clásicos de Nand2Tetris):
  - Code        : tablas comp / dest / jump y codificación a bits.
  - SymbolTable : símbolos predefinidos, etiquetas y variables.
  - Parser      : limpieza de líneas y análisis sintáctico de cada instrucción.
  - assemble()  : primera pasada (validación + etiquetas) y segunda pasada
                  (variables + generación de código).

Ante un error imprime en la salida estándar
    ERROR *** Línea N: <mensaje>
no genera el archivo de salida y termina con código 1.
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# Code: tablas de la especificación (sección 7.2 del enunciado)
# ---------------------------------------------------------------------------

# comp -> bits "a c1 c2 c3 c4 c5 c6" (28 mnemónicos exactos)
COMP = {
    '0': '0101010', '1': '0111111', '-1': '0111010',
    'D': '0001100', 'A': '0110000', 'M': '1110000',
    '!D': '0001101', '!A': '0110001', '!M': '1110001',
    '-D': '0001111', '-A': '0110011', '-M': '1110011',
    'D+1': '0011111', 'A+1': '0110111', 'M+1': '1110111',
    'D-1': '0001110', 'A-1': '0110010', 'M-1': '1110010',
    'D+A': '0000010', 'D+M': '1000010',
    'D-A': '0010011', 'D-M': '1010011',
    'A-D': '0000111', 'M-D': '1000111',
    'D&A': '0000000', 'D&M': '1000000',
    'D|A': '0010101', 'D|M': '1010101',
}

# Solo los 7 destinos de la tabla (más el vacío). DM, ADM, MA... son errores.
DEST = {'': '000', 'M': '001', 'D': '010', 'MD': '011',
        'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'}

JUMP = {'': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
        'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}

MAX_VALUE = 32767        # mayor constante representable en 15 bits
ROM_SIZE = 32768         # número máximo de instrucciones (ROM32K)
FIRST_VARIABLE = 16      # primera dirección RAM para variables

# Símbolo: letras, dígitos, _ . $ : y no empieza por dígito.
SYMBOL_RE = re.compile(r'[A-Za-z_.$:][A-Za-z0-9_.$:]*\Z')
DECIMAL_RE = re.compile(r'[0-9]+\Z')


class AsmError(Exception):
    """Error en el programa fuente, asociado a un número de línea."""

    def __init__(self, line, message):
        super().__init__(message)
        self.line = line
        self.message = message


# ---------------------------------------------------------------------------
# SymbolTable
# ---------------------------------------------------------------------------

class SymbolTable:
    """Diccionario nombre -> dirección.

    Se inicializa con los 23 símbolos predefinidos. Las etiquetas se agregan
    en la primera pasada (dirección ROM) y las variables en la segunda
    (dirección RAM a partir de 16, en orden de primera aparición).
    """

    PREDEFINED = dict({f'R{i}': i for i in range(16)},
                      SP=0, LCL=1, ARG=2, THIS=3, THAT=4,
                      SCREEN=16384, KBD=24576)

    def __init__(self):
        self.entries = dict(self.PREDEFINED)
        self.label_lines = {}            # etiqueta -> línea donde se declaró
        self.next_variable = FIRST_VARIABLE

    def is_predefined(self, symbol):
        return symbol in self.PREDEFINED

    def add_label(self, symbol, address, line):
        if self.is_predefined(symbol):
            raise AsmError(line, f"la etiqueta '{symbol}' usa el nombre de un símbolo predefinido")
        if symbol in self.label_lines:
            raise AsmError(line, f"la etiqueta '{symbol}' ya fue declarada en la línea "
                                 f"{self.label_lines[symbol]}")
        self.entries[symbol] = address
        self.label_lines[symbol] = line

    def resolve(self, symbol, line):
        """Dirección de un símbolo; si es nuevo, se crea como variable."""
        if symbol not in self.entries:
            if self.next_variable > MAX_VALUE:
                raise AsmError(line, f"no hay direcciones disponibles para la variable '{symbol}'")
            self.entries[symbol] = self.next_variable
            self.next_variable += 1
        return self.entries[symbol]


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def clean(raw_line):
    """Quita el comentario (// hasta fin de línea) y todos los espacios/tabs."""
    cut = raw_line.find('//')
    if cut != -1:
        raw_line = raw_line[:cut]
    return ''.join(raw_line.split())


def parse_a(text, line):
    """'@valor' -> ('A', entero) o ('A', símbolo)."""
    body = text[1:]
    if not body:
        raise AsmError(line, "instrucción A sin valor '@'")
    if DECIMAL_RE.match(body):
        value = int(body)
        if value > MAX_VALUE:
            raise AsmError(line, f"constante fuera de rango '@{body}' (debe estar entre 0 y {MAX_VALUE})")
        return ('A', value)
    if body[0] in '0123456789':
        raise AsmError(line, f"símbolo inválido '{body}' (no puede empezar por un dígito)")
    if body[0] in '+-' and DECIMAL_RE.match(body[1:]):
        raise AsmError(line, f"constante inválida '@{body}' (solo se permiten valores entre 0 y {MAX_VALUE})")
    if not SYMBOL_RE.match(body):
        raise AsmError(line, f"símbolo inválido '{body}' en instrucción A")
    return ('A', body)


def parse_label(text, line):
    """'(NOMBRE)' -> ('L', NOMBRE)."""
    if not text.endswith(')') or len(text) < 2:
        raise AsmError(line, f"etiqueta sin paréntesis de cierre '{text}'")
    name = text[1:-1]
    if not name:
        raise AsmError(line, "etiqueta vacía '()'")
    if not SYMBOL_RE.match(name):
        raise AsmError(line, f"nombre de etiqueta inválido '{name}'")
    return ('L', name)


def parse_c(text, line):
    """'dest=comp;jump' -> ('C', dest, comp, jump), validando cada campo."""
    if text.endswith(')') and '(' not in text:
        raise AsmError(line, f"etiqueta sin paréntesis de apertura '{text}'")
    if text.count('=') > 1:
        raise AsmError(line, f"instrucción C con más de un '=': '{text}'")
    if text.count(';') > 1:
        raise AsmError(line, f"instrucción C con más de un ';': '{text}'")
    if '=' in text and ';' in text and text.index('=') > text.index(';'):
        raise AsmError(line, f"instrucción C mal formada '{text}' ('=' después de ';')")
    if '=' not in text and ';' not in text and text not in COMP:
        raise AsmError(line, f"instrucción no reconocida '{text}'")

    dest, comp, jump = '', text, ''
    if '=' in comp:
        dest, comp = comp.split('=')
        if not dest:
            raise AsmError(line, "destino vacío antes de '='")
        if dest not in DEST:
            raise AsmError(line, f"destino inválido '{dest}'")
    has_jump = ';' in comp
    if has_jump:
        comp, jump = comp.split(';')
    if not comp:
        raise AsmError(line, "cómputo vacío")
    if comp not in COMP:
        raise AsmError(line, f"cómputo inválido '{comp}'")
    if has_jump:
        if not jump:
            raise AsmError(line, "salto vacío después de ';'")
        if jump not in JUMP:
            hint = ' (los mnemónicos distinguen mayúsculas)' if jump.upper() in JUMP else ''
            raise AsmError(line, f"salto inválido '{jump}'{hint}")
    return ('C', dest, comp, jump)


def parse_line(text, line):
    if text.startswith('@'):
        return parse_a(text, line)
    if text.startswith('('):
        return parse_label(text, line)
    return parse_c(text, line)


def split_lines(source):
    """Divide en líneas aceptando LF o CRLF; conserva la numeración real."""
    if source.startswith('\ufeff'):   # BOM de UTF-8 (Bloc de notas)
        source = source[1:]
    return [l[:-1] if l.endswith('\r') else l for l in source.split('\n')]


# ---------------------------------------------------------------------------
# Ensamblado en dos pasadas
# ---------------------------------------------------------------------------

def assemble(source):
    """Devuelve la lista de palabras de 16 bits o lanza AsmError."""
    symbols = SymbolTable()
    program = []          # (línea, instrucción analizada) sin etiquetas
    address = 0           # dirección ROM de la siguiente instrucción

    # Primera pasada: analiza TODAS las líneas en orden (así el primer error
    # reportado es el de menor número de línea) y registra cada etiqueta con
    # la dirección de la instrucción que le sigue.
    for number, raw in enumerate(split_lines(source), 1):
        text = clean(raw)
        if not text:
            continue
        parsed = parse_line(text, number)
        if parsed[0] == 'L':
            symbols.add_label(parsed[1], address, number)
        else:
            if address >= ROM_SIZE:
                raise AsmError(number, f"el programa supera las {ROM_SIZE} instrucciones de la ROM")
            program.append((number, parsed))
            address += 1

    # Segunda pasada: resuelve símbolos (creando variables) y codifica.
    words = []
    for number, parsed in program:
        if parsed[0] == 'A':
            value = parsed[1]
            if isinstance(value, str):
                value = symbols.resolve(value, number)
            words.append(format(value, '016b'))
        else:
            _, dest, comp, jump = parsed
            words.append('111' + COMP[comp] + DEST[dest] + JUMP[jump])
    return words


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def remove_if_exists(path):
    try:
        os.remove(path)
    except OSError:
        pass


def main(argv):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if len(argv) != 2:
        print('ERROR *** Uso: ensamblador.sh ruta/Prog.asm')
        return 2
    input_path = argv[1]
    base, extension = os.path.splitext(input_path)
    if extension.lower() != '.asm':
        print(f"ERROR *** El archivo de entrada debe tener extensión .asm: '{input_path}'")
        return 2
    output_path = base + '.hack'

    try:
        with open(input_path, 'rb') as file:
            source = file.read().decode('utf-8', errors='replace')
    except OSError as error:
        print(f"ERROR *** No se pudo leer el archivo '{input_path}': {error.strerror}")
        return 1

    try:
        words = assemble(source)
    except AsmError as error:
        print(f'ERROR *** Línea {error.line}: {error.message}')
        remove_if_exists(output_path)   # nunca dejar una salida de una corrida anterior
        return 1

    # Mismo formato que el ensamblador oficial en Windows: CRLF por línea.
    with open(output_path, 'w', encoding='ascii', newline='') as file:
        file.write(''.join(word + '\r\n' for word in words))
    print(f'{input_path} -> {output_path} ({len(words)} instrucciones)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
