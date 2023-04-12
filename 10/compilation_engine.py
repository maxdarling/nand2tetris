from tokenizer import JackTokenizer, TokenType

# test order -> no expressions / arrays -> impl expressions -> impl arrays

class CompilationEngine():
    """Given a Jack file, generate a parse tree and write it to the specified
    filepath in the XML format specified in the ch10 spec.

    As Jack is an LL(1) language, a simple recurisve descent parser is used.

    Usage:
        engine = CompilationEngine('my/Program.Jack', 'some/file.xml')
        engine.compile()
    """

    def __init__(self, infile, outfile) -> None:
        self.t = JackTokenizer(infile)
        self.t.advance() # prepare the first token
        self.f = open(outfile, 'w')

    def compile(self):
        """Compile a Jack file."""
        self._compileClass()
        self.f.close()

    # ~~ private methods ~~
    def _process(self, token):
        """Asserts that the supplied token matches the current token, writes
        the correctly formatted output, and prepares the next token."""
        if not self.t.hasMoreTokens():
            raise SyntaxError(f"Ran out of tokens; cannot match next logical token {token}")
        if self.t.getToken() != token:
            raise SyntaxError(f"Next logical token {token} doesn't match actual token {self.t.getToken()}") 
        
        symbol_conv = { '<' : '&lt;', '>' : '&gt;', '"' : '&quot;', '&' : '&amp;'}
        if token in symbol_conv:
            token = symbol_conv[token]
        type_str = { 
            TokenType.KEYWORD: 'keyword', TokenType.IDENTIFIER: 'identifier',
            TokenType.INT_CONST: 'integerConstant', TokenType.STRING_CONST: 'stringConstant',
            TokenType.SYMBOL: 'symbol',
        }[self.t.getTokenType()]
        self._writeLine(f"<{type_str}> {token} </{type_str}>")

        self.t.advance()

    def _processType(self, token_type: TokenType):
        """Like 'process', but for an unspecified token of a given type."""
        if self.t.getTokenType() != token_type:
            raise SyntaxError(f"Expected a token of type {token_type} but got {self.t.getTokenType()}")

        self._process(self.t.getToken())

    def _processOneOf(self, possible_tokens: list[TokenType]):
        """Like 'process', but matches the first token from the supplied list."""
        for token in possible_tokens:
            try:
                self._process(token)
                return
            except Exception:
                pass
        
        raise SyntaxError(f"Possible next tokens {possible_tokens} didn't match the current token {self.t.getToken()}")

    def _writeLine(self, s):
        """Write string 's' to the output file."""
        self.f.write(f"{s}\n")

    def _compileClass(self):
        self._writeLine("<class>")        
        # 'class' className '{' classVarDec* subroutineDec* '}'
        self._process("class")
        self._processType(TokenType.IDENTIFIER)
        self._process("{")
        while self.t.getToken() in {'static', 'field'}:
            self._compileClassVarDec()
        while self.t.getToken() in {'constructor', 'function', 'method'}:
            self._compileSubroutine()
        self._process("}")
        self._writeLine("</class>")        

    def _compileClassVarDec(self):
        self._writeLine("<classVarDec>")
        # ('static' | 'field') type varName (',' varName)* ';'
        self._processOneOf(['static', 'field'])
        self._compileType()
        self._processType(TokenType.IDENTIFIER)
        while self.t.getToken() == ',':
            self._process(',')
            self._processType(TokenType.IDENTIFIER)

        self._process(';')
        self._writeLine("</classVarDec>")

    def _compileSubroutine(self):
        self._writeLine("<subroutineDec>")
        # ('constructor'|'function'|'method') ('void'|type) subroutineName
        # '( parameterList ')' subroutineBody
        self._processOneOf(['constructor', 'function', 'method'])
        if self.t.getToken() == 'void':
            self._process('void')
        else:
            self._compileType()

        self._processType(TokenType.IDENTIFIER)
        self._process('(')
        self._compileParameterList()
        self._process(')')
        self._compileSubroutineBody()
        self._writeLine("</subroutineDec>")

    def _compileParameterList(self):
        self._writeLine("<parameterList>")
        # ((type varName)(,type varName)*)?
        skip_comma = True
        while self.t.getToken() != ')':
            if not skip_comma: 
                self._process(',')
            skip_comma = False
            self._compileType()
            self._processType(TokenType.IDENTIFIER)
        self._writeLine("</parameterList>")

    def _compileSubroutineBody(self):
        self._writeLine("<subroutineBody>")
        # '{' varDec* statements '}'
        self._process('{')
        while self.t.getToken() == 'var':
            self._compileVarDec()
        self._compileStatements()
        self._process('}')
        self._writeLine("</subroutineBody>")

    def _compileVarDec(self):
        """Compiles a 'var' declaration."""
        self._writeLine("<varDec>")
        # 'var' type varName (, varName)* ';'
        self._process('var')
        self._compileType()
        self._processType(TokenType.IDENTIFIER)
        while self.t.getToken() == ',':
            self._process(',')
            self._processType(TokenType.IDENTIFIER)
        self._process(';')
        self._writeLine("</varDec>")
        
    def _compileStatements(self):
        self._writeLine("<statements>")
        # (letStatement | ifStatement | whileStatement | doStatement | returnStatement)*
        while True:
            match self.t.getToken():
                case 'let':
                    self._compileLet()
                case 'if':
                    self._compileIf()
                case 'while':
                    self._compileWhile()
                case 'do':
                    self._compileDo()
                case 'return':
                    self._compileReturn()
                case _:
                    break
        self._writeLine("</statements>")

    def _compileLet(self):
        self._writeLine("<letStatement>")
        # 'let' varName ('[' expression ']')? '=' expression ';'
        self._process("let")
        self._processType(TokenType.IDENTIFIER)
        if self.t.getToken() == '[':
            self._process('[')
            self._compileExpression()
            self._process(']')
        self._process('=')
        self._compileExpression()
        self._process(';')
        self._writeLine("</letStatement>")
        
    def _compileIf(self):
        self._writeLine("<ifStatement>")
        # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        self._process('if')
        self._process('(')
        self._compileExpression()
        self._process(')')
        self._process('{')
        self._compileStatements()
        self._process('}')
        if self.t.getToken() == 'else':
            self._process('else')
            self._process('{')
            self._compileStatements()
            self._process('}')
        self._writeLine("</ifStatement>")

    def _compileWhile(self):
        self._writeLine("<whileStatement>")
        # 'while' '(' expression ')' '{' statements '}'
        self._process('while')
        self._process('(')
        self._compileExpression()
        self._process(')')
        self._process('{')
        self._compileStatements()
        self._process('}')
        self._writeLine("</whileStatement>")

    def _compileDo(self):
        self._writeLine("<doStatement>")
        # 'do' subroutineCall ';'
        self._process('do')
        # 'subroutineCall' is folded into 'term' to isolate the implementation
        # of +1 lookahead to just one spot.
        self._compileTerm(omitTags=True)
        self._process(';')
        self._writeLine("</doStatement>")

    def _compileReturn(self):
        self._writeLine("<returnStatement>")
        # 'return' expression? ';'
        self._process('return')
        if self.t.getToken() != ';':
            self._compileExpression()
        self._process(';')
        self._writeLine("</returnStatement>")

    def _compileExpression(self):
        self._writeLine("<expression>")
        # term (op term)*
        self._compileTerm()
        while self.t.getToken() in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:
            self._processType(TokenType.SYMBOL)
            self._compileTerm()
        self._writeLine("</expression>")

    def _compileTerm(self, omitTags = False):
        """Compiles a term. If the current token is an identifier, it must be
        resolved into a variable, array element, or subroutine call. A single
        lookahead token, which may be '[', '(', or '.', suffices to distinguish
        between the possibilities.  Any other token is not part of this term and
        should not be advanced over."""
        if not omitTags: self._writeLine("<term>")
        # integerConstant | stringConstant | keywordConstant | varName |
        # varName'[' expression ']' | '(' expression ')' | (unaryOp term) |
        # subroutineName '(' expressionList ')' | 
        # (className | varName) '.' subroutineName '(' expressionList ')'
        token_type = self.t.getTokenType()
        token = self.t.getToken()

        if token_type in { TokenType.INT_CONST, TokenType.STRING_CONST, TokenType.KEYWORD }:
            self._process(token)
        elif token in { '-', '~' }: # unaryOp
            self._process(token)
            self._compileTerm()
        elif token == '(':
            self._process('(')
            self._compileExpression()
            self._process(')')
        elif token_type == TokenType.IDENTIFIER:
            # must lookahead. special-case code! but not too bad - all
            # lookahead cases start with an identifier, so no need to do
            # backtracking.
            self._process(token)
            next_token = self.t.getToken()
            if next_token == '[':
                self._process('[')
                self._compileExpression()
                self._process(']')
            elif next_token == '(':
                self._process('(')
                self._compileExpressionList()
                self._process(')')
            elif next_token == '.':
                self._process('.')
                self._processType(TokenType.IDENTIFIER)
                self._process('(')
                self._compileExpressionList()
                self._process(')')
            else:
                # it was just a varName. Nothing more to process.
                pass
        else:
            raise SyntaxError("Unresolved symbol {token} in term expression.")
            
        if not omitTags: self._writeLine("</term>")

    def _compileExpressionList(self):
        # (expression (',' expression)*)?
        self._writeLine("<expressionList>")
        skip_comma = True
        while self.t.getToken() != ')':
            if not skip_comma: 
                self._process(',')
            skip_comma = False
            self._compileExpression()
        self._writeLine("</expressionList>")

    def _compileType(self):
        """Compile a type."""
        # type: (int | char | boolean | className)
        if self.t.getTokenType() == TokenType.IDENTIFIER:
            self._processType(TokenType.IDENTIFIER) 
        else:
            self._processOneOf(['int', 'char', 'boolean'])
