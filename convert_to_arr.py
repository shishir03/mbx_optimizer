# Convert a polynomial file to using a t[] array instead of local variables
import re
import shutil

from remove_newlines import remove_newlines

def convert_to_arr(file_in, file_out):
    line_regex = "const double t[0-9]+ =[^;]*;"
    remove_newlines(file_in, "new_file.txt", line_regex)
    shutil.copy("new_file.txt", file_in)

    func_regex = "eval\("
    t_regex = "t[0-9]+"

    file = open(file_in, "r+")
    new_file = open(file_out, "w")
    line = file.readline()

    while line:
        line = re.sub(func_regex, fix_func, line)
        line = re.sub(t_regex, fix_t, line)
        line = re.sub("const double ", "", line)

        new_file.write(line)
        line = file.readline()

def fix_func(match):
    return match.group(0) + "double* t, "

def fix_t(match):
    var = int(match.group(0)[1:])
    return f"t[{var}]"

# convert_to_arr("src/potential/2b/poly-2b-v6x.cpp", "new_file.txt")
