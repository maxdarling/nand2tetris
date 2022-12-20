import re

class Parser:
    """Parser for Hack assembly langauge.

    Initializing a parser will open the specified filename for parsing,
    starting at the first line of a Hack assembly file. The available
    methods allow for gaining information about the current line and
    advancing to the next line. Comments and blank lines are ignored.

    Example usage:
       parser = Parser('path/to/file.asm') # file contents: @hello
       parser.has_more_lines() # True
       parser.instruction_type() # 'A_INSTRUCTION'
       parser.symbol() # 'hello'
       parser.advance()
       parser.has_more_lines() # False
    """

    def __init__(self, filename: str):
        with open(filename, 'r', encoding=None) as f:
            self._lines = [line for line in f]

        # trim whitespace and newlines.
        self._lines = [line.replace(' ', '').replace('\n', '') for line in self._lines]
        # remove comments, including in-line comments
        tmp = []
        for line in self._lines:
            idx = line.find('//')
            tmp.append(line[:idx if idx != -1 else None])
        self._lines = tmp
        # remove empty lines
        self._lines = list(filter(lambda x: x != '', self._lines))

        self.reset()
    
    def has_more_lines(self) -> bool:
        """True if the current line isn't the last line."""
        return self._curr_line < len(self._lines) - 1

    def advance(self):
        """Move ahead 1 line in the file."""
        self._curr_line += 1
        self._current_line = self._lines[self._curr_line]
        self._eq_idx = self._current_line.find('=')
        self._colon_idx = self._current_line.find(';')

    def reset(self):
        """Move to the first line in the file"""
        self._curr_line = -1
        self.advance()

    def instruction_type(self) -> str:
        """The type of the current instruction.

        Returns one of: {'A_INSTRUCTION', 'C_INSTRUCTION', 'L_INSTRUCTION'}
        """
        if self._current_line[0] == '@':
            return 'A_INSTRUCTION'
        elif self._current_line[0] == '(':
            return 'L_INSTRUCTION'
        else:
            return 'C_INSTRUCTION'

    def symbol(self) -> str:
        """Returns xxx if the current line is '@xxx' or '(xxx)'."""
        if self._current_line[0] == '@':
            return self._current_line[1:]
        else:
            return self._current_line[1:-1]

    def dest(self) -> str:
        """Returns the symbolic 'dest' part of the current C-instruction."""
        return self._current_line[:self._eq_idx] if self._eq_idx != -1 else ''

    def comp(self) -> str:
        """Returns the symbolic 'comp' part of the current C-instruction."""
        start = self._eq_idx + 1 if self._eq_idx != -1 else 0
        end = self._colon_idx if self._colon_idx != -1 else None
        return self._current_line[start:end]

    def jump(self) ->str:
        """Returns the symbolic 'jump' part of the current C-instruction."""
        return self._current_line[self._colon_idx+1:] if self._colon_idx != -1 else ''

