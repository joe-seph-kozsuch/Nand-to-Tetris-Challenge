import os
import sys

class vm_compiler:
    
    def __init__(self, needs_initializing = False):
        
        # key is the order in which the vm was compiled
        # value is the resulting hack code
        self.compiled_hack = {}
        self.vm_line_index = 0
        # used for distinguishing jumps
        self.loop_counter = 0
        self.needs_initializing = needs_initializing
        self.function_argument_count = {}
        self.most_recent_function_file = ''
        
    
    def _translate_vm_command(self, vm_code):
        """
        translate vm code to hack
        inputs:
            * vm_code: str
        outputs:
            * hack_code: list of str
        """
        operation_map = {
            'push': self._translate_stack_command,
            'pop': self._translate_stack_command,
            'label': self._translate_label_command,
            'function': self._translate_function_command,
            'return': self._translate_return_command,
            'call': self._translate_call_command,
            'goto': self._translate_branch_command,
            'if-goto': self._translate_branch_command,
            'add': self._translate_logic_command,
            'sub': self._translate_logic_command,
            'neg': self._translate_logic_command,
            'eq': self._translate_logic_command,
            'gt': self._translate_logic_command,
            'lt': self._translate_logic_command,
            'and': self._translate_logic_command,
            'or': self._translate_logic_command,
            'not': self._translate_logic_command
        }
        
        operation = vm_code.split(' ')[0]
        
        return operation_map[operation](vm_code)
    
    def _translate_stack_command(self, stack_vm_code):
        """
        translate stack command of form push/pop [segment] [index]
        """
        
        pop_push, segment, index = stack_vm_code.split(' ')
        
        # translate constant
        if segment == 'constant':
            # constant can only push value
            hack_code = [
                f'@{index}',
                'D=A',
                '@SP',
                'M=M+1',
                'A=M-1',
                'M=D'
            ]
            
        if segment in ['local','argument','this','that']:
            vm_hack_mem_seg_map = {
                'local': 'LCL',
                'argument': 'ARG',
                'this': 'THIS',
                'that': 'THAT'
            }
            
            segment_hack = vm_hack_mem_seg_map[segment]
            
            if pop_push == 'pop':
                hack_code = [
                    f'@{segment_hack}',
                    'D=M',
                    f'@{index}',
                    'D=D+A',
                    '@R13',
                    'M=D',
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    'M=0',
                    '@R13',
                    'A=M',
                    'M=D'
                ]
            else:
                hack_code = [
                    f'@{segment_hack}',
                    'D=M',
                    f'@{index}',
                    'A=D+A',
                    'D=M',
                    '@SP',
                    'M=M+1',
                    'A=M-1',
                    'M=D'
                ]
                
        if segment == 'temp':
            # this is almost the same as four above,
            # but temp memory segment always starts at five,
            # so indixing is a little different
            if pop_push == 'pop':
                hack_code = [
                    '@5',
                    'D=A',
                    f'@{index}',
                    'D=D+A',
                    '@R13',
                    'M=D',
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    'M=0',
                    '@R13',
                    'A=M',
                    'M=D'
                ]
            else:
                hack_code = [
                    '@5',
                    'D=A',
                    f'@{index}',
                    'A=D+A',
                    'D=M',
                    '@SP',
                    'M=M+1',
                    'A=M-1',
                    'M=D'
                ]
                
        if segment == 'static':
            if pop_push == 'pop':
                hack_code = [
                    '@SP',
                    'AM=M-1',
                    'D=M',
                    'M=0',
                    f'@{self.most_recent_function_file}.{index}',
                    'M=D'
                ]
            else:
                hack_code = [
                    f'@{self.most_recent_function_file}.{index}',
                    'D=M',
                    '@SP',
                    'M=M+1',
                    'A=M-1',
                    'M=D'
                ]
                
        if segment == 'pointer':
            if index == '0':
                pointer = 'THIS'
            else:
                pointer = 'THAT'
            
            if pop_push == 'pop':
                hack_code = [
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    'M=0',
                    f'@{pointer}',
                    'M=D',
                ]
                
            else:
                hack_code = [
                    f'@{pointer}',
                    'D=M',
                    '@SP',
                    'M=M+1',
                    'A=M-1',
                    'M=D'
                ]
                
        return hack_code
        
    
    def _translate_logic_command(self, logic_vm_code):
        """
        translate vm logic command to hack
        input:
            * logic_vm_code: str
        output:
            * hack_code: list of str
        """

        
        if logic_vm_code == 'neg':
            hack_code = [
                '@SP',
                'A=M-1',
                'M=-M',
            ]
        elif logic_vm_code == 'add':
            hack_code = [
                '@SP',
                'A=M-1',
                'D=M',
                'M=0',
                '@SP',
                'M=M-1',
                'A=M-1',
                'M=D+M',
            ]
            
        elif logic_vm_code == 'sub':
            hack_code = [
                '@SP',
                'A=M-1',
                'D=M',
                'M=0',
                '@SP',
                'M=M-1',
                'A=M-1',
                'M=M-D',
            ]
            
        elif logic_vm_code == 'eq':
            hack_code = [
                '@SP',
                'AM=M-1',
                'D=M',
                'M=0',
                '@SP',
                'A=M-1',
                'D=M-D',
                'M=0',
                f'@eq_{self.loop_counter}',
                'D;JNE',
                '@SP',
                'A=M-1',
                'M=-1',
                f'(eq_{self.loop_counter})'
            ]
            self.loop_counter += 1
            
        elif logic_vm_code == 'gt':
            hack_code = [
                '@SP',
                'AM=M-1',
                'D=M',
                'M=0',
                '@SP',
                'A=M-1',
                'D=M-D',
                'M=0',
                f'@gt_{self.loop_counter}',
                'D;JLE',
                '@SP',
                'A=M-1',
                'M=-1',
                f'(gt_{self.loop_counter})'
            ]
            self.loop_counter += 1
            
        elif logic_vm_code == 'lt':
            hack_code = [
                '@SP',
                'AM=M-1',
                'D=M',
                'M=0',
                '@SP',
                'A=M-1',
                'D=M-D',
                'M=0',
                f'@lt_{self.loop_counter}',
                'D;JGE',
                '@SP',
                'A=M-1',
                'M=-1',
                f'(lt_{self.loop_counter})'
            ]
            self.loop_counter += 1
            
        elif logic_vm_code == 'and':
            hack_code = [
                '@SP',
                'A=M-1',
                'D=M',
                'M=0',
                '@SP',
                'M=M-1',
                'A=M-1',
                'M=D&M',
            ]
            
        elif logic_vm_code == 'or':
            hack_code = [
                '@SP',
                'A=M-1',
                'D=M',
                'M=0',
                '@SP',
                'M=M-1',
                'A=M-1',
                'M=D|M',
            ]
            
        elif logic_vm_code == 'not':
            hack_code = [
                '@SP',
                'A=M-1',
                'M=!M'
            ]
            
        return hack_code
    
    def _translate_call_command(self, vm_code):
        """
        inputs:
            * num_arguments: int, number of arguments passed into function
            * num_local: int, number of local argument in funciton memory segment
            * function_name: str, name of function being called
        outputs:
            * hack_code: list, hack assembly code w/o new line \n in strings

        1. Save ROM program location where this function was called
        2. push 4 pointers onto stack:  LCL, ARG, THIS, THAT
        3. push argument pointer for new function: ARG = SP - 5 - nArgs
        4. initiate local variable pointer: LCL = SP
        5. Move stack pointer to after local memory segment
        6. jump to ROM location of next function
        """

        _, function_name, num_arguments = vm_code.split(" ")
        
        num_local = self.function_argument_count[function_name]

        hack_code = []

        # add returnAddress
        hack_code += [
            f'// ___ Function {function_name} Call _____',
            '// Add ROM return address to stack (defined at end of call command)',
            f'@{function_name}.{self.loop_counter}',
            'D=A',
            '@SP',
            'M=M+1',
            'A=M-1',
            'M=D',
        ]

        # add LCL, ARG, THIS, THAT to stack and set each pointer to 0
        for pointer in ['LCL','ARG','THIS','THAT']:
            hack_code+=[
                f'// Add pointer {pointer} to stack',
                f'@{pointer}',
                'D=M',
                'M=0',
                '@SP',
                #move stack pointer up one since next two lines will insert value
                'M=M+1', 
                'A=M-1',
                'M=D',
            ]

        # set ARG
        hack_code += [
            '// Set new ARG pointer for new function',
            '@SP',
            'D=M',
            f'@{num_arguments}',
            'D=D-A',
            '@5',
            'D=D-A',
            '@ARG',
            'M=D'
        ]

        # set LCL
        hack_code += [
            '// Set new LCL pointer for new function',
            '@SP',
            'D=M',
            '@LCL',
            'M=D'
        ]
        
        # initialize all locals to 0
        for offset in range(int(num_local)):
            hack_code += [
                f"// Set local variable {offset} to 0",
                "@LCL",
                "D=M",
                f"@{offset}",
                "A=D+A",
                "M=0"
            ]

        # set stack pointer
        hack_code += [
            '// set stack pointer for new function',
            '@SP',
            'D=M',
            f'@{num_local}',
            'D=D+A',
            '@SP',
            'M=D'
        ]

        # move ROM program line
        hack_code += [
            '// jump to function label and create return address label',
            f'@{function_name}',
            '0;JMP',
            f'({function_name}.{self.loop_counter})'
        ]

        self.loop_counter+=1

        return hack_code
    
    def _translate_return_command(self, vm_code):
        """
        inputs:
            null
        outputs:
            * hack_code: list, hack assembly code w/o new line \n in strings

        1. create variable to reference end of previous pointers, endFrame = *LCL
        2. returnAddr = endFrame - 5
        3. *ARG = pop value from local stack
        4. SP = ARG + 1
        5. reinstate pointers of previous function
        6. jump to previous ROM location at previous location
        Note: I don't need to nullify (set to 0) values of saved pointers or callee local/stack.
            The program will not pop the values at those cells without overwriting them with a push.
        """

        hack_code = []

        hack_code += [
            '// set temp endFrame variable for referencing parent function pointers',
            '@LCL',
            'D=M',
            '@end_frame',
            'M=D',
        ]

        hack_code += [
            '// set temp rom-return-address variable for easy access',
            '@5',
            'A=D-A',
            'D=M',
            '@rom_return_address',
            'M=D',
        ]

        hack_code += [
            '// return value to parent function',
            '@SP',
            'A=M-1',
            'D=M',
            'M=0',
            '@ARG',
            'A=M',
            'M=D'
        ]

        hack_code += [
            '// reset stack pointer to prior stack (just after returned value)',
            '@ARG',
            'D=M+1',
            '@SP',
            'M=D'
        ]

        for pointer, offset in {'LCL':4,'ARG':3,'THIS':2,'THAT':1}.items():

            hack_code += [
                f'// reinstate pointer {pointer} of parent function',
                '@end_frame',
                'D=M',
                f'@{offset}',
                'A=D-A',
                'D=M',
                f'@{pointer}',
                'M=D'
            ]

        hack_code += [
            '@rom_return_address',
            'A=M',
            '0;JMP'
        ]

        return hack_code
    
    
    def _translate_label_command(self,vm_code):
        """
        convert to asm label 
        """
        _, label_name = vm_code.split(" ")

        return [f"({label_name})"]

    def _translate_function_command(self,vm_code):
        """
        convert to asm label
        """
        _, function_name, _ = vm_code.split(" ")
        
        self.most_recent_function_file = function_name.split(".")[0]

        return [f"({function_name})"]

    def _translate_branch_command(self,vm_code):
        """
        convert from vm jump to asm jump
        For conditional, boolean value needs to be popped from stack
        """

        jump_type, label = vm_code.split(" ")

        if jump_type == 'goto':
            hack_code = [
                f'@{label}',
                '0;JMP'
            ]

        else: # jump_type == 'if-goto'
            hack_code = [
                '@SP',
                'AM=M-1',
                'D=M',
                'M=0',
                f'@{label}',
                'D;JGT'
            ]

        return hack_code
    
    
    def get_compiled_hack(self):
        return self.compiled_hack

    def get_cleaned_vm_commands(self):
        return self.vm_commands

    def intake_vm_code(self, vm_code, input_object_name):
        """
        alternative to read_file()
        receives already de-commented and stripped vm code
        and assigns to class variable self.vm_commands for translation
        input:
            * vm_code: list of str
        output:
        """
        self.vm_commands = vm_code
        self.file_name = input_object_name
        
    def read_file(self, file_path):
        """
        read file, trim spaces and comments, and convert lines of vm commands to list
        """
        self.file_name = os.path.basename(file_path).split(".")[0]
        
        with open(file_path, 'r') as file:
            lines = file.readlines()
            
        self.vm_commands = []
        for line in lines:
            if len(line.strip()) == 0:
                continue
            if line.strip()[0] == '/':
                continue
            
            self.vm_commands.append(
                line.split('/')[0].strip()
            )
        
    def compile_all_lines(self):
        """
        compile all vm commands into hack
        and store in compiled_hack by line number
        """
        
        # first need to iterate through lines searching for functions 
        # so as to store the number of local arguments for function calls
        for vm_code in self.vm_commands:
            if vm_code.split(' ')[0] == 'function':
                _,func_name, num_local = vm_code.split(' ')
                self.function_argument_count[func_name] = num_local
                
        if self.needs_initializing:
            # set stack pointer
            self.compiled_hack[-1] = self._initialize_memory_segments()
            # initialize first function
            self.vm_commands = ['call Sys.init 0'] + self.vm_commands
        
        while self.vm_line_index < len(self.vm_commands):
            
            self.compiled_hack[self.vm_line_index] = self._compile_next_line()
            self.vm_line_index+=1
            
    def _initialize_memory_segments(self):
        """
        if sys.init is ran to begin program,
        and test script does not initialize sp and other memory segments,
        begin asm with following hack code
        """
        
        hack_code = [
            "@256",
            "D=A",
            "@SP",
            "M=D",
        ]
        
        return hack_code
    
    def _compile_next_line(self):
        """
        Given vm command
        1. translate to list of hack commands
        2. insert commented vm code at beginning
        
        input:
            null (reads from self.compiled_hack, a dict by line value of hack)
        output:
            hack_code_list: list of asm lines translated from vm
        """
        
        hack_code_list = ['// '+ self.vm_commands[self.vm_line_index]]
        hack_code_list += self._translate_vm_command(self.vm_commands[self.vm_line_index])
        
        return hack_code_list
    
    def write_hack_code(self, file_path):
        with open(file_path, "w") as file:
            lines = []
            for hack_lines in self.compiled_hack.values():
                lines+= [i+'\n' for i in hack_lines]
            file.writelines(lines)


            
def main(input_object):
    
    vm_files = []
    if "." not in input_object:
        asm_file_name = os.path.join(input_object, os.path.basename(input_object) +'.asm')
        for file in os.listdir(input_object):
            if ".vm" in file:
                vm_files.append(os.path.join(input_object, file))
    else:
        vm_files.append(input_object)
        asm_file_name = os.path.abspath(input_object).split(".")[0]+'.asm'

    vm_commands = []
    
    for vm_file_name in vm_files:

        comp = vm_compiler()
        comp.read_file(vm_file_name)
        vm_commands += comp.get_cleaned_vm_commands()
    
    if 'element' in input_object.lower() or 'static' in input_object.lower():
        comp = vm_compiler(True)
    else:
        comp = vm_compiler()
    comp.intake_vm_code(vm_commands, os.path.basename(input_object))
    comp.compile_all_lines()
    comp.write_hack_code(asm_file_name)



if __name__ == "__main__":
    cmd_input = sys.argv[1]
    main(cmd_input)

        
