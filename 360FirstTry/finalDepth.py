import numpy as np
from PIL import Image
import time
import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from progress.bar import IncrementalBar
from multiprocessing import Process, Queue
import pickle

"""
    Written By Aaron Spaulding

    To speed up processing we use the PIL library in conjunction with numpy.
    Since we do not need to define our own flattening functions we omit the
    imaging.py file needed earlier.
"""

def Marker(data,location,width=100,color = [0,255,0]):
    for i in range(-width,width+1):
        for j in range(-width,width+1):
            if abs(j) == width or abs(i) == width:
                try:
                    data[location[0]+i,location[1]+j] = color
                except:pass
            else:pass
    return(data)

def shiftImages(currentPosition,image1,image2,image3,amount):
    """
        Amount should be in pixels
        Works for images that measure 5792x2896 with three colour channels
    """
    image1 = np.roll(image1,3*amount)
    image2 = np.roll(image2,3*amount)
    image3 = np.roll(image3,3*amount)
    currentPosition = (currentPosition[0] + amount,currentPosition[1])
    return((currentPosition,image1,image2,image3))

pixelsToRadians = lambda p : math.pi * p / 2896
radiansToPixels = lambda r : int(2896 * r / math.pi)
 
def AnglesToDistance(p1,p2,cameraDistance = 0.3):
    """
        Inputs two tuples of angles and outputs the distance from the camera 1 to the projected position
        p1 and p2 should be tuples of elements theta and phi
    """
    alpha1 = math.acos(math.sin(p1[1])*math.cos(p1[0]))
    alpha2 = math.acos(-math.sin(p2[1])*math.cos(p2[0]))
    distance = (cameraDistance * math.sin(alpha2)) / (math.sin(alpha2 + alpha1))
    return(distance)

def histogramEqualization(image):
    # http://www.janeriksolem.net/2009/06/histogram-equalization-with-python-and.html
    R = image[:,:,0]
    G = image[:,:,1]
    B = image[:,:,2]
    s = image.shape
    
    image_histogramR, binsR = np.histogram(R.flatten(), 256, density=True)
    image_histogramG, binsG = np.histogram(G.flatten(), 256, density=True)
    image_histogramB, binsB = np.histogram(B.flatten(), 256, density=True)
    cdfR = image_histogramR.cumsum() # cumulative distribution function
    cdfG = image_histogramG.cumsum()
    cdfB = image_histogramB.cumsum()
    cdfR = 255 * cdfR / cdfR[-1] # normalize
    cdfG = 255 * cdfG / cdfG[-1]
    cdfB = 255 * cdfB / cdfB[-1]
    image_equalizedR = np.interp(R.flatten(), binsR[:-1], cdfR)
    image_equalizedG = np.interp(G.flatten(), binsG[:-1], cdfG)
    image_equalizedB = np.interp(B.flatten(), binsB[:-1], cdfB)
    ImageOut = np.column_stack((image_equalizedR,image_equalizedG,image_equalizedB)).astype("uint8")
    ImageOut = ImageOut.reshape(s)
    return(ImageOut)

if __name__ == "__main__":
    startTime = time.time()
    image1 = Image.open("aisle1sphere_pano.jpg")
    image2 = Image.open("aisle2sphere_pano.jpg")
    print("Images Imported:", time.time()-startTime)

    image1data = np.array(image1)
    image2data = np.array(image2)
    image1data = np.roll(image1data,-3*(91))
    #image2data = np.roll(image2data,-3*(91))
    image2data = np.roll(image2data,-3*(91+2896))
    outputData = image1data * 0
    outputData = histogramEqualization(outputData)
    #image1data = histogramEqualization(image1data)
    #image2data = histogramEqualization(image2data)
    print("Images Equalized:",time.time()-startTime)

    stepSize        =   128
    sampleSize      =   400
    centerposition  =   (2896,0)
    planesToCheck   =   np.array([400,300,200,5,4,3])
    statusBar = IncrementalBar("Image Lines",max = 5792,suffix = '%(index)d/%(max)d %(elapsed)s/%(eta_td)s')
    
    OUTPUTC = []
    #for _ in range(0,5792,stepSize):
    for _ in [1]:
        [statusBar.next() for _ in range(stepSize)]
        (centerposition,outputData,image1data,image2data) = shiftImages(centerposition,outputData,image1data,image2data,1400)
        #for y in range(500,2397,stepSize):
        for y in [700]:
            placesToCheck = []
            relativeposition1 = (2896,y)# This is the current spot in image 1 we are looking at
            AbsolutePosition1 = (centerposition[0]-relativeposition1[0],y)# Offset from absolute top Center
            theta1 = pixelsToRadians(AbsolutePosition1[0])
            phi1 = pixelsToRadians(AbsolutePosition1[1])
            #alpha1 = math.acos(math.sin(phi1)*math.cos(theta1))
            square1 = image1data[relativeposition1[1]-sampleSize:relativeposition1[1]+sampleSize,relativeposition1[0]-sampleSize:relativeposition1[0]+sampleSize]
            L = math.tan(phi1) * math.sin(theta1)

            #Now we must generate the list of places to check Correlation
            Delta = np.array([100 for _ in planesToCheck])
            placesToCheck = [(0,0) for _ in planesToCheck]
            k = []
            for i in range(-400,100,1):
                try:
                    theta2 = pixelsToRadians(i + AbsolutePosition1[0])
                    phi2 = math.atan((L / math.sin(theta2)))
                    if phi2 < 0: phi2 += math.pi
                    distance = AnglesToDistance((theta1,phi1),(theta2,phi2))
                    if distance >= 0:
                        k.append(distance)
                        delta = np.abs(planesToCheck-distance)
                        for h in range(planesToCheck.size):
                            if delta[h] < Delta[h]:
                                Delta[h] = delta[h]
                                placesToCheck[h] = (theta2,phi2)
                                #placesToCheck.append((theta2,phi2))
                except ZeroDivisionError:pass
            k = k[1:]
            plt.plot(np.array(k))
            plt.xlabel("Pixel Shift")
            plt.ylabel("Calculated Distance(m)") 
            plt.show()
            input()
            
            #We must go through the list of possible locations and calculate correlations
            correlations = []
            for place in placesToCheck:
                AbsolutePosition2 = (centerposition[0]-radiansToPixels(place[0]),radiansToPixels(place[1]))
                try:image2data[radiansToPixels(phi2),AbsolutePosition2[0]] = [0,255,0]
                except IndexError:pass
                try:
                    square2 = image2data[AbsolutePosition2[1]-sampleSize:AbsolutePosition2[1]+sampleSize,AbsolutePosition2[0]-sampleSize:AbsolutePosition2[0]+sampleSize]
                    distance = AnglesToDistance((theta1,phi1),(place[0],place[1]))
                    mean1=np.mean(square1)
                    mean2=np.mean(square2)
                    std1 = np.std(square1)
                    std2 = np.std(square2)
                    square1 = ((square1 - mean1) / std1) * ((square2 - mean2) / std2)
                    correlations.append(np.sum(square1))
                    # correlations.append(np.sum(square1*square2))
                except:
                    correlations.append(0)
            
                #except ValueError:correlations.append(10000000000)
            #OUTPUTC.append(np.array(correlations))
            #Now we must find the best fit
            a = correlations.index(max(correlations))
            bestMatch = placesToCheck[a]
            image1data = Marker(image1data,[relativeposition1[1],relativeposition1[0]],20)
            image2data = Marker(image2data,[relativeposition1[1],relativeposition1[0]],20,color=[255,0,0])
            image2data = Marker(image2data,[radiansToPixels(bestMatch[1]),centerposition[0]-radiansToPixels(bestMatch[0])],20)
            distance = AnglesToDistance((theta1,phi1),(bestMatch[0],bestMatch[1]))
            outputData[relativeposition1[1]-int(stepSize/2):relativeposition1[1]+int(stepSize/2),relativeposition1[0]-int(stepSize/2):relativeposition1[0]+int(stepSize/2)] = [distance,distance,distance]
            #print(y)
    print()
    
    
    outputData = histogramEqualization(outputData)
    Image.fromarray(image1data).save("1.JPG")
    Image.fromarray(image2data).save("2.JPG")
    Image.fromarray(outputData).save("Depth.JPG")

    endTime = time.time()
    print(endTime-startTime)


    # AllData = []
    # for i in OUTPUTC:
    #     #window = np.ones(20) / 20
    #     #iSmooth = np.convolve(i,window,mode='valid')
    #     AllData.append(i)

    # for i in AllData:
    #     plt.plot(i)
    # plt.show()
    #input()