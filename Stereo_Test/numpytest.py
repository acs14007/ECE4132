import numpy as np
from PIL import Image
import time

"""
    To speed up processing we use the PIL library in conjunction with numpy.
    Since we do not need to define our own flattening functions we omit the
    imaging.py file needed earlier.
"""

def Marker(data,location,width=100):
    for i in range(-width,width+1):
        for j in range(-width,width+1):
            if abs(j) == width or abs(i) == width:
                data[location[0]+i,location[1]+j] = [0,245,0]
            else:pass
    return(data)

def SSD(square1,square2):
    """
        Inputs two numpy arrays that are the same size and outputs the SSD
        Simplified by reducing square root to absolute value
    """
    square1 = np.absolute(square1-square2)
    return(np.sum(square1))

def CC(square1,square2):
    """
        Inputs two numpy arrays that are the same size and outputs the Cross Correlation
    """
    return(np.sum(square1*square2))

def NCC(square1,square2):
    """
        Input two same sized numpy arrays and outputs normalized cross correlation
        Simplified by omitting divide by number of elements since we are only comparing squares of the same size
    """
    mean1=np.mean(square1)
    mean2=np.mean(square2)
    std1 = np.std(square1)
    std2 = np.std(square2)
    square1 = ((square1 - mean1) / std1) * ((square2 - mean2) / std2)
    return(np.sum(square1))


def CorrelatePoint(square1,image2,location):
    height = int(len(square1)/2)
    width = int(len(square1[0])/2)
    bestMatch = [10000000,[0,0]]
    for i in range(-150,150):
        for j in range(-150,150):
            square2 = image2[location[0]+i-width:location[0]+i+width,location[1]+j-height:location[1]+j+height]
            h = SSD(square1,square2)
            if h < bestMatch[0]:
                bestMatch = [h,[location[0]+i,location[1]+j]]
    return(bestMatch[1])

if __name__ == "__main__":
    startTime = time.time()

    #We first import the two photos.
    image1 = Image.open("aisle1sphere_pano.jpg")
    image2 = Image.open("aisle2sphere_pano.jpg")
    print("Images Imported:", time.time()-startTime)

    #We now convert the images to numpy arrays.
    #numpy arrays are faster and take less memory than python lists
    image1data = np.array(image1)
    image2data = np.array(image2)

    #We now center the images
    #We know the offset from manual calibration 91 pixels for the aisle image
    #We should automate this so the center point can be calculated faster.
    #This is a TO-DO item
    centeredimage1data = np.roll(image1data,-3*(91+724))
    centeredimage2data = np.roll(image2data,-3*(91+2896+724))
    outputData = centeredimage1data * 0


    # trimPoint = [1448,2596]
    # width = 100
    # trimmedData1 = centeredimage1data[trimPoint[0]-width:trimPoint[0]+width,trimPoint[1]-width:trimPoint[1]+width]

    # y = time.time()
    # a = CorrelatePoint(trimmedData1,centeredimage2data,trimPoint)
    # print(time.time()-y)
    # centeredimage1data = Marker(centeredimage1data,trimPoint,width)
    # centeredimage2data = Marker(centeredimage2data,a,width)
    # print(trimPoint)
    # print(a)

    # for i in range(800,2096,200):
    #     print(i)
    #     trimPoint = [i,2596]
    #     width = 100
    #     trimmedData1 = centeredimage1data[trimPoint[0]-width:trimPoint[0]+width,trimPoint[1]-width:trimPoint[1]+width]
    #     a = CorrelatePoint(trimmedData1,centeredimage2data,trimPoint)
    #     centeredimage1data = Marker(centeredimage1data,trimPoint,width)
    #     centeredimage2data = Marker(centeredimage2data,a,width)
    Image.fromarray(centeredimage1data).show("test9P1.JPG")
    Image.fromarray(centeredimage2data).show("test9P2.JPG")
    
    endTime = time.time()
    print(endTime-startTime)