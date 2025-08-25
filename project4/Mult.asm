//screen is at 16,384
//ram register of pixel: 16,384 + row*32 + column / 16; bit of register = column % 16
//keyboard is at register 24,576 and can be accessed via KEYBOARD

//Store values in variables
@0
D=M
@multiplicand
M=D
@1
D=M
@muliplicator
M=D
@product
M=0
//reset just in case
@R2
M=0


//Start
@Loop
0;JMP

//Value Assignment before concluding with infinite loop
(valueAssignment)
@product
D=M
@2
M=D
@End
0;JMP

//End
@End
0;JMP


(Loop)
@multiplicand
D=M
@product
M=D+M
@muliplicator
M=M-1
D=M
@valueAssignment
D;JEQ
@Loop
0;JMP
