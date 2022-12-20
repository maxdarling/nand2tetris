#!/usr/bin/python3
import sys
import parser
import decoder
import symbol_table

def assemble(filepath: str):
    """Assemble a given .asm file 'filepath' into its .hack binary

    For a filepath 'my/file/path.asm', the binary will be 'my/file/path.hack'

    Assembler source is assumed to be error-free. No error checking is provided.
    """
    result = [] # lines of output
    p = parser.Parser(sys.argv[1])
    st = symbol_table.SymbolTable()
    next_var_addr = 16

    # first pass: populate symbol table with label declarations
    line_num = 0
    while True:
        instr_type = p.instruction_type()
        if instr_type == 'L_INSTRUCTION':
            st.add_entry(p.symbol(), line_num)
        else:
            line_num += 1
        
        if not p.has_more_lines():
            break
        p.advance()

    # second pass: translate
    p.reset()
    while True:
        instr_type = p.instruction_type()
        if instr_type == 'C_INSTRUCTION':
            dest = decoder.dest(p.dest());
            comp = decoder.comp(p.comp());
            jump = decoder.jump(p.jump());
            # format: '111accccccdddjjj'
            result.append('111' + comp + dest + jump);
        elif instr_type == 'A_INSTRUCTION':
            if p.symbol().isdigit():
                dec = int(p.symbol())
                result.append("{0:016b}".format(dec))
            else:
                if not st.contains(p.symbol()):
                    st.add_entry(p.symbol(), next_var_addr)
                    next_var_addr += 1
                addr = st.get_address(p.symbol())
                result.append("{0:016b}".format(addr))

        if not p.has_more_lines():
            break
        p.advance()

    # write output file
    outpath = filepath[:-3] + 'hack'
    with open(outpath, 'w', encoding=None) as f:
        for line in result:
            f.write(f"{line}\n")


if __name__ == '__main__':
    assemble(sys.argv[1])

