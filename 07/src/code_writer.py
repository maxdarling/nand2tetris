import vm_constants as vm

class CodeWriter:
    """Translates parsed VM commands into Hack assembly.

    Output is written sequentially to the specified filepath.
    Remember to eventually close the file via the provided facility.

    Example usage:
        cw = CodeWriter('out/Prog.asm')
        cw.writePushPop(vm.CommandType.PUSH, 'local', 0)
        cw.writePushPop(vm.CommandType.PUSH, 'constant', 1)
        cw.writeArithmetic('add')
        cw.writePushPop(vm.CommandType.POP, 'local', 0)
    """

    def __init__(self, filepath: str):
        self._f = open(filepath, 'w', encoding=None)
        # for static var naming
        slash_idx = filepath.rfind('/')
        start = slash_idx + 1 if slash_idx != -1 else None
        self._filename_base = filepath[start:-4]
        # for jump labels
        self._jump_cnt = 0

    def _write_verbatim(self, s: str):
        self._f.write(f'{s}\n')

    def _push_addr(self, addr):
        # RAM[SP++] = RAM[addr]
        self._f.write(f'@{addr}\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n')

    def _pop_addr(self, addr):
        # RAM[addr] = RAM[sp--]
        self._f.write(f'@SP\nM=M-1\nA=M\nD=M\n@{addr}\nM=D\n')

    def _cmp(self, jump_instr: str):
        # 2-value comparison. 'jump_instr' should be an explicit 
        # jump instruction using D, e.g. 'D;JEQ'
        self._pop_addr('R13')
        self._pop_addr('R14')
        self._f.write(
            f'@R13\nD=M\n@R14\nM=M-D\nD=M\nM=-1\n@_VM_CMP_{self._jump_cnt}\n' +
            f'{jump_instr}\n@R14\nM=0\n(_VM_CMP_{self._jump_cnt})\n'
        )
        self._push_addr('R14')
        self._jump_cnt += 1

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
            print('ERROR - invalid command')

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

    def close(self):
        """Closes the output file."""
        self._f.close()

    def write_infinite_loop(self):
        """Write an infinite loop."""
        self._f.write('(__INF_LOOP)\n@__INF_LOOP\n0;JMP\n')

