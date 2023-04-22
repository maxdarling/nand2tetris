import os
import sys

from compilation_engine import CompilationEngine

def compile(source: str):
    """Compiler for the Jack language.

    Given a path to a .jack file or a directory of .jack files, writes
    compiled VM files for each Jack file, like so:
    - [single file]: my/File.jack -> my/File.vm
    - [directory]: my/Project -> my/Project/FileOne.vm, my/Project/FileTwo.vm, ...

    See 'compilation_engine.py' for more details.
    """
    # determine list of files to read + write
    infiles = []
    if os.path.isfile(source):
        infiles = [source]
    else:
        source = source.rstrip('/')
        with os.scandir(source) as it:
            for entry in it:
                if entry.name.endswith('.jack'):
                    infiles.append(entry.path)

    outfiles = [file[:-4] + 'vm' for file in infiles]

    # compile each file
    for infile, outfile in zip(infiles, outfiles):
        engine = CompilationEngine(infile, outfile)
        engine.compile()
        print(f"compiled file {infile}")

if __name__ == '__main__':
    compile(sys.argv[1])
