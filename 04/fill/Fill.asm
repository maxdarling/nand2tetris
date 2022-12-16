// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// pseudocode (cyclical pattern) (1-word at a time)
// SCREEN_SIZE = 8K
// offset = 0 // screen row = offset / 32, screen word = offset % 32
// while(true):
//   <fill the current word based on pressed key>
//   offset += 1
//   if offset >= 8K: offset = 0

// offset = 0
@offset
M=0
(LOOP)
// fill_color = nothing pressed ? white : black
@fill_color
M=0
@KBD
D=M
@COLOR_CHOSEN
D;JEQ
@fill_color
M=-1
(COLOR_CHOSEN)
// fill the word at 'offset'
@SCREEN
D=A
@offset
D=D+M
@word_addr
M=D
@fill_color
D=M
@word_addr
A=M
M=D
@1 // offset += 1
D=A
@offset
M=D+M
// if offset >= 8K: offset = 0
D=M
@8192
D=D-A
@DONT_RESET_OFFSET
D;JLT
@offset
M=0
(DONT_RESET_OFFSET)
@LOOP
0;JMP
