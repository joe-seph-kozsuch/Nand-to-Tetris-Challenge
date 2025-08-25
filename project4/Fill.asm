// Continually loop, checking for key press

//screen is at 16,384
//ram register of pixel: 16,384 + row*32 + column / 16; bit of register = column % 16
//keyboard is at register 24,576 and can be accessed via KEYBOARD

@ResetIndex
0;JMP

(CheckKeys)
@KBD
D=M
@WhitenScreen
D;JEQ
@DarkenScreen
D;JGT

//reset index before returning to infinite key check loop
(ResetIndex)
@SCREEN
D=A
@RegisterIndex
M=D
@CheckKeys
0;JMP

(DarkenScreen)
@RegisterIndex
D=M
@24576
D=A-D
@DarkenRegister
D;JGT
@ResetIndex
0;JMP

(WhitenScreen)
@RegisterIndex
D=M
@24576
D=A-D
@WhitenRegister
D;JGT
@ResetIndex
0;JMP

(DarkenRegister)
@RegisterIndex
A=M
M=-1
@RegisterIndex
M=M+1
@DarkenScreen
0;JMP

(WhitenRegister)
@RegisterIndex
A=M
M=0
@RegisterIndex
M=M+1
@WhitenScreen
0;JMP