// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.
/*My pseudocode
RESET:
    i = 0
    addr = SCREEN
    n = 8192
    pixel = !pixel
CHECK:
    if pixel == 0 goto CHECK1
CHECK0
    if KBD == 0 goto CHECK0
    goto LOOP
CHECK1
    if KBD != 0 goto CHECK1
LOOP:
    if i == n goto RESET
    RAM[addr] = pixel
    addr = addr + 1
    i = i + 1
    goto LOOP
*/
(RESET)
    @SCREEN
    D=A
    @addr
    M=D // addr = SCREEN
    @i
    M=0 // i = 0
    @8192
    D=A
    @n
    M=D // n = 8192
    @pixel
    M=!M // pixel = !pixel
(CHECK)
    @pixel
    D=M
    @CHECK1
    D;JEQ // if pixel == 0 goto CHECK1
(CHECK0)
    @KBD
    D=M
    @CHECK0
    D;JEQ
    @LOOP
    0;JMP // if KBD == 0 goto CHECK0 else goto LOOP
(CHECK1)
    @KBD
    D=M
    @CHECK1
    D;JNE // if KBD != 0 goto CHECK1
(LOOP)
    @i
    D=M
    @n
    D=D-M
    @RESET
    D;JEQ // if i == n goto RESET
    @pixel
    D=M
    @addr
    A=M
    M=D // RAM[addr] = pixel
    @addr
    M=M+1 // addr = addr + 1
    @i
    M=M+1 // i = i + 1
    @LOOP
    0;JMP // goto LOOP