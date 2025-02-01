import time
import os

from computations import reassign_shared_computations
from fix_indices import vectorize_indices
from liveness_analysis import reassign_unused_vars
from remove_a_assignments import remove_assignments
from remove_newlines import remove_newlines
from remove_unused import remove_unused_vars
from howBIGisit import how_big_is_it

MBX_DIR = f"{os.getenv("HOME")}/MBX/src/potential"
files = []

print("Removing newlines...")
t1 = time.time()
files.append(f"{MBX_DIR}/3b/poly-3b-v2x.cpp")
files.append("out_files/nobreaks.cpp")
remove_newlines(files[-2], files[-1])
t2 = time.time()
print(f"Removed newlines from {files[-2]} in {t2 - t1} seconds")

print("Removing a assigments...")
t1 = time.time()
files.append("out_files/noaassignments.cpp")
remove_assignments(files[-2], files[-1], "a")
t2 = time.time()
print(f"Removed a assignments from {files[-2]} in {t2 - t1} seconds")

print("Removing unused indices...")
t1 = time.time()
files.append("out_files/noskips.cpp")
remove_unused_vars(files[-2], files[-1])
t2 = time.time()
print(f"Removed unused indices from {files[-2]} in {t2 - t1} seconds")

print("Reassigning shared computations (pass 1)...")
t1 = time.time()
files.append("out_files/sharedcomps.cpp")
reassign_shared_computations(files[-2], files[-1])
print("Reassigning shared computations (pass 2)...")
files.append("sharedcomps2.cpp")
reassign_shared_computations(files[-2], files[-1])
t2 = time.time()
print(f"Reassigned shared computations in {files[-2]} in {t2 - t1} seconds")

print("Reassigning variables...")
t1 = time.time()
files.append("out_files/newvars.cpp")
reassign_unused_vars(files[-2], files[-1])
t2 = time.time()
print(f"Reassigned variables in {files[-2]} in {t2 - t1} seconds")

print("Removing unused indices...")
t1 = time.time()
files.append("out_files/noskips2.cpp")
remove_unused_vars(files[-2], files[-1])
t2 = time.time()
print(f"Removed unused indices from {files[-2]} in {t2 - t1} seconds")

print("Adding vectorization...")
t1 = time.time()
files.append("out_files/poly-3b-v2x-new.cpp")
vectorize_indices(files[-2], files[-1])
t2 = time.time()
print(f"Vectorized {files[-2]} in {t2 - t1} seconds")

size1 = how_big_is_it(files[0])
size2 = how_big_is_it(files[-1])
print(f"All done! Number of variables used decreased from {size1} to {size2}. Now fix the rest of the file yourself stupid")
