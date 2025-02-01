import re

from howBIGisit import how_big_is_it

def remove_assignments(file_in, file_out, arr):
    NUM_VARS = how_big_is_it(file_in)
    a_vars = ["" for _ in range(NUM_VARS)]

    def fix_index(match):
        match_str = match.group(0)
        index = int(match_str[2:-1])
        a_var = a_vars[index]
        return a_var if a_var != "" else match_str
    
    regex = "t\[[0-9]+\] = [^;]*;"
    regex = re.compile(regex)

    file = open(file_in, "r+")
    line = file.readline()

    while line:
        rhs = re.findall(regex, line)
        if len(rhs) > 0:
            rhs = rhs[0]
            eqsign = rhs.find("=")
            lhs = rhs[:eqsign - 1]
            rhs = rhs[eqsign + 2:-1]
            if rhs[0] == arr:
                lhs_idx = int(lhs[2:-1])
                a_vars[lhs_idx] = rhs

        line = file.readline()

    file = open(file_in, "r+")
    new_file = open(file_out, "w")
    line = file.readline()

    regex = "t\[[0-9]+\]"
    regex = re.compile(regex)

    while line:
        # Line does not assign to an a[] var
        if line.find(f"= {arr}") == -1:
            line = re.sub(regex, fix_index, line)
            new_file.write(line)

        line = file.readline()
