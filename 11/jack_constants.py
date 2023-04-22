from enum import Enum, StrEnum

# Jack
class VarKind(Enum):
    STATIC = 1
    FIELD = 2
    ARG = 3
    VAR = 4

# VM
class VMArithmetic(StrEnum):
    ADD = 'add'
    SUB = 'sub'
    NEG = 'neg'
    EQ = 'eq'
    GT = 'gt'
    LT = 'lt'
    AND = 'and'
    NOT = 'not'
    OR = 'or'

class VMSegment(StrEnum):
    CONSTANT = 'constant'
    ARGUMENT = 'argument'
    LOCAL = 'local'
    STATIC = 'static'
    THIS = 'this'
    THAT = 'that'
    POINTER = 'pointer'
    TEMP = 'temp'
