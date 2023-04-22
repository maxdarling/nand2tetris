from tokenizer import JackTokenizer, TokenType
from symbol_table import SymbolTable, SymbolInfo
from vm_writer import VMWriter
from jack_constants import VarKind, VMArithmetic, VMSegment

class CompilationEngine():
    """Compiler for the Jack language from the "nand2tetris" course.
    Compiles a given Jack file to Jack VM bytecode.

    Usage:
        engine = CompilationEngine('my/Program.Jack', 'some/file.vm')
        engine.compile()

    As Jack is an LL(1) language, a simple recurisve descent parser
    without backtracking is sufficiently powerful.

    Resources from the free textbook ("The Elements Of Computing Systems"):
    - VM spec - sec. 7.3 and 8.4
    - Jack language spec - fig. 9.6
    - Jack grammar - fig. 10.5
    - Jack standard mapping - sec. 11.3.1
    - Discussion of the simplifications in the Jack language design - sec. 11.5

    Future extension ideas:
    - operator precendence
    - 'this.x' access for fields and methods

    Implementation thoughts:
    - I kept the symbol table very dumb. I decided to keep it unaware of the mapping
    between Jack variable kinds (var, field, etc.) and the appropriate corresponding VM
    segments (local, this, etc.). I decided that that mapping is an important
    implementation choice of the compiler, so it should live in the compiler. Then it
    follows that the symbol table is just a utility with an awareness of Jack only,
    not the VM. I think this respects "separation of concerns". The downside, though,
    is that the symbol table class is pretty shallow.
    """

    def __init__(self, infile, outfile) -> None:
        self._writer = VMWriter(outfile)

        self._t = JackTokenizer(infile)
        self._t.advance() # prepare the first token

        self._class_table = SymbolTable()
        self._subroutine_table = SymbolTable()

        self._class_name = None # e.g. 'Main'
        self._label_count = 0


    def compile(self):
        """Compile a Jack file."""
        self._compile_class()
        self._writer.close()


    # ~~ helper methods ~~
    def _resolve_symbol(self, identifier: str) -> tuple[SymbolInfo, VMSegment]:
        """Given an identifier, gets its symbol table info and VM segment.
        Try the subroutine table first.
        If the symbol isn't found in either table, raise a KeyError."""
        kind_to_seg_mapping = { VarKind.ARG: VMSegment.ARGUMENT,
                                VarKind.FIELD: VMSegment.THIS,
                                VarKind.STATIC: VMSegment.STATIC,
                                VarKind.VAR: VMSegment.LOCAL }
        info = (
            self._subroutine_table.get_symbol_info(identifier)
            if self._subroutine_table.has_symbol(identifier)
            else self._class_table.get_symbol_info(identifier)
        )
        return (info, kind_to_seg_mapping[info.kind])


    def _process(self, token) -> str:
        """Asserts that the supplied token matches the current token, and
        prepares the next token. Also returns the matched token for
        convenience."""
        if not self._t.has_more_tokens():
            raise SyntaxError(f"Ran out of tokens; cannot match next logical token {token}")
        if self._t.get_token() != token:
            raise SyntaxError(f"Next logical token {token} doesn't" +
                              f"match actual token {self._t.get_token()}")

        self._t.advance()
        return token


    def _process_type(self, token_type: TokenType):
        """Like 'process', but for an unspecified token of a given type."""
        if self._t.get_token_type() != token_type:
            raise SyntaxError(f"Expected a token of type {token_type}" +
                              f"but got {self._t.get_token_type()}")

        return self._process(self._t.get_token())


    def _process_one_of(self, possible_tokens: list[str]) -> str:
        """Like 'process', but matches the first token from the supplied list."""
        for token in possible_tokens:
            try:
                return self._process(token)
            except Exception:
                pass

        raise SyntaxError(f"Possible next tokens {possible_tokens} " +
                          f"didn't match the current token {self._t.get_token()}")


    # ~ private methods ~
    def _compile_class(self):
        # grammar: 'class' className '{' classVarDec* subroutineDec* '}'
        # codegen: n/a. set the class name.
        self._process("class")
        self._class_name = self._process_type(TokenType.IDENTIFIER)
        self._process("{")
        while self._t.get_token() in {'static', 'field'}:
            self._compile_class_var_dec()
        while self._t.get_token() in {'constructor', 'function', 'method'}:
            self._compile_subroutine()
        self._process("}")


    def _compile_class_var_dec(self):
        # grammar: ('static' | 'field') type varName (',' varName)* ';'
        # codegen: n/a. setup the class symbol table.
        kind = {
            'static': VarKind.STATIC,
            'field': VarKind.FIELD
        }[self._process_one_of(['static', 'field'])]
        type = self._compile_type()
        while True:
            identifier = self._process_type(TokenType.IDENTIFIER)
            self._class_table.define(identifier, type, kind)
            if self._t.get_token() != ',':
                break
            self._process(',')

        self._process(';')


    def _compile_subroutine(self):
        # grammar:
        # ('constructor'|'function'|'method') ('void'|type) subroutineName
        # '( parameterList ')' subroutineBody
        #
        # codegen: generate a function. if it's a 'method', the caller must
        # specially push the object reference as the first argument.
        self._subroutine_table.reset()

        subroutine_type = self._process_one_of(['constructor', 'function', 'method'])

        if subroutine_type == 'method':
            self._subroutine_table.define('this', self._class_name, VarKind.ARG)

        if self._t.get_token() == 'void':
            self._process('void')
        else:
            self._compile_type()

        func_name = self._process_type(TokenType.IDENTIFIER)

        self._process('(')
        self._compile_parameter_list()
        self._process(')')

        # subroutineBody <-> '{' varDec* statements '}'
        self._process('{')
        while self._t.get_token() == 'var':
            self._compile_var_dec()

        # after var decs, we know the # of variables.
        n_vars = self._subroutine_table.var_count(VarKind.VAR)
        self._writer.write_function(f"{self._class_name}.{func_name}", n_vars)

        # constructor allocates memory and sets 'this'
        if subroutine_type == 'constructor':
            n_fields = self._class_table.var_count(VarKind.FIELD)
            self._writer.write_push(VMSegment.CONSTANT, n_fields)
            self._writer.write_call("Memory.alloc", 1)
            self._writer.write_pop(VMSegment.POINTER, 0)

        # method sets up 'this' that was pushed specially by the caller.
        if subroutine_type =='method':
            self._writer.write_push(VMSegment.ARGUMENT, 0)
            self._writer.write_pop(VMSegment.POINTER, 0)

        self._compile_statements()
        # note: Jack requires constructors to end with 'return this'.
        # 'compileTerm' knows to map this to 'push pointer 0', so nothing to do
        # here.
        self._process('}')


    def _compile_parameter_list(self):
        # grammar: ((type varName)(,type varName)*)?
        # codegen: n/a. adds args to the subroutine symbol table.
        while self._t.get_token() != ')':
            type = self._compile_type()
            identifier = self._process_type(TokenType.IDENTIFIER)
            self._subroutine_table.define(identifier, type, VarKind.ARG)
            if self._t.get_token() != ',':
                break
            self._process(',')


    def _compile_var_dec(self):
        # grammar: 'var' type varName (, varName)* ';'
        # codegen: n/a. adds local vars to the subroutine symbol table.
        self._process('var')
        type = self._compile_type()
        while True:
            identifier = self._process_type(TokenType.IDENTIFIER)
            self._subroutine_table.define(identifier, type, VarKind.VAR)
            if self._t.get_token() != ',':
                break
            self._process(',')

        self._process(';')


    def _compile_statements(self):
        # grammar: (letStatement | ifStatement | whileStatement
        #           | doStatement | returnStatement)*
        # codegen: generate a statement.
        while True:
            match self._t.get_token():
                case 'let':
                    self._compile_let()
                case 'if':
                    self._compile_if()
                case 'while':
                    self._compile_while()
                case 'do':
                    self._compile_do()
                case 'return':
                    self._compile_return()
                case _:
                    break


    def _compile_let(self):
        # grammar: 'let' varName ('[' expression ']')? '=' expression ';'
        # codegen: make an assignment.
        self._process("let")
        var_name = self._process_type(TokenType.IDENTIFIER)
        info, seg = self._resolve_symbol(var_name)

        if self._t.get_token() != '[':
            self._process('=')
            self._compile_expression()
            self._process(';')
            self._writer.write_pop(seg, info.index)
        else:
            self._writer.write_push(seg, info.index)
            self._process('[')
            self._compile_expression()
            self._process(']')
            self._writer.write_arithmetic(VMArithmetic.ADD)
            self._process('=')
            self._compile_expression()
            self._process(';')
            self._writer.write_pop(VMSegment.TEMP, 0)
            self._writer.write_pop(VMSegment.POINTER, 1)
            self._writer.write_push(VMSegment.TEMP, 0)
            self._writer.write_pop(VMSegment.THAT, 0)


    def _compile_if(self):
        # grammar: 'if' '(' expression ')' '{' statements '}'
        #          ('else' '{' statements '}')?
        # codegen: self-explanatory
        else_label = f"{self._class_name}.{self._label_count}.else"
        end_label = f"{self._class_name}.{self._label_count}.if_end"
        self._label_count += 1

        self._process('if')
        self._process('(')
        self._compile_expression()
        # goto 'else' if not true
        self._writer.write_arithmetic(VMArithmetic.NOT)
        self._writer.write_if(else_label)
        self._process(')')
        self._process('{')
        self._compile_statements()
        self._process('}')
        # goto end
        self._writer.write_goto(end_label)
        # begin else label
        self._writer.write_label(else_label)
        if self._t.get_token() == 'else':
            self._process('else')
            self._process('{')
            self._compile_statements()
            self._process('}')
        # end label
        self._writer.write_label(end_label)


    def _compile_while(self):
        # grammar: 'while' '(' expression ')' '{' statements '}'
        # codegen: self-explanatory
        loop_start_label = f"{self._class_name}.{self._label_count}.while_start"
        loop_end_label = f"{self._class_name}.{self._label_count}.while_end"
        self._label_count += 1

        # plant loop start label
        self._writer.write_label(loop_start_label)

        self._process('while')
        self._process('(')
        self._compile_expression()
        # jump out of loop if expression is false
        self._writer.write_arithmetic(VMArithmetic.NOT)
        self._writer.write_if(loop_end_label)
        self._process(')')
        self._process('{')
        self._compile_statements()
        # jump to start of loop
        self._writer.write_goto(loop_start_label)
        self._process('}')

        # plant loop end label
        self._writer.write_label(loop_end_label)


    def _compile_do(self):
        # grammar: 'do' subroutineCall ';'
        # codegen: perform a function call and drop its return value.
        self._process('do')
        # impl trick: 'subroutineCall' is folded into 'term' to isolate the
        # implementation of +1 lookahead to just one spot.
        self._compile_term()
        self._process(';')
        self._writer.write_pop(VMSegment.TEMP, 0)


    def _compile_return(self):
        # grammar: 'return' expression? ';'
        # codegen: exit a function and return a value. void functions return 0.
        self._process('return')
        if self._t.get_token() != ';':
            self._compile_expression()
        else:
            self._writer.write_push(VMSegment.CONSTANT, 0)

        self._process(';')
        self._writer.write_return()


    def _compile_expression(self):
        # grammar: term (op term)*
        # codegen: push the expression result.
        self._compile_term()
        while self._t.get_token() in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:
            symbol = self._process_type(TokenType.SYMBOL)
            self._compile_term()
            match symbol:
                case '+':
                    self._writer.write_arithmetic(VMArithmetic.ADD)
                case '-':
                    self._writer.write_arithmetic(VMArithmetic.SUB)
                case '*':
                    self._writer.write_call('Math.multiply', 2)
                case '/':
                    self._writer.write_call('Math.divide', 2)
                case '&':
                    self._writer.write_arithmetic(VMArithmetic.AND)
                case '|':
                    self._writer.write_arithmetic(VMArithmetic.OR)
                case '<':
                    self._writer.write_arithmetic(VMArithmetic.LT)
                case '>':
                    self._writer.write_arithmetic(VMArithmetic.GT)
                case '=':
                    self._writer.write_arithmetic(VMArithmetic.EQ)
                case _:
                    raise Exception("Something went wrong.")


    def _compile_term(self):
        # grammar:
        # integerConstant | stringConstant | keywordConstant | varName |
        # varName'[' expression ']' | '(' expression ')' | (unaryOp term) |
        # subroutineName '(' expressionList ')' |
        # (className | varName) '.' subroutineName '(' expressionList ')'
        #
        # codegen: push a value, either directly in the case of a
        # constant/variable, or by generating an expression or a function call.
        token_type = self._t.get_token_type()
        token = self._t.get_token()
        self._process(token)

        if token_type == TokenType.INT_CONST:
            # integerConstant
            self._writer.write_push(VMSegment.CONSTANT, int(token))
        elif token_type == TokenType.STRING_CONST:
            # stringConstant
            self._writer.write_push(VMSegment.CONSTANT, len(token))
            self._writer.write_call("String.new", 1)
            for char in token:
                self._writer.write_push(VMSegment.CONSTANT, ord(char))
                self._writer.write_call("String.appendChar", 2)
        elif token_type == TokenType.KEYWORD:
            # keywordConstant
            match token:
                case 'true':
                    self._writer.write_push(VMSegment.CONSTANT, 1)
                    self._writer.write_arithmetic(VMArithmetic.NEG)
                case 'false' | 'null':
                    self._writer.write_push(VMSegment.CONSTANT, 0)
                case 'this':
                    self._writer.write_push(VMSegment.POINTER, 0)
                case _:
                    raise Exception("Something went wrong.")
        elif token in { '-', '~' }:
            # (unaryOp term)
            self._compile_term()
            if token == '-':
                self._writer.write_arithmetic(VMArithmetic.NEG)
            else:
                self._writer.write_arithmetic(VMArithmetic.NOT)
        elif token == '(':
            # '(' expression ')'
            self._compile_expression()
            self._process(')')
        elif token_type == TokenType.IDENTIFIER:
            # special case: next token isn't determined, must lookahead.
            next_token = self._t.get_token()
            if next_token not in {'[', '(', '.'}:
                # varName
                info, seg = self._resolve_symbol(token)
                self._writer.write_push(seg, info.index)
            elif next_token == '[':
                # varName'[' expression ']'
                info, seg = self._resolve_symbol(token)
                self._writer.write_push(seg, info.index)
                self._process('[')
                self._compile_expression()
                self._process(']')
                self._writer.write_arithmetic(VMArithmetic.ADD)
                self._writer.write_pop(VMSegment.POINTER, 1)
                self._writer.write_push(VMSegment.THAT, 0)
            elif next_token == '(':
                # subroutineName '(' expressionList ')'
                subr_name = token
                # method on current object -> push 'this' as arg 0
                self._writer.write_push(VMSegment.POINTER, 0)
                self._process('(')
                n_args = self._compile_expression_list()
                self._process(')')
                self._writer.write_call(f"{self._class_name}.{subr_name}", n_args + 1)
            elif next_token == '.':
                # (className | varName) '.' subroutineName '(' expressionList ')'
                if (not self._subroutine_table.has_symbol(token) and
                    not self._class_table.has_symbol(token)):
                    is_method = False
                    class_name = token
                else:
                    is_method = True
                    info, seg = self._resolve_symbol(token)
                    class_name = info.type
                    self._writer.write_push(seg, info.index)

                self._process('.')
                subr_name = self._process_type(TokenType.IDENTIFIER)
                self._process('(')
                n_args = self._compile_expression_list()
                self._process(')')
                self._writer.write_call(f"{class_name}.{subr_name}", n_args + is_method)
            else:
                raise SyntaxError(f"Unresolved symbol {next_token} in term expression.")
        else:
            raise SyntaxError("Unresolved symbol {token} in term expression.")


    def _compile_expression_list(self) -> int:
        """Compile an expression list.
        Returns the # of expressions matched for convenience."""
        # grammar: (expression (',' expression)*)?
        # codegen: generates a series of expressions, pushing each on the stack.
        n_exprs = 0
        while self._t.get_token() != ')':
            self._compile_expression()
            n_exprs += 1
            if self._t.get_token() != ',':
                break
            self._process(',')

        return n_exprs


    def _compile_type(self) -> str:
        """Compile a type.
        Returns the type token for convencience."""
        # grammar: type <-> (int | char | boolean | className)
        # codegen: n/a
        if self._t.get_token_type() == TokenType.IDENTIFIER:
            return self._process_type(TokenType.IDENTIFIER)
        else:
            return self._process_one_of(['int', 'char', 'boolean'])
