# To read the npy file which store the values after attenuation etc
# the same thing is stored in csv file after reshaping -- see main.py (after tissue interaction) -
 
import os
import sys
# python_dir = sys.prefix  # Points to your active Python folder
python_dir = r"C:\Users\Sridhar\AppData\Local\Programs\Python\Python313"   # r helps in avoid interpreting \ as backslashes
os.environ['TCL_LIBRARY'] = os.path.join(python_dir, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(python_dir, 'tcl', 'tk8.6')

import numpy as np


import matplotlib.pyplot as plt

file_path = "photon_output/view_2_detector.npy"

detector_image = np.load(file_path)

print(detector_image.shape)
rows,columns = detector_image.shape


# ---------------
# Cross check with csv
# -------------------
check_val = 525275.06
ray_id_csv = 0
exit = False  # to break both the loops 
for i in range(rows):  # 64 in number
    for j in range(columns): # 888 in number
        ray_id_csv += 1 # increment to match and check with the csv 
        if detector_image[i][j] < check_val:
            print(f"The value at ({i},{j}) is {detector_image[i][j]} which corresponds to {ray_id_csv - 1}")
            exit = True
            break
        
        if exit:
            break




plt.figure(figsize=(12, 6))

plt.imshow(
    detector_image,
    aspect="auto"
)

plt.colorbar(label="Detector Signal")

plt.xlabel("Detector Channel")
plt.ylabel("Detector Row")
plt.title("Detector Image - View 1")

# plt.show()