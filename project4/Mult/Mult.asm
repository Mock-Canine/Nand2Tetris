// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

//// Replace this comment with your code.
/* My pseudocode
    i = 1
    sum = 0
LOOP:
    if i > R1 goto STOP
    i = i + 1
    sum = sum + R0
    goto LOOP
STOP:
    R2 = sum
*/

    @i
    M=1    // i = 1
    @R1    
    D=M
    @sum
    M=0    // sum = 0
    
(LOOP)
    @i
    D=M
    @R1
    D=D-M
    @STOP
    D;JGT   // if i > R1 goto STOP
    @i
    M=M+1
    @R0
    D=M
    @sum
    M=D+M   // sum = sum + R0
    @LOOP
    0;JMP
(STOP)
    @sum
    D=M
    @R2
    M=D    // R2 = sum
(END)
    @END
    0;JMP


