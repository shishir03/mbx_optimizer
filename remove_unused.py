import re
import bisect

from howBIGisit import how_big_is_it

def remove_unused_vars(file_in, file_out):
    NUM_VARS = how_big_is_it(file_in)

    vars_to_delete = []
    def fix_index(match):
        match_str = match.group(0)[2:-1]
        index = int(match_str)
        index -= bisect.bisect_left(vars_to_delete, index)
        return f"t[{index}]"

    regex = "t\[[0-9]+\]"
    regex = re.compile(regex)

    usages = [0 for _ in range(NUM_VARS)]

    file = open(file_in, "r+")
    contents = file.read()
    vars = [int(i[2:-1]) for i in re.findall(regex, contents)]  # Every variable usage in the program

    for i in vars:
        usages[i] += 1

    for i in range(NUM_VARS):
        if usages[i] <= 1:
            vars_to_delete.append(i)

    # print(vars_to_delete)

    file = open(file_in, "r+")
    new_file = open(file_out, "w")
    line = file.readline()

    regex_line = "t\[[0-9]+\] = [^;]*;"
    regex_line = re.compile(regex_line)

    while line:
        rhs = re.findall(regex_line, line)
        if len(rhs) > 0:
            rhs = rhs[0]
            eqsign = rhs.find("=")
            lhs = rhs[:eqsign - 1]
            lhs_var = int(lhs[2:-1])
            if lhs_var in vars_to_delete:
                line = file.readline()
                continue

        iter = re.finditer(regex, line)
        line = re.sub(regex, fix_index, line)

        new_file.write(line)
        line = file.readline()
