# Are any t indices in the file used without ever being assigned to?
import re

assigned = set()
used = set()

t_var = re.compile("t\\[[0-9]+\\]")
t_line = re.compile("t\\[[0-9]+\\] = [^;]*;")
file = open("out_files/nodf.cpp", "r+")
line = file.readline()

while line:
    rhs = re.findall(t_line, line)
    if len(rhs) > 0:
        rhs = rhs[0]
        eqsign = rhs.find("=")
        lhs = rhs[:eqsign - 1]
        lhs_idx = int(lhs[2:-1])
        rhs = rhs[eqsign + 2:-1]
        
        assigned.add(lhs_idx)
        rhs_vars = re.findall(t_var, rhs)
        for var in rhs_vars:
            idx = int(var[2:-1])
            used.add(idx)

    line = file.readline()

print(used - assigned)