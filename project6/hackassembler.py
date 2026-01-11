"""A HackAssembler"""

from pathlib import Path
from utility import *

def assembler(parser, evaler):
    """First pass to process (Xxx) instructions and populate instances of instructions 
    into the list, then convert the instructions into binary codes"""
    instructions = []
    while True:
        command = parser.advance()
        if command is not None:
            if isinstance(command, CommandL):
                evaler.populate(command)
            else:
                instructions.append(command)
        else:
            break
    yield from map(evaler.convert, instructions)

@main
def run(*argv):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', type=argparse.FileType('r'), default=None, help='.asm file to run')
    args = parser.parse_args()

    assert args.file is not None, 'Please provide one .asm file to convert'
    parser = Parser(args.file)
    symboltable = SymbolTable()
    evaler = Evaler(symboltable)
    out_file = Path(args.file.name).with_suffix(".hack")
    
    with open(out_file, 'w') as f:
        f.writelines(line + '\n' for line in assembler(parser, evaler))
