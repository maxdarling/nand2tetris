import os
import sys

from compilation_engine import CompilationEngine

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
        source = source.rstrip('/')
        with os.scandir(source) as it:
            for entry in it:
                if entry.name.endswith('.jack'):
                    files.append(entry.path)

    outfiles = [file[:-4] + 'xml' for file in files]

    # compile each file
    for i in range(len(files)):
        engine = CompilationEngine(files[i], outfiles[i])
        engine.compile()
        print(f"compiled file {files[i]}")

if __name__ == '__main__':
    analyze(sys.argv[1])
