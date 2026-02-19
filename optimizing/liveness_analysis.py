import re

from howBIGisit import how_big_is_it

def get_kill_lines(file_in):
    NUM_VARS = how_big_is_it(file_in)

    var_list = range(NUM_VARS)
    regex = re.compile("t\[[0-9]+\]")

    last_usages = [-1 for _ in var_list]    # For each variable, what is the line number it is last used at

    file = open(file_in, "r+")
    line = file.readline()
    lineno = 1

    while line:
        iter = re.finditer(regex, line)
        for match in iter:
            index = int(match.group(0)[2:-1])
            last_usages[index] = lineno

        line = file.readline()
        lineno += 1

    kill_line = [[] for _ in range(lineno)]   # Which variables are "killed off" at each line
    for i in var_list:
        lineno = last_usages[i]
        kill_line[lineno].append(i)

    return kill_line, last_usages

def plot_livesize(file_in):
    regex = re.compile("t\[[0-9]+\]")

    file = open(file_in, "r+")
    line = file.readline()
    lineno = 1

    kill_line, _ = get_kill_lines(file_in)

    liveset = set()
    lines = []
    livesizes = []

    while line:
        eq_index = line.find("=")
        if eq_index >= 0:
            assignment = line[:eq_index]
            match = re.findall(regex, assignment)
            if len(match) > 0:
                match = match[0]
                index = int(match[2:-1])
                liveset.add(index)

            rhs = line[eq_index + 1:]
            iter = re.finditer(regex, rhs)
            for match in iter:
                index = int(match.group(0)[2:-1])
                if index in kill_line[lineno]:
                    try:
                        liveset.remove(index)
                    except KeyError:
                        print(f"Element {index} wasn't in the set anyway!")

        lines.append(lineno)
        livesizes.append(len(liveset))

        line = file.readline()
        lineno += 1

def reassign_unused_vars(file_in, file_out):
    NUM_VARS = how_big_is_it(file_in)

    var_list = range(NUM_VARS)
    var_map = [-1 for _ in var_list]    # What variable should each variable be replaced with

    def fix_index(match):
        match_str = match.group(0)[2:-1]
        index = int(match_str)
        new_idx = var_map[index]
        return f"t[{index}]" if new_idx == -1 else f"t[{new_idx}]"
    
    regex = re.compile("t\[[0-9]+\]")

    file = open(file_in, "r+")
    new_file = open(file_out, "w")
    line = file.readline()
    lineno = 1
    free_list = []  # Which variables are eligible to replace the next assignment

    kill_line, last_usages = get_kill_lines(file_in)

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
                    new_kill_line = last_usages[index]
                    kill_line[new_kill_line].remove(index)
                    kill_line[new_kill_line].append(free_var)

        line = re.sub(regex, fix_index, line)
        new_file.write(line)
        line = file.readline()
        lineno += 1

if __name__ == "__main__":
    reassign_unused_vars("out_files/3b/sharedcomps.cpp", "out_files/3b/newvars-new.cpp")
    print(how_big_is_it("out_files/3b/newvars-new.cpp"))