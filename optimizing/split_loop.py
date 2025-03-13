import numpy as np

def split_file(file_in, file_out):
    file = open(file_in, "r+")
    contents = file.read()
    lines = contents.split("\n")
    lines_to_split = np.array(lines[41:12239])

    split_lines = np.array_split(lines_to_split, 100)
    new_file = open(file_out, "w")
    for i in range(100):
        new_file.write(
    """    #pragma omp simd simdlen(8)
    for(size_t i = 0; i < 8; i++) {
        size_t nv = j*8 + i;
""")

        for l in split_lines[i]:
            new_file.write(f"{l}\n")

        new_file.write("\t}\n")

if __name__ == "__main__":
    split_file("out_files/poly-2b-v6x-new.cpp", "out_files/split_loop.txt")