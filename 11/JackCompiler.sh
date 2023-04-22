#!/bin/bash

# Usage: ./JackCompiler.sh source
#
# where 'source' is a path to a .jack file or a directory of .jack files. Writes
# compiled VM files for each Jack file, like so:
# - [single file]: my/File.jack -> my/File.vm
# - [directory]: my/Project -> my/Project/FileOne.vm, my/Project/FileTwo.vm, ...
python3 compiler.py $1
