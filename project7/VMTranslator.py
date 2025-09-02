import os
import sys

class vm_compiler:
    
    def __init__(self):
        
        # key is the order in which the vm was compiled
        # value is the resulting hack code
        self.compiled_hack = {}
        self.vm_line_index = 0
        # used for distinguishing jumps
        self.loop_counter = 0
        
    
    def _translate_vm_command(self, vm_code):
        """
        translate vm code to hack
        inputs:
            * vm_code: str
        outputs:
            * hack_code: list of str
        """
        if vm_code.split(' ')[0] in ('push', 'pop'):
            return self._translate_stack_command(vm_code)
        else:
            return self._translate_logic_command(vm_code)
    
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
                    'M=M-1',
                    'A=M',
                    'D=M',
                    'M=0',
                    f'@{self.file_name}.{index}',
                    'A=M',
                    'M=D'
                ]
            else:
                hack_code = [
                    f'@{self.file_name}.{index}',
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
                
        return [line + '\n' for line in hack_code]
        
    
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
            
        return [line + '\n' for line in hack_code]
    
    def get_compiled_hack(self):
        return self.compiled_hack
        
    def read_file(self, file_path):
        """
        read file, trim spaces and comments, and convert lines of vm commands to list
        """
        self.file_name = file_path.split('.')[0].split('\\')[-1]
        
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
        
        while self.vm_line_index < len(self.vm_commands):
            
            self.compiled_hack[self.vm_line_index] = self.compile_next_line()
            self.vm_line_index+=1
    
    def compile_next_line(self):
        """
        Given vm command
        1. translate to list of hack commands
        2. insert commented vm code at beginning
        """
        
        hack_code_list = ['// '+ self.vm_commands[self.vm_line_index] + '\n']
        hack_code_list += self._translate_vm_command(self.vm_commands[self.vm_line_index])
        
        return hack_code_list
    
    def write_hack_code(self, file_path):
        with open(file_path, "w") as file:
            lines = []
            for hack_lines in self.compiled_hack.values():
                lines+=hack_lines
            file.writelines(lines)
            
def main(file):
    comp = vm_compiler()
    comp.read_file(file)
    comp.compile_all_lines()
    asm_file = file.split('.')[0]+'.asm'
    comp.write_hack_code(asm_file)

if __name__ == "__main__":
    file = sys.argv[1]
    main(file)

        
