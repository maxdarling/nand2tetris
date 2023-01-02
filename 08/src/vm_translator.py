import sys
import os
import vm_constants as vm
import parser
import code_writer

def translate(source: str):
    """VM translator for the Jack VM to Hack assembly.

    Given a path 'source' to a .vm file or folder of .vm files, writes the Hack assembly translation of
    all functions in all encompassed .vm files one after another to an output file as such:
    - [single file]: my/Prog.vm -> my/Prog.asm
    - [directory]: my/Project -> my/Project/Project.asm

    As above, the source base name should be uppercase (and end in '.vm' if it's a file).

    The final translated program is terminated with an infinite loop, per the Hack asm guidelines.
    """
    files = []
    outpath = None
    if os.path.isfile(source):
        files = [source]
        outpath = source[:-2] + 'asm'
    else:
        source = source[:-1] if source[-1] == '/' else source
        outpath = f'{source}/{os.path.basename(source)}.asm'
        with os.scandir(source) as it:
            for entry in it:
                if entry.name.endswith('.vm'):
                    files.append(entry.path)

    cw = code_writer.CodeWriter(outpath)

    for file in files:
        p = parser.Parser(file)
        cw.set_vm_filename(file)

        while(p.has_more_lines()):
            p.advance()
            cw.write_verbatim(f'// {p.get_current_line()}') # comment for clarity
            cmd_type = p.command_type()
            if cmd_type == vm.CommandType.ARITHMETIC:
                cw.write_arithmetic(p.arg_1())
            elif cmd_type in (vm.CommandType.PUSH, vm.CommandType.POP):
                cw.write_push_pop(cmd_type, p.arg_1(), int(p.arg_2()))
            elif cmd_type == vm.CommandType.LABEL:
                cw.write_label(p.arg_1())
            elif cmd_type == vm.CommandType.GOTO:
                cw.write_goto(p.arg_1())
            elif cmd_type == vm.CommandType.IF_GOTO:
                cw.write_if_goto(p.arg_1())
            elif cmd_type == vm.CommandType.FUNCTION:
                cw.write_function(p.arg_1(), int(p.arg_2()))
            elif cmd_type == vm.CommandType.CALL:
                cw.write_call(p.arg_1(), int(p.arg_2()))
            elif cmd_type == vm.CommandType.RETURN:
                cw.write_return()
            else:
                print("ERROR - UNKNOWN VM COMMAND")


    cw.write_verbatim('// infinite loop')
    cw.write_infinite_loop()
    cw.close()

if __name__ == '__main__':
    translate(sys.argv[1])

