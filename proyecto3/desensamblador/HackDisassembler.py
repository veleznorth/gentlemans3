"""Avance del trabajo 3: desensamblador Hack.

Uso: python3 HackDisassembler.py Prog.hack [-o Prog.asm] [--force]
Traduce instrucciones binarias de 16 bits a mnemonicos A/C y genera
etiquetas de salto automaticamente (seccion 9.1): cuando una
instruccion @valor es seguida de una instruccion C con salto no vacio,
"valor" se trata como direccion destino: se reemplaza por una etiqueta
Lk y se inserta "(Lk)" antes de la instruccion ubicada en esa direccion.
"""

import re
import argparse
from dataclasses import dataclass
from pathlib import Path

COMP_REV = {
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
DEST_REV = {'000': '', '001': 'M', '010': 'D', '011': 'MD',
            '100': 'A', '101': 'AM', '110': 'AD', '111': 'AMD'}
JUMP_REV = {'000': '', '001': 'JGT', '010': 'JEQ', '011': 'JGE',
            '100': 'JLT', '101': 'JNE', '110': 'JLE', '111': 'JMP'}

BIT16 = re.compile(r'[01]{16}\Z')


def decode_comp(bits: str) -> str:
    try:
        return COMP_REV[bits]
    except KeyError:
        raise ValueError(f'campo comp invalido: {bits!r}') from None


@dataclass(frozen=True)
class Word:
    line: int
    bits: str

    def kind(self) -> str:
        return 'A' if self.bits[0] == '0' else 'C'

    def a_value(self) -> int:
        return int(self.bits[1:], 2)

    def c_fields(self) -> tuple[str, str, str]:
        comp_bits = self.bits[3] + self.bits[4:10]
        dest = DEST_REV[self.bits[10:13]]
        jump = JUMP_REV[self.bits[13:16]]
        return dest, decode_comp(comp_bits), jump


class BinaryParser:
    def __init__(self, source: str):
        self.words = []
        for number, raw in enumerate(source.splitlines(), 1):
            text = raw.strip()
            if not text:
                continue
            if not BIT16.fullmatch(text):
                raise ValueError(f'Linea {number}: instruccion invalida: {text!r}')
            self.words.append(Word(number, text))

    def __iter__(self):
        return iter(self.words)


def disassemble(source: str) -> str:
    words = list(BinaryParser(source))

    # Primera pasada: detectar pares (@valor, instruccion C con salto) y
    # asignar etiquetas Lk a cada direccion destino, en orden de aparicion.
    labels_by_address: dict[int, str] = {}
    is_jump_source = [False] * len(words)
    for index, word in enumerate(words):
        if word.kind() != 'A':
            continue
        if index + 1 >= len(words) or words[index + 1].kind() != 'C':
            continue
        try:
            _, _, jump = words[index + 1].c_fields()
        except ValueError as error:
            raise ValueError(f'Linea {words[index + 1].line}: {error}') from None
        if not jump:
            continue
        address = word.a_value()
        if address not in labels_by_address:
            labels_by_address[address] = f'L{len(labels_by_address)}'
        is_jump_source[index] = True

    # Segunda pasada: emitir mnemonicos, insertando "(Lk)" antes de la
    # instruccion en esa direccion y sustituyendo "@valor" por "@Lk".
    result = []
    for index, word in enumerate(words):
        if index in labels_by_address:
            result.append(f'({labels_by_address[index]})')
        if word.kind() == 'A':
            value = word.a_value()
            if is_jump_source[index]:
                result.append(f'@{labels_by_address[value]}')
            else:
                result.append(f'@{value}')
        else:
            try:
                dest, comp, jump = word.c_fields()
            except ValueError as error:
                raise ValueError(f'Linea {word.line}: {error}') from None
            text = comp if not dest else f'{dest}={comp}'
            if jump:
                text += f';{jump}'
            result.append(text)
    return ''.join(line + '\n' for line in result)


def translate_cli(translator, input_suffix: str, output_suffix: str, description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('input', type=Path, help=f'archivo {input_suffix}')
    parser.add_argument('-o', '--output', type=Path, help='ruta del archivo de salida')
    parser.add_argument('--force', action='store_true', help='permitir reemplazar una salida existente')
    args = parser.parse_args()
    output = args.output or args.input.with_suffix(output_suffix)
    try:
        if args.input.suffix.lower() != input_suffix:
            raise ValueError(f'la entrada debe tener extension {input_suffix}')
        if args.input.resolve() == output.resolve():
            raise ValueError('la salida debe ser distinta de la entrada')
        result = translator(args.input.read_text(encoding='utf-8-sig'))
        with output.open('w' if args.force else 'x', encoding='utf-8', newline='\n') as file:
            file.write(result)
    except FileExistsError:
        parser.exit(1, f'ERROR *** {output} ya existe; usa -o o --force.\n')
    except (OSError, ValueError) as error:
        parser.exit(1, f'ERROR *** {error}\n')
    print(f'{args.input} -> {output} ({len(result.splitlines())} instrucciones)')


if __name__ == '__main__':
    translate_cli(disassemble, '.hack', '.asm', 'Desensamblador Hack')
