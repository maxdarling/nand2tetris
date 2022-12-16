// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// strategy: define a counter n = 0 and set r2 = 0
// we will perform r2 = r2 + r0, r1 times.

// n = 0
@n
M=0
// r2 = 0
@R2
M=0
(LOOP)
// if n == r1: goto STOP
@n
D=M
@R1
D=D-M
@STOP
D;JEQ
// r2 += r0
@R0
D=M
@R2
M=M+D
// n += 1
@n
M=M+1
@LOOP
0;JMP
(STOP)
(END)
@END
0;JMP



