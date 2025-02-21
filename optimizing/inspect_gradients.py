file_bad = "test_files/bad_gradients.txt"
file_good = "test_files/good_gradients.txt"

def gradient_dict(file_in):
    file = open(file_in, "r")
    contents = file.read()
    gg = contents.split(" , ")
    nd = len(gg) // 31

    gradients = []
    for i in range(31):
        gradients.append(gg[nd*i:nd*(i + 1) - 1])

    return gradients

bad_gradients = gradient_dict(file_bad)
good_gradients = gradient_dict(file_good)
gradient_diff = []

for i in range(31):
    diffs = []
    for j in range(len(bad_gradients[i])):
        badg = float(bad_gradients[i][j])
        goodg = float(good_gradients[i][j])
        d = 0 if abs(badg - goodg) < 1e-10 else badg - goodg
        diffs.append(d)

    gradient_diff.append(diffs)

for i in range(31):
    print(f"{i}: {gradient_diff[i]}")