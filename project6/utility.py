"""The utility module provides Parser, Evaler, SymbolTable classes, 
three classes to represent instructions, tool functions"""

import inspect
import sys

class Parser:
    """A Parser provides an instance of one instruction each time it is queried 
    
    Its constructor takes an iterable containing lines of instructions

    >>> comment_space_line = ['\\n', '//comment\\n', '\t// comment\\n']
    >>> a_instruction = ['@i', '\t// comment', '\t@15//comment', '\t@15 // comment']
    >>> l_instruction = ['(LOOP)', '0;JMP']
    >>> c_instruction = ['\tD', 'D=M+1', 'M-1;JEQ', 'M=D+1;JEQ // comment']
    >>> parser1 = Parser(comment_space_line)
    >>> print(parser1.advance())
    None
    >>> parser2 = Parser(a_instruction)
    >>> [parser2.advance() for i in range(4)]
    [(A, i), (A, 15), (A, 15), None]
    >>> parser3 = Parser(l_instruction)
    >>> [parser3.advance() for i in range(2)]
    [(L, LOOP, 0), (C, [null, 0, JMP])]
    >>> parser4 = Parser(c_instruction)
    >>> [parser4.advance() for i in range(4)]
    [(C, [null, D, null]), (C, [D, M+1, null]), (C, [null, M-1, JEQ]), (C, [M, D+1, JEQ])]
    """
    _WHITESPACE = ' \t\n\r'

    def __init__(self, source):
        self.source = iter(source)
        self.next_line = None
        self.line_idx = 0 # used as the value of commandL

    def advance(self):
        if self.has_more_lines:
            pre_command = self.preprocess()
            if pre_command:
                return self.tokenlize(pre_command)
            return self.advance()
        return None

    @property
    def has_more_lines(self):
        """This method updates the next_line attribute"""
        try:
            self.next_line = next(self.source)
        except StopIteration:
            return False
        return True

    def preprocess(self):
        """Get rid of comments and whitespaces. Empty lines and comment lines become '' """
        no_comment = self.next_line.split('/', 1)[0]
        return no_comment.strip(self._WHITESPACE)
    
    def tokenlize(self, command):
        """Return an instance of command A, L or C"""
        if '@' in command:
            self.line_idx += 1
            return CommandA(command[1:])
        elif '(' in command:
            return CommandL(command[1:].rstrip(')'), self.line_idx) # commandL will not advance line_idx
        else:
            dest = "null"
            jmp = "null"
            if ";" in command:
                command, jmp = command.split(";", 1)
            if "=" in command:
                dest, comp = command.split("=", 1)
            else:
                comp = command
            self.line_idx += 1
            return CommandC(dest, comp, jmp)

class Evaler:
    """An Evaler converts the instructions into binary strings using the look-up table in the SymbolTable class or appends new symbols into the table

    >>> symboltable = SymbolTable()
    >>> evaler = Evaler(symboltable)
    >>> a_command = CommandA('i')
    >>> evaler.convert(a_command)
    '0000000000010000'
    >>> evaler.convert(CommandA('sum'))
    '0000000000010001'
    >>> evaler.convert(CommandA('i'))
    '0000000000010000'
    >>> evaler.convert(CommandA('R0'))
    '0000000000000000'
    >>> c_command = [CommandC('D', 'M+1', 'null'), CommandC('null', 'M-1', 'JEQ'), CommandC('M', 'D+1', 'JEQ')]
    >>> [evaler.convert(i) for i in c_command]
    ['1111110111010000', '1111110010000010', '1110011111001010']
    """

    def __init__(self, symboltable):
        self.symboltable = symboltable

    def convert(self, command):
        """Convert the command instance into binary strings"""
        if isinstance(command, CommandA):
            if command.value.isnumeric():
                value = int(command.value)
            else:
                value = self.symboltable.retrieve(command)
            return str(format(value, '016b'))   
        return '111' + self.symboltable.retrieve(command) 

    def populate(self, commandL):
        """Populate the symboltable with commandL during first pass"""
        self.symboltable.deposit(commandL)

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
        self.address_index = 16

    def retrieve(self, command):
        """Return the address of components of commands, allocate the address from 16 if commandA  
        represents a variable and should be initilized
        """
        if isinstance(command, CommandA):
            value = command.value
            if value in self.pre_defined:
                return self.pre_defined[value]
            elif value not in self.user_symbol:
                self.user_symbol[value] = self.address_index
                self.address_index += 1
            return self.user_symbol[value]
        else:
            dest = self.dest[command.dest]
            comp = self.comp[command.comp]
            jmp = self.jmp[command.jmp]
            return comp + dest + jmp

    def deposit(self, commandL):
        self.user_symbol[commandL.label] = commandL.value

class CommandA:
    """@value"""
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return f"(A, {self.value})"

class CommandC:
    """dest=comp;jmp"""
    def __init__(self, dest, comp, jmp):
        self.dest = dest
        self.comp = comp
        self.jmp = jmp

    def __repr__(self):
        return f"(C, [{self.dest}, {self.comp}, {self.jmp}])"

class CommandL:
    """(Xxx)"""
    def __init__(self, label: str, value: int):
        self.label = label
        self.value = value

    def __repr__(self):
        return f"(L, {self.label}, {self.value})"

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

