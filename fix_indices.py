### Fix indices s.t. t[9] => t[9*8 + i]
import re

regex = "[gtx]\[[0-9]+\]"
regex = re.compile(regex)

def fix_all(s):
    iter = re.finditer(regex, s)
    for match in iter:
        index = match.group(0)
        s = re.sub(regex, index[:-1] + "*8 + i]", s, count=1)

    return s

def vectorize_indices(file_in, file_out):
    file = open(file_in, "r+")
    new_file = open(file_out, "w")
    line = file.readline()

    open_bracket = False
    while line:
        new_file.write(fix_all(line))
        if "void" in line and "{" in line:
            new_file.write("#pragma omp simd simdlen(8)\n")
            new_file.write("for(int i = 0; i < 8; i++) {\n")
            open_bracket = True
        if "}" in line and open_bracket:
            new_file.write("}\n")
            open_bracket = False
        line = file.readline()
