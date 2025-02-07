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
    
    a_regex = re.compile(f"t\[[0-9]+\] = {arr}\[[0-9]+\];")

    file = open(file_in, "r+")
    line = file.readline()

    while line:
        rhs = re.findall(a_regex, line)
        if len(rhs) > 0:
            rhs = rhs[0]
            eqsign = rhs.find("=")
            lhs = rhs[:eqsign - 1]
            rhs = rhs[eqsign + 2:-1]
            lhs_idx = int(lhs[2:-1])
            a_vars[lhs_idx] = rhs

        line = file.readline()

    print(a_vars)

    file = open(file_in, "r+")
    new_file = open(file_out, "w")
    line = file.readline()

    regex = re.compile("t\[[0-9]+\]")

    while line:
        # Line does not assign to an a[] var
        if re.search(a_regex, line) is None:
            line = re.sub(regex, fix_index, line)
            new_file.write(line)

        line = file.readline()

if __name__ == "__main__":
    remove_assignments("out_files/nodf.cpp", "out_files/noassignments.cpp", "a")
