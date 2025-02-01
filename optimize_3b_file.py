import time

from computations import reassign_shared_computations
from fix_indices import vectorize_indices
from liveness_analysis import reassign_unused_vars
from remove_a_assignments import remove_assignments
from remove_newlines import remove_newlines
from remove_unused import remove_unused_vars
from howBIGisit import how_big_is_it

print("Removing newlines...")
t1 = time.time()
file1 = "poly-2b-v6x-old.cpp"
file2 = "nobreaks.cpp"
remove_newlines(file1, file2)
t2 = time.time()
print(f"Removed newlines from {file1} in {t2 - t1} seconds")

print("Removing a assigments...")
t1 = time.time()
file3 = "noaassignments.cpp"
remove_assignments(file2, file3, "a")
t2 = time.time()
print(f"Removed a assignments from {file2} in {t2 - t1} seconds")

print("Removing unused indices...")
t1 = time.time()
file4 = "noskips.cpp"
remove_unused_vars(file3, file4)
t2 = time.time()
print(f"Removed unused indices from {file3} in {t2 - t1} seconds")

print("Reassigning shared computations (pass 1)...")
t1 = time.time()
file5 = "sharedcomps.cpp"
reassign_shared_computations(file4, file5)
print("Reassigning shared computations (pass 2)...")
file6 = "sharedcomps2.cpp"
reassign_shared_computations(file5, file6)
t2 = time.time()
print(f"Reassigned shared computations in {file4} in {t2 - t1} seconds")

print("Reassigning variables...")
t1 = time.time()
file7 = "newvars.cpp"
reassign_unused_vars(file6, file7)
t2 = time.time()
print(f"Reassigned variables in {file6} in {t2 - t1} seconds")

print("Removing unused indices...")
t1 = time.time()
file8 = "noskips2.cpp"
remove_unused_vars(file7, file8)
t2 = time.time()
print(f"Removed unused indices from {file7} in {t2 - t1} seconds")

print("Adding vectorization...")
t1 = time.time()
file9 = "poly-2b-v6x-new.cpp"
vectorize_indices(file8, file9)
t2 = time.time()
print(f"Vectorized {file8} in {t2 - t1} seconds")

size1 = how_big_is_it(file1)
size2 = how_big_is_it(file9)
print(f"All done! Number of variables used decreased from {size1} to {size2}. Now fix the rest of the file yourself stupid")
