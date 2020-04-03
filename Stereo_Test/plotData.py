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

dataName = "output.pickle"
with open(dataName,'rb') as f:
    data = pickle.load(f)
    for i in data:
        AllData.append(np.array(i))
print("Data Imported and Converted")
for i in AllData:
    plt.plot(i)
    
plt.show()
input()