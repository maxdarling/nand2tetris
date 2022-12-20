"""Translates Hack assembly C-instructions to their respective binary codes.

Example usage:
   import decoder

   decoder.dest('DM') # '011'
   decoder.comp('M+1') # '1110111'
   decoder.jump('JNE') # '101'
"""

def dest(s: str) -> str:
    options = {'' : '000',
               'M' : '001',
               'D' : '010',
               'DM' : '011',
               'A' : '100',
               'AM' : '101',
               'AD' : '110',
               'ADM' : '111'
    }
    s = ''.join(sorted(s)) # e.g. allows for 'DM' and 'MD'
    return options[s] 

def comp(s: str) -> str:
    a = '0' if s.find('M') == -1 else '1'
    s = s.replace('M', 'A')

    options = {'0' : '101010',
               '1' : '111111',
               '-1' : '111010',
               'D' : '001100',
               'A' : '110000',
               '!D' : '001101',
               '!A' : '110001',
               '-D' : '001111',
               '-A' : '110011',
               'D+1' : '011111',
               'A+1' : '110111',
               'D-1' : '001110',
               'A-1' : '110010',
               'D+A' : '000010',
               'D-A' : '010011',
               'A-D' : '000111',
               'D&A' : '000000',
               'D|A' : '010101'
    }
    return a + options[s]

def jump(s: str) -> str:
    options = {'' : '000',
               'JGT' : '001',
               'JEQ' : '010',
               'JGE' : '011',
               'JLT' : '100',
               'JNE' : '101',
               'JLE' : '110',
               'JMP' : '111'
    }
    return options[s]

