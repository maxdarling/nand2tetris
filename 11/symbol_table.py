from typing import NamedTuple
from jack_constants import VarKind


class SymbolInfo(NamedTuple):
    name: str
    type: str
    kind: VarKind
    index: int

class SymbolTable():
    """A symbol table for parsing the Jack language.
    Usage:
        st = SymbolTable()
        st.define('count', 'int', 'arg')
        st.define('arr', 'Array', 'var')
        st.define('i', 'int', 'var')

        # resulting table:
        +-------+-------+------+-------+
        | name  | type  | kind | index |
        +-------+-------+------+-------+
        | count | int   | arg  |     0 |
        | arr   | Array | var  |     0 |
        | i     | int   | var  |     1 |
        +-------+-------+------+-------+
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Empty the symbol table."""
        self._d = {}
        self._kind_counts = {k: 0 for k in VarKind}

    def define(self, name: str, type: str, kind: VarKind):
        """Define a new variable with a given name, type, and 'VarKind', and
        assigns it the next index in its kind. Indexes start at 0."""
        idx = self._kind_counts[kind]
        self._kind_counts[kind] += 1
        self._d[name] = SymbolInfo(name, type, kind, idx)

    def var_count(self, kind: VarKind) -> int:
        """Return the # of variables stored for the given kind."""
        return self._kind_counts[kind]

    def has_symbol(self, name: str) -> bool:
        """Return true if symbol exists in the table."""
        return name in self._d

    def get_symbol_info(self, name: str) -> SymbolInfo:
        """Return the table's representation for a given identifer."""
        return self._d[name]
