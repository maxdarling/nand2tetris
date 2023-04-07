from enum import Enum
import re

class TokenType(Enum):
    KEYWORD = 1
    SYMBOL = 2
    IDENTIFIER = 3
    INT_CONST = 4
    STRING_CONST = 5


class JackTokenizer():
    """given an input file, tokenize it and provide basic accessor methods
    according to the Jack language syntax."""

    KEYWORDS = {
        'class', 'method', 'function', 'constructor', 'int', 'boolean', 'char',
        'void', 'var', 'static', 'field', 'let', 'do', 'if', 'else', 'while',
        'return', 'true', 'false', 'null', 'this',
    }
    SYMBOLS = { 
        '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&',
        '|', '<', '>', '=', '~'
    }

    def __init__(self, infile):
        self.curr = -1

        with open (infile, 'r') as f:
            self.rawfile = f.read()

        # remove comments
        self.rawfile = re.sub(r"/\*(\*)?.*?\*/", '', self.rawfile, flags=re.DOTALL) # DOTALL for multi-line
        self.rawfile = re.sub(r"//.*", '', self.rawfile)
        # remove newline stuff (assumes these aren't allowed in string literals...which is right.)
        self.rawfile = re.sub(r"(\n|\t|\r)", '', self.rawfile)
        # trim whitespace
        self.rawfile = self.rawfile.strip()

        # tokenization algorithm: iteratively match regexes for tokens while skipping whitespace.
        self.tokens = []
        i = 0
        while True:
            # escape symbols 
            symbolcopy = [s for s in self.SYMBOLS] 
            symbolcopy.remove(']')
            symbolcopy.append('\]')
            symbolcopy.remove('-')
            symbolcopy.append('\-')

            regexes = [
                # string constant (preserve surrounding quotes)
                r"\s*(\".*?\")",
                # integer constant
                r"\s*(\d+)",
                # symbols
                rf"\s*([{''.join(symbolcopy)}])",
                # keyword / identifier
                r"\s*([a-zA-Z_][a-zA-Z_0-9]*)",
            ]
            match = None
            for regex in regexes:
                match = re.match(regex, self.rawfile[i:])
                if match:
                    self.tokens.append(match.group(1))
                    i += match.end(1)
                    break
            
            # couldn't match anything -> exit
            if not match:
                break

        # sanity check - did we scan the whole file?
        assert(len(self.rawfile[i:]) == 0)


    def hasMoreTokens(self) -> bool:
        """Are there more tokens in the input?"""
        return len(self.tokens) != 0 and self.curr < len(self.tokens)

    def advance(self):
        """Move to the next token. Initially there is no current
        token."""
        self.curr += 1

    def tokenType(self) -> TokenType:
        """Return the type of the current token."""
        t = self.tokens[self.curr]
        if t in self.SYMBOLS:
            return TokenType.SYMBOL
        elif t in self.KEYWORDS:
            return TokenType.KEYWORD
        elif t[0] == '"':
            return TokenType.STRING_CONST
        elif t[0].isdigit():
            return TokenType.INT_CONST
        else:
            return TokenType.IDENTIFIER

    def keyword(self) -> str:
        """When the current token is a keyword, return its value.""" 
        return self.tokens[self.curr]

    def symbol(self) -> str:
        """When the current token is a symbol, return its value."""
        return self.tokens[self.curr]

    def identifier(self) -> str:
        """When the current token is an identifier, return its value."""
        return self.tokens[self.curr]

    def intVal(self) -> int:
        """When the current token is an integer constant, return its value."""
        return self.tokens[self.curr]

    def stringVal(self) -> str:
        """When current token is a string constant, return its value without
        the surrounding double quotes."""
        return self.tokens[self.curr][1:-1]
