import os
import sys

from tokenizer import JackTokenizer, TokenType

def analyze(source: str):
    """Parser / syntax analyzer for the Jack language.

    Given a path 'source' to a .jack file or directory of .jack files, writes an XML parse tree
    for each Jack file, like so:
    - [single file]: my/File.jack -> my/File.xml
    - [directory]: my/Project -> my/Project/FileOne.xml, my/Project/FileTwo.xml, ...
    """
    # determine list of files to read + write
    files = []
    if os.path.isfile(source):
        files = [source]
    else:
        source = source[:-1] if source[-1] == '/' else source
        with os.scandir(source) as it:
            for entry in it:
                if entry.name.endswith('.jack'):
                    files.append(entry.path)

    outfiles = [file[:-4] + 'xml' for file in files]

    # construct XML
    for i in range(len(files)):
        out_lines = []
        t = JackTokenizer(files[i])
        t.advance()
        while t.hasMoreTokens():
            tokenType = t.getTokenType()
            tagstr = None # temp, for testing
            token = t.getToken()
            if tokenType == TokenType.KEYWORD:
                tagstr = 'keyword'
            elif tokenType == TokenType.SYMBOL:
                symbol_conv = { '<' : '&lt;', '>' : '&gt;', '"' : '&quot;', '&' : '&amp;'}
                if token in symbol_conv:
                    token = symbol_conv[token]
                tagstr = 'symbol'
            elif tokenType == TokenType.IDENTIFIER:
                tagstr = 'identifier'
            elif tokenType == TokenType.INT_CONST:
                tagstr = 'integerConstant'
            else:
                tagstr = 'stringConstant'

            res = f"<{tagstr}> {token} </{tagstr}>"
            out_lines.append(res)
            t.advance()

        with open(outfiles[i], 'w') as f:
            out_lines = ['<tokens>'] + out_lines + ['</tokens>'] # temp testing
            f.write("\n".join(out_lines) + "\n")
            # f.writelines("%s\n" % l for l in out_lines)
            print(f"wrote file {outfiles[i]}")


if __name__ == '__main__':
    analyze(sys.argv[1])

