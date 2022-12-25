import vm_constants as vm

class Parser:
    """Parser for the Jack VM standard implementation.

    Instantiate a Parser on a filepath for some .vm file to begin parsing
    one line at a time. Whitespace, comments, and empty lines are ignored.

    Example usage:
        p = Parser('my/Prog.vm')
        while(p.has_more_lines()):
            print(p.arg_1())
            p.advance()
    """

    def __init__(self, filepath: str):
        """Open a VM program for parsing. Starts at logical line index -1."""
        with open(filepath, 'r', encoding=None) as f:
            self._lines = [line.replace('\n', '') for line in f]

        # remove comments and empty lines
        self._lines = list(filter(lambda x: x != '' and x[:2] != '//', self._lines))

        self._idx = -1
        self._tokens = []

    def has_more_lines(self) -> bool:
        """Returns True if there are more lines after the current line."""
        return self._idx + 1 < len(self._lines)

    def advance(self):
        """Advance to the next line."""
        self._idx += 1
        # break line into tokens
        self._tokens = self._lines[self._idx].split(' ')

    def command_type(self) -> vm.CommandType:
        """Return the CommandType of the current line."""
        if len(self._tokens) == 1:
            return vm.CommandType.ARITHMETIC
        elif self._tokens[0] == 'push':
            return vm.CommandType.PUSH
        elif self._tokens[0] == 'pop':
            return vm.CommandType.POP

    def arg_1(self) -> str:
        """Return the first argument of the command on the current line.
        Arithmetic commands are special: the first argument is the operation
        itself, e.g. 'add'.
        """
        if self.command_type() == vm.CommandType.ARITHMETIC:
            return self._tokens[0]
        else:
            return self._tokens[1]

    def arg_2(self) -> int:
        """Return the second argument of the command on the current line."""
        return self._tokens[2]

    # debug
    def _current_line(self):
        return ' '.join(self._tokens)

