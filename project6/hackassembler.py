"""A HackAssembler and its REPL"""

from pathlib import Path
from utility import *

def assembler(parser, evaler):
    """Read each line until an end of file"""
    while True:
        line = parser.advance()
        if line is not None:
            binary_line = evaler.convert(line)
            yield binary_line 
        else:
            break
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
