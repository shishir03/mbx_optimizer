import numpy as np

"""
Split file structure:

void f???(const double *x, const double *a, double *t, size_t nv0, size_t nd) {
    #simd
    for(int i = 0; i < 8; i++) {
        t[0*8 + i] = ... ;
        t[1*8 + i] = ... ;
        ...
    }
}

...

std::vector<double> poly_2b_v6x::eval(const size_t nd, const double* a, const double* x, double* t, double* g) {
    int nv = 0;
    for(int j = 0; j < nd / 8; j++) {
        f1(x, a, t, j*8, nd);
        ...
        f100(x, a, t, j*8, nd);

        for(int i = 0; i < 8; i++) {
            nv = j*8 + i;
            g[nv + nd*0] = t[???*8 + i] + t[???*8 + i] + ... ;
            ...

            energy[nv] = t[???*8 + i] + t[???*8 + i];
        }
    }

    for(int i = 0; nv < nd; i++) {
        nv++;
        t[0*8 + i] = ... ;
        t[1*8 + i] = ... ;
        ...

        g[nv + nd*0] = t[???*8 + i] + t[???*8 + i] + ... ;
        ...

        energy[nv] = t[???*8 + i] + t[???*8 + i];
    }
}
"""

def split_file(file_in, file_out):
    file = open(file_in, "r+")
    contents = file.read()
    lines = contents.split("\n")
    lines_to_split = np.array(lines[41:12239])

    split_lines = np.array_split(lines_to_split, 100)
    new_file = open(file_out, "w")
    for i in range(100):
        new_file.write(f"void f{i}(const double *x, const double *a, double *t, double nv0, double nd) {{")
        new_file.write("""
    #pragma omp simd simdlen(8)
    for(size_t i = 0; i < 8; i++) {
        size_t nv = nv0 + i;
""")

        for l in split_lines[i]:
            new_file.write(f"{l}\n")

        new_file.write("}\n}\n\n")

    for i in range(100):
        new_file.write(f"f{i}(x, a, t, j*8, nd);\n")

if __name__ == "__main__":
    split_file("out_files/poly-2b-v6x-new.cpp", "out_files/split.txt")
