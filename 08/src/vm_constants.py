from enum import Enum

class CommandType(Enum):
    """All possible command types for the Jack standard VM."""
    ARITHMETIC = 1
    PUSH = 2
    POP = 3
    LABEL = 4
    GOTO = 5
    IF_GOTO = 6
    FUNCTION = 7
    RETURN = 8
    CALL = 9
    UNKNOWN = 10

