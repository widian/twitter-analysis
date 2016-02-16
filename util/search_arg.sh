#i : case insensitive
#n : print line of result
#-color : coloring in keyword
grep -in --color -A1 $1 ../*.py ../*/*.py
