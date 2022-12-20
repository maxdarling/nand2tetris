class SymbolTable:
    """Symbol table for the Hack assembler.

    Supports basic dictionary operations on <str, int> pairs 
    representing symbols and their decimal addresses.
    
    Many builtin symbols are supported as well, like 'R0', 'THIS', etc.

    Example usage:
        st = SymbolTable()
        st.get_address('R15') # 15
        st.contains('R16') # False
        st.add_entry('sum', 16)
        st.get_address('sum') # 16
    """

    def __init__(self):
        self._d = {'R0' : 0,
                   'R1' : 1,
                   'R2' : 2,
                   'R3' : 3,
                   'R4' : 4,
                   'R5' : 5,
                   'R6' : 6,
                   'R7' : 7,
                   'R8' : 8,
                   'R9' : 9,
                   'R10' : 10,
                   'R11' : 11,
                   'R12' : 12,
                   'R13' : 13,
                   'R14' : 14,
                   'R15' : 15,
                   'SP' : 0,
                   'LCL' : 1,
                   'ARG' : 2,
                   'THIS' : 3,
                   'THAT' : 4,
                   'SCREEN' : 16384,
                   'KBD' : 24576
        }

    def get_address(self, symbol: str) -> int:
        return self._d[symbol]

    def contains(self, symbol: str) -> bool:
        return symbol in self._d

    def add_entry(self, symbol: str, address: int):
        self._d[symbol] = address

