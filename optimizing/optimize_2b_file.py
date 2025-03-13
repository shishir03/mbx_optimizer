import time
import os

from computations import reassign_shared_computations
from convert_to_arr import convert_to_arr
from remove_df import remove_df
from fix_indices import vectorize_indices
from liveness_analysis import reassign_unused_vars
from remove_a_assignments import remove_assignments
from remove_newlines import remove_newlines
from remove_unused import remove_unused_vars
from howBIGisit import how_big_is_it

MBX_DIR = f"{os.getenv("HOME")}/MBX/src/potential"
OUT_DIR = "out_files"
files = []

print("Removing newlines...")
t1 = time.time()
files.append(f"{OUT_DIR}/poly-2b-v6x-old.cpp")
files.append(f"{OUT_DIR}/nobreaks.cpp")
remove_newlines(files[0], f"{OUT_DIR}/new_file.txt")
remove_newlines(f"{OUT_DIR}/new_file.txt", files[-1], "const double t[0-9]+ =[^;]*;")
t2 = time.time()
print(f"Removed newlines from {files[-2]} in {t2 - t1} seconds")

print("Converting to t[] array...")
t1 = time.time()
files.append(f"{OUT_DIR}/noconst.cpp")
convert_to_arr(files[-2], files[-1])
t2 = time.time()
print(f"Converted {files[-2]} to use t[] in {t2 - t1} seconds")

print("Removing a assigments...")
t1 = time.time()
files.append(f"{OUT_DIR}/noaassignments.cpp")
remove_assignments(files[-2], files[-1], "a")
t2 = time.time()
print(f"Removed a assignments from {files[-2]} in {t2 - t1} seconds")

print("Removing df[] array...")
t1 = time.time()
files.append(f"{OUT_DIR}/nodf.cpp")
remove_df(files[-2], files[-1])
t2 = time.time()
print(f"Removed df[] from {files[-2]} in {t2 - t1} seconds")

print("Removing unused indices...")
t1 = time.time()
files.append(f"{OUT_DIR}/noskips.cpp")
remove_unused_vars(files[-2], files[-1])
t2 = time.time()
print(f"Removed unused indices from {files[-2]} in {t2 - t1} seconds")

print("Reassigning shared computations (pass 1)...")
t1 = time.time()
files.append(f"{OUT_DIR}/sharedcomps.cpp")
reassign_shared_computations(files[-2], files[-1])
print("Reassigning shared computations (pass 2)...")
files.append(f"{OUT_DIR}/sharedcomps2.cpp")
reassign_shared_computations(files[-2], files[-1])
t2 = time.time()
print(f"Reassigned shared computations in {files[-2]} in {t2 - t1} seconds")

print("Reassigning variables...")
t1 = time.time()
files.append(f"{OUT_DIR}/newvars.cpp")
reassign_unused_vars(files[-2], files[-1])
t2 = time.time()
print(f"Reassigned variables in {files[-2]} in {t2 - t1} seconds")

print("Removing unused indices...")
t1 = time.time()
files.append(f"{OUT_DIR}/noskips2.cpp")
remove_unused_vars(files[-2], files[-1])
t2 = time.time()
print(f"Removed unused indices from {files[-2]} in {t2 - t1} seconds")

print("Adding vectorization...")
t1 = time.time()
files.append(f"{OUT_DIR}/poly-2b-v6x-new.cpp")
vectorize_indices(files[-2], files[-1])
t2 = time.time()
print(f"Vectorized {files[-2]} in {t2 - t1} seconds")

size1 = how_big_is_it(files[0])
size2 = how_big_is_it(files[-1])
print(f"All done! Number of variables used decreased from {size1} to {size2}. Now fix the rest of the file yourself stupid")
