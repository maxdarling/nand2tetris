import sys
import vm_constants as vm
import parser
import code_writer

def translate(filepath: str):
    """VM translator for the Jack VM to Hack assembly.

    Given a file 'my/Prog.vm', writes a functionally equivalent hack assembly program to 'my/Prog.asm'.
    The filename must start with an uppercase letter and have the .vm extension.

    Programs are terminated with infinite loops, per the Hack asm guidelines.
    """
    p = parser.Parser(filepath)
    outpath = filepath[:-2] + 'asm'
    cw = code_writer.CodeWriter(outpath)

    while(p.has_more_lines()):
        p.advance()
        cw._write_verbatim(f'// {p._current_line()}') # comment for clarity
        cmd_type = p.command_type()
        if cmd_type == vm.CommandType.ARITHMETIC:
            cw.write_arithmetic(p.arg_1())
        elif cmd_type in (vm.CommandType.PUSH, vm.CommandType.POP):
            cw.write_push_pop(cmd_type, p.arg_1(), int(p.arg_2()))
        else:
            print("ERROR - UNIMPLEMENTED")


    cw._write_verbatim('// infinite loop')
    cw.write_infinite_loop()
    cw.close()

if __name__ == '__main__':
    translate(sys.argv[1])

