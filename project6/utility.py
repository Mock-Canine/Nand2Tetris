"""The utility module provides Parser, Evaler, SymbolTable classes and tool functions"""

import inspect
import sys

class Parser:
    """A Parser provides next line of tokens as a list each time it is queried 
    
    Its constructor takes a file object

    >>> comment_space_line = ['\\n', '//comment\\n', '\t// comment\\n']
    >>> a_instruction = ['@i', '\t// comment', '\t@15//comment', '\t@15 // comment']
    >>> c_instruction = ['\tD', 'D=M+1', 'M-1;JEQ', 'M=D+1;JEQ // comment']
    >>> parser1 = Parser(comment_space_line)
    >>> print(parser1.advance())
    None
    >>> parser2 = Parser(a_instruction)
    >>> [parser2.advance() for i in range(4)]
    [('A', 'i'), ('A', '15'), ('A', '15'), None]
    >>> parser3 = Parser(c_instruction)
    >>> [parser3.advance() for i in range(4)]
    [('C', ['null', 'D', 'null']), ('C', ['D', 'M+1', 'null']), ('C', ['null', 'M-1', 'JEQ']), ('C', ['M', 'D+1', 'JEQ'])]
    """
    _WHITESPACE = ' \t\n\r'

    def __init__(self, source):
        self.source = iter(source)
        self.next_line = None

    def advance(self):
        if self.has_more_lines:
            pre_command = self.preprocess()
            if pre_command is not None:
                return self.tokenlize(pre_command)
            return self.advance()
        return None

    @property
    def has_more_lines(self):
        """This method updates the next_line attribute, and must be called before advance()""" 
        try:
            self.next_line = next(self.source)
        except StopIteration:
            return False
        return True

    def preprocess(self):
        """Return a tuple (command_type, command) for tokenlizing, comments and whitesapces excluded(return None)"""
        command_type = None
        no_comment = self.next_line.split('/', 1)[0]
        command = no_comment.strip(self._WHITESPACE)
        if command:
            if '@' in command:
                command_type = 'A'
            elif '(' in command:
                command_type = 'L'
            else:
                command_type = 'C'
            return command_type, command
    
    def tokenlize(self, command):
        """Return a tuple (command_type, [token1, token2, ...])"""
        if command[0] == 'A':
            return command[0], command[1][1:]
        else:
            dest = "null"
            jump = "null"
            s = command[1]
            if ";" in s:
                s, jump = s.split(";", 1)
            if "=" in s:
                dest, comp = s.split("=", 1)
            else:
                comp = s
            return command[0], [dest, comp, jump]

class Evaler:
    """A Evaler converts the instructions into binary strings using the look-up table in the SymbolTable class or append new symbols in the table

    >>> symboltable = SymbolTable()
    >>> evaler = Evaler(symboltable)
    >>> a_command = ('A', '14')
    >>> evaler.convert(a_command)
    '0000000000001110'
    >>> c_command = [('C', ['D', 'M+1', 'null']), ('C', ['null', 'M-1', 'JEQ']), ('C', ['M', 'D+1', 'JEQ'])]
    >>> [evaler.convert(i) for i in c_command]
    ['1111110111010000', '1111110010000010', '1110011111001010']
    """

    def __init__(self, symboltable):
        self.symboltable = symboltable

    def convert(self, command):
        if command[0] == 'A':
            return str(format(int(command[1]), '016b'))   
        else:
            dest = self.symboltable.dest[command[1][0]]
            comp = self.symboltable.comp[command[1][1]]
            jmp = self.symboltable.jmp[command[1][2]]
            return '111' + comp + dest + jmp

class SymbolTable:
    """A symboltable contains all the name-address pairs of symbols"""
    pre_defined = {
		"SP":0,"LCL":1,"ARG":2,"THIS":3,"THAT":4,
		"R0":0,"R1":1,"R2":2,"R3":3,"R4":4,"R5":5,
		"R6":6,"R7":7,"R8":8,"R9":9,"R10":10,"R11":11,
		"R12":12,"R13":13,"R14":14,"R15":15,
		"SCREEN":16384,"KBD":24576} 
    comp = {
		"0":"0101010","1":"0111111","-1":"0111010",
		"D":"0001100","A":"0110000","!D":"0001101", 
		"!A":"0110001","-D":"0001111","-A":"0110011",
		"D+1":"0011111","A+1":"0110111","D-1":"0001110",
		"A-1":"0110010","D+A":"0000010","D-A":"0010011",
		"A-D":"0000111","D&A":"0000000","D|A":"0010101",
		"M":"1110000","!M":"1110001","-M":"1110011",
		"M+1":"1110111","M-1":"1110010","D+M":"1000010",
		"D-M":"1010011","M-D":"1000111","D&M":"1000000",
		"D|M":"1010101"}
    dest = {
		"null":"000","M":"001","D":"010","MD":"011",
		"A":"100","AM":"101","AD":"110","AMD":"111"}
    jmp = {
		"null":"000","JGT":"001","JEQ":"010","JGE":"011",
		"JLT":"100","JNE":"101","JLE":"110","JMP":"111"}

    def __init__(self):
        self.user_symbol = {}

def main(fn):
    """Call fn with command line arguments.  Used as a decorator.

    The main decorator marks the function that starts a program. For example,

    @main
    def my_run_function():
        # function body

    Use this instead of the typical __name__ == "__main__" predicate.
    """
    if inspect.stack()[1][0].f_locals['__name__'] == '__main__':
        args = sys.argv[1:] # Discard the script name from command line
        fn(*args) # Call the main function
    return fn

