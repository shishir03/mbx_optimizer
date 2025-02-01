import re

# How many variables are used in the file in total?
def how_big_is_it(file_in):
    regex = "t\[[0-9]+"
    regex = re.compile(regex)
    
    file = open(file_in, "r+")
    line = file.readline()
    maxidx = 0

    while line:
        iter = re.finditer(regex, line)
        for match in iter:
            index = int(match.group(0)[2:])
            maxidx = max(maxidx, index)

        line = file.readline()

    return maxidx + 1
