from os import listdir, getpid
from os.path import isfile, join, splitext
from aba.aba_parser import ABA_Parser

print("Start performance test")

runonly = []
with open("test_files.txt", "r") as f:
    runonly = f.readlines()
runonly = [x.strip() for x in runonly]

path = "input_files"

test_files = [f for f in listdir(path) if
              splitext(f)[0] in runonly and isfile(join(path, f)) and splitext(f)[1] == ".txt"]

for file in test_files:
    with open(join(path, file), 'r') as f:
        source_code = f.read()
        print("Start running %s", file)

        parser = ABA_Parser(source_code)
        parse_errors = parser.parse()

        if len(parse_errors) > 0:
            print("Parse error: %s", ', '.join(parse_errors))
        else:
            try:
                parser.construct_aba()
            except MemoryError:
                print("Out of memory!")
