import numpy as np
from PIL import Image
import time
import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from progress.bar import IncrementalBar
from multiprocessing import Process, Queue
import pickle

AllData = []

dataName = "SS10.pickle"
with open(dataName,'rb') as f:
    data = pickle.load(f)
    data = np.array(data)
    mean = np.mean(data)
    data = data/mean
    AllData.append(data)
dataName = "SS40.pickle"
with open(dataName,'rb') as f:
    data = pickle.load(f)
    data = np.array(data)
    mean = np.mean(data)
    data = data/mean
    AllData.append(data)
dataName = "SS800.pickle"
with open(dataName,'rb') as f:
    data = pickle.load(f)
    data = np.array(data)
    mean = np.mean(data)
    data = data/mean
    AllData.append(data)
print("Data Imported and Converted")

for i in AllData:
    plt.plot(i)

plt.legend(('10 Pixels Wide', '40 Pixels Wide', '800 Pixels Wide'))
plt.xlabel("Distance along epipolar line")
plt.ylabel("Mean normalized sum of squared differences")
plt.show()
input()