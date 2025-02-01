import re

from howBIGisit import how_big_is_it

def reassign_unused_vars(file_in, file_out):
    NUM_VARS = how_big_is_it(file_in)

    var_list = range(NUM_VARS)
    var_map = [-1 for _ in var_list]    # What variable should each variable be replaced with

    def fix_index(match):
        match_str = match.group(0)[2:-1]
        index = int(match_str)
        new_idx = var_map[index]
        return f"t[{index}]" if new_idx == -1 else f"t[{new_idx}]"
    
    regex = "t\[[0-9]+\]"
    regex = re.compile(regex)

    live_ranges = [-1 for _ in var_list]    # For each variable, what is the line number it is last used at

    # Simple liveness detection algorithm - live range is just the first and last usages of a variable
    file = open(file_in, "r+")
    line = file.readline()
    lineno = 1

    while line:
        iter = re.finditer(regex, line)
        for match in iter:
            index = int(match.group(0)[2:-1])
            live_ranges[index] = lineno

        line = file.readline()
        lineno += 1

    kill_line = [[] for _ in range(lineno)]   # Which variables are "killed off" at each line
    for i in var_list:
        lineno = live_ranges[i]
        kill_line[lineno].append(i)

    file = open(file_in, "r+")
    new_file = open(file_out, "w")
    line = file.readline()
    lineno = 1
    free_list = []  # Which variables are eligible to replace the next assignment

    '''
    For each line:
    1. Do any variables die on this line? If so, add them to the free list
    2. Are there any assignments on this line? If so, try to replace with a variable from the free list
    3. Make any necessary replacements throughout the line based on the variable map
    '''
    while line:
        free_list.extend(kill_line[lineno])

        # Line has an assignment
        eq_index = line.find("=")
        if eq_index >= 0:
            assignment = line[:eq_index]
            match = re.findall(regex, assignment)
            if len(match) > 0:
                match = match[0]
                index = int(match[2:-1])

                if len(free_list) > 0:
                    free_var = free_list.pop()
                    var_map[index] = free_var
                    new_kill_line = live_ranges[index]
                    kill_line[new_kill_line].remove(index)
                    kill_line[new_kill_line].append(free_var)

        line = re.sub(regex, fix_index, line)
        new_file.write(line)
        line = file.readline()
        lineno += 1
