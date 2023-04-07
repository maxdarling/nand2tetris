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
        self.idx = -1

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
                # string constant (keep surrounding quotes)
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
                    i += match.end(0)
                    break
            
            # couldn't match anything -> exit
            if not match:
                break

        # sanity check - did we scan the whole file?
        assert(len(self.rawfile[i:]) == 0)


    def hasMoreTokens(self) -> bool:
        """Are there more tokens in the input, including the current one?"""
        return len(self.tokens) != 0 and self.idx < len(self.tokens)

    def advance(self):
        """Move to the next token. Initially there is no current
        token."""
        if not self.hasMoreTokens():
            raise Exception("Can't advance: no more tokens!")
        self.idx += 1

    def getTokenType(self) -> TokenType:
        """Return the type of the current token."""
        t = self.tokens[self.idx]
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

    def getToken(self) -> str:
        """Return the current token as a string. Note: string constants have
        their surrounding quotes omitted."""
        if self.getTokenType() == TokenType.STRING_CONST:
            # strip quotation marks.
            return self.tokens[self.idx][1:-1]
        return self.tokens[self.idx]
