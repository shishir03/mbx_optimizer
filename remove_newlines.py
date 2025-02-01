'''
Remove newlines from computations

e.g. t[1] =
            t[2] + t[3] +
            t[4] + t[5];

becomes t[1] =          t[2] + t[3] +           t[4] + t[5];
'''

import re

def fix_comp(match):
    match_str = match.group(0)
    return re.sub("\n", " ", match_str)

def remove_newlines(file_in, file_out, line_regex="t\\[[0-9]+\\] =[^;]*;"):
    # regex = "t\\[[0-9]+\\] =[^;]*;"
    regex = re.compile(line_regex)

    file = open(file_in, "r+")
    contents = file.read()

    new_file = open(file_out, "w")
    contents = re.sub(regex, fix_comp, contents)
    new_file.write(contents)
