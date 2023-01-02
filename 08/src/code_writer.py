import vm_constants as vm

class CodeWriter:
    """Translates parsed VM commands into Hack assembly.

    Output is written sequentially to the specified filepath.
    You must use 'set_vm_filename()' before any write commands
    for ~each~ .vm file you work with.

    Example usage:
        cw = CodeWriter('out/Prog.asm')
        cw.set_vm_filename('out/Prog.vm')
        // local[0] += 1
        cw.writePushPop(vm.CommandType.PUSH, 'local', 0)
        cw.writePushPop(vm.CommandType.PUSH, 'constant', 1)
        cw.writeArithmetic('add')
        cw.writePushPop(vm.CommandType.POP, 'local', 0)
        cw.close()
    """
    # Developer note: this code was written for maximum simplicity, whereas optimization
    # was not a priority. Overall the generated assembly is far from optimal.

    def __init__(self, filepath: str):
        """Perform setup. 'filepath' is the .asm file to write output to."""
        self._f = open(filepath, 'w', encoding=None)
        # use user-inputted file base name for static var scoping
        self._filename_base = '_VM_init_filename'
        # bookeep current function name for labels and call/return
        self._curr_func = '_VM_init_func'
        # running integer for generating unique labels
        self._label_cnt = 0
        
        # Jack standard initialization: set SP=256 and call Sys.init
        self._f.write('// standard bootstrap: setup stack and call Sys.init\n')
        self._f.write('@256\nD=A\n@SP\nM=D\n')
        self.write_call('Sys.init', 0)

    def set_vm_filename(self, filepath: str):
        """Ready a new VM file for processing."""
        slash_idx = filepath.rfind('/')
        start = slash_idx + 1 if slash_idx != -1 else None
        self._filename_base = filepath[start:-3]

    def write_arithmetic(self, command: str):
        """Translate an arithmetic command."""
        if command == 'add':
            self._pop_addr('R13')
            self._pop_addr('R14')
            self._f.write('@R13\nD=M\n@R14\nM=M+D\n')
            self._push_addr('R14')
        elif command == 'sub':
            self._pop_addr('R13')
            self._pop_addr('R14')
            self._f.write('@R13\nD=M\n@R14\nM=M-D\n')
            self._push_addr('R14')
        elif command == 'neg':
            self._pop_addr('R13')
            self._f.write('@R13\nM=-M\n')
            self._push_addr('R13')
        elif command == 'eq':
            self._cmp('D;JEQ')
        elif command == 'gt':
            self._cmp('D;JGT')
        elif command == 'lt':
            self._cmp('D;JLT')
        elif command == 'and':
            self._pop_addr('R13')
            self._pop_addr('R14')
            self._f.write('@R13\nD=M\n@R14\nM=D&M\n')
            self._push_addr('R14')
        elif command == 'or':
            self._pop_addr('R13')
            self._pop_addr('R14')
            self._f.write('@R13\nD=M\n@R14\nM=D|M\n')
            self._push_addr('R14')
        elif command == 'not':
            self._pop_addr('R13')
            self._f.write('@R13\nM=!M\n')
            self._push_addr('R13')
        else:
            print('ERROR - invalid arithmetic command')

    def write_push_pop(
            self,
            cmd_type: vm.CommandType,
            segment: str,
            index: int
    ):
        """Translate a push/pop command at a given segment and index."""
        seg = {
               # dereferenced
               'argument' : 'ARG',
               'local' : 'LCL',
               'this' : 'THIS',
               'that' : 'THAT',
               # direct addressed
               'static' : f'{self._filename_base}.{index}',
               'temp' : str(5 + index),
               'pointer' : 'THIS' if index == 0 else 'THAT',
               # other
               'constant' : None # not used
        }[segment]

        if segment in ('static', 'pointer', 'temp'):
            if cmd_type == vm.CommandType.PUSH:
                self._push_addr(seg)
            else:
                self._pop_addr(seg)
        elif segment == 'constant' and cmd_type == vm.CommandType.PUSH:
            self._f.write(f'@{index}\nD=A\n@R13\nM=D\n')
            self._push_addr('R13')
        # rest: base addresses in LCL, ARG, THIS, THAT
        elif cmd_type == vm.CommandType.PUSH:
            self._f.write(
                f'@{seg}\nD=M\n@{index}\nA=A+D\nD=M\n' +
                '@SP\nM=M+1\nA=M-1\nM=D\n'
            )
        elif cmd_type == vm.CommandType.POP:
            self._f.write(
                f'@{seg}\nD=M\n@{index}\nD=D+A\n@R13\nM=D\n' +
                '@SP\nM=M-1\nA=M\nD=M\n' +
                '@R13\nA=M\nM=D\n'
            )
        else:
            print('ERROR - UNIMPLEMENTED')

    def write_label(self, label: str):
        """Translate a label command with the given label name.
        The label is scoped to its enclosing function."""
        full_label = self._curr_func + f'${label}'
        self._f.write(f'({full_label})\n')

    def write_goto(self, label: str):
        """Translate a goto command with the given label name.
        This instruction must be enclosed in the same function as
        the label definiton."""
        # unconditonal jump to the function-scoped label
        full_label = self._curr_func + f'${label}'
        self._f.write(f'@{full_label}\n0;JMP\n')

    def write_if_goto(self, label: str):
        """Translate an if-goto command with the given label name.
        This instruction must be enclosed in the same function as
        the label definiton."""
        # pop 1 value off stack. if != 0, jump
        full_label = self._curr_func + f'${label}'
        self._pop_addr('R13')
        self._f.write(f'@R13\nD=M\n@{full_label}\nD;JNE\n')

    def write_function(self, func_name: str, n_vars: int):
        """Translate a fuction command. 'func_name' is the fully
        qualified function name, e.g. 'Main.main'."""
        # update current function
        self._curr_func = func_name
        # (f)
        self._f.write(f'({func_name})\n')

        # push 0 (n_vars times)
        self._f.write('@R13\nM=0\n')
        for i in range(n_vars):
            self._push_addr('R13')

    def write_call(self, func_name: str, n_args: int):
        """Translate a call command. 'func_name' is the fully
        qualified function name, e.g. 'Main.main'."""
        ret_addr = self._curr_func + f'$ret.{self._label_cnt}'
        self._label_cnt += 1
        # push return address
        self._f.write(f'@{ret_addr}\nD=A\n@R13\nM=D\n')
        self._push_addr('R13')
        # push LCL, ARG, THIS, THAT
        self._push_addr('LCL')
        self._push_addr('ARG')
        self._push_addr('THIS')
        self._push_addr('THAT')
        # setup ARG for callee
        self._f.write(f'@SP\nD=M\n@{5 + n_args}\nD=D-A\n@ARG\nM=D\n')
        # setup LCL for callee
        self._f.write('@SP\nD=M\n@LCL\nM=D\n')
        # goto f
        self._f.write(f'@{func_name}\n0;JMP\n')
        # (return address)
        self._f.write(f'({ret_addr})\n')

    def write_return(self):
        """Translate a return command."""
        # store frame addr in R13
        self._f.write('@LCL\nD=M\n@R13\nM=D\n')
        # *ARG = pop()
        self._pop_addr('R15')
        self._f.write('@R15\nD=M\n@ARG\nA=M\nM=D\n')
        # SP = ARG + 1
        self._f.write('@ARG\nD=M\n@SP\nM=D+1\n')
        # THAT = *(frame-1)
        self._f.write('@R13\nD=M\n@1\nD=D-A\nA=D\nD=M\n@THAT\nM=D\n')
        # THIS = *(frame-2)
        self._f.write('@R13\nD=M\n@2\nD=D-A\nA=D\nD=M\n@THIS\nM=D\n')
        # ARG = *(frame-3)
        self._f.write('@R13\nD=M\n@3\nD=D-A\nA=D\nD=M\n@ARG\nM=D\n')
        # LCL = *(frame-4)
        self._f.write('@R13\nD=M\n@4\nD=D-A\nA=D\nD=M\n@LCL\nM=D\n')
        # goto ret addr at *(frame-5)
        self._f.write('@R13\nD=M\n@5\nD=D-A\nA=D\nA=M\n0;JMP\n')

    def close(self):
        """Closes the output file."""
        self._f.close()

    def write_infinite_loop(self):
        """Write an infinite loop."""
        self._f.write('(__INF_LOOP)\n@__INF_LOOP\n0;JMP\n')

    def write_verbatim(self, s: str):
        """Write the input string as a verbait assembly command.
        Useful for inserting comments."""
        self._f.write(f'{s}\n')

    # private methods
    def _push_addr(self, addr):
        # RAM[SP++] = RAM[addr]
        self._f.write(f'@{addr}\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n')

    def _pop_addr(self, addr):
        # RAM[addr] = RAM[sp--]
        self._f.write(f'@SP\nM=M-1\nA=M\nD=M\n@{addr}\nM=D\n')

    def _cmp(self, jump_instr: str):
        # compare the top 2 stack values. 'jump_instr' should be an explicit 
        # jump instruction using D, e.g. 'D;JEQ'
        self._pop_addr('R13')
        self._pop_addr('R14')
        self._f.write(
            f'@R13\nD=M\n@R14\nM=M-D\nD=M\nM=-1\n@_VM_CMP_{self._label_cnt}\n' +
            f'{jump_instr}\n@R14\nM=0\n(_VM_CMP_{self._label_cnt})\n'
        )
        self._push_addr('R14')
        self._label_cnt += 1

