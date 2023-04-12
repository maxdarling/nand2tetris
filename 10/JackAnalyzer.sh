#!/bin/bash

# Usage: ./JackAnalyzer.sh source
#
# where 'source' is a path to a .jack file or a directory of .jack files. Writes
# an XML parse tree for each Jack file, like so:
# - [single file]: my/File.jack -> my/File.xml
# - [directory]: my/Project -> my/Project/FileOne.xml, my/Project/FileTwo.xml, ...
python3 analyzer.py $1
