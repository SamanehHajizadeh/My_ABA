from os import listdir
from os.path import isfile, join, splitext
from aba.argumet_transformer import Argumet_transformer

input_list = []
with open('inputs.txt', "r") as f:
    input_list = f.readlines()
input_list = [x.strip() for x in input_list]

path = "input_files"

test_files = [f for f in listdir(path) if
              splitext(f)[0] in input_list and isfile(join(path, f)) and splitext(f)[1] == ".txt"]

for file in test_files:
    with open(join(path, file), 'r') as f:
        source_code = f.read()
        print("hello kitty")
        parser = Argumet_transformer(source_code)
        parse_errors = parser.parse()
        parser.aba_constructBuilder()
