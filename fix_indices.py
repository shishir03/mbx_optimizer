### Fix indices s.t. t[9] => t[9*8 + i]
import re

regex = re.compile("[gtx]\[[0-9]+\]")

def fix_idx(match):
    index = match.group(0)
    # print(index)
    return f"{index[:2]}({index[2:-1]})*8 + i]"

def vectorize_indices(file_in, file_out):
    file = open(file_in, "r+")
    new_file = open(file_out, "w")
    line = file.readline()

    open_bracket = False
    while line:
        new_line = re.sub(regex, fix_idx, line)
        new_file.write(new_line)
        if "void" in line and "{" in line:
            new_file.write("#pragma omp simd simdlen(8)\n")
            new_file.write("for(int i = 0; i < 8; i++) {\n")
            open_bracket = True
        if "}" in line and open_bracket:
            new_file.write("}\n")
            open_bracket = False
        line = file.readline()

if __name__ == "__main__":
    vectorize_indices("out_files/noskips2.cpp", "out_files/newtest.cpp")
