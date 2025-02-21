from remove_unused import get_unused_vars

file_bad = "test_files/bad_t.txt"
file_good = "test_files/good_t.txt"

unused_t = get_unused_vars("out_files/noaassignments.cpp", 0)
print(unused_t)

file_bad = open(file_bad, "r")
file_good = open(file_good, "r")

line_bad = file_bad.readline()
line_good = file_good.readline()

while line_bad:
    bad_t = line_bad.split(" , ")
    good_t = line_good.split(" , ")
    bad_indices = []
    for i in range(len(bad_t) - 1):
        if float(bad_t[i]) - float(good_t[i]) > 1e-10 and i not in unused_t:
            bad_indices.append(i)

    print(bad_indices)
    line_bad = file_bad.readline()
    line_good = file_good.readline()
