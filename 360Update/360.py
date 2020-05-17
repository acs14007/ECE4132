import numpy as np
from PIL import Image
import time
import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from progress.bar import IncrementalBar
from multiprocessing import Process, Queue
import pickle
from scipy import ndimage
from scipy.linalg import blas


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
 
def AnglesToDistance(p1,p2,cameraDistance = 0.27305):
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

    dataType = np.ubyte
    image1data = np.array(image1,dtype=dataType)
    image2data = np.array(image2,dtype=dataType)
    
    
    # b = 0
    # while True:
    #     a = int(input("How much: "))
    #     b += a
    #     image2data = np.roll(image2data,-3*int(a))
    #     print(b)
    #     Image.fromarray(image2data).show()



    # image1data = np.roll(image1data,-3*(91))
    # image2data = np.roll(image2data,-3*(91+2896))
    image1data = np.roll(image1data,-3*(10))
    image2data = np.roll(image2data,-3*(-61+2896))
    outputData = np.array(image1data * 0,dtype=dataType)
    outputData = histogramEqualization(outputData)
    Image.fromarray(image1data).show()
    Image.fromarray(image2data).show()
    print("Images Equalized:",time.time()-startTime)
    
    #This is a slow way to compute the sobel filter and then adjust the values
    #It would be faster to use histogram modification to adjust the values
    #This is just easy to program and should be fixed
    edgeData = ndimage.sobel(np.mean(image1data,axis=2))
    shape = edgeData.shape
    edgeData = np.ndarray.tolist(edgeData.flatten())
    edgeData = np.reshape(np.array(list(map(lambda x: 0 if x < 0 else (255 if (x > 255) else (255 if (x > 50) else 0)),edgeData))),shape)
    print("Edge Data Computed:",time.time()-startTime)
    Image.fromarray(edgeData).show()
    input()

    stepSize        =   16
    sampleSizes     =   [120,140,160,180,200,225,250,275,300,350,400,450,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700]
    #sampleSizes     =   [120,140,160,180,200,225,250,275,300,350,400,450,500]
    sobelFactor     =   2000 #made up value 1530
    centerposition  =   (2896,0)
    # planesToCheck   =   np.array([400,300,200,100,75,50,25,20,15,10,8,7,6,5,4.5,4,3.5,3,2.5,2,1.6,1.3,1],dtype=dataType)
    planesToCheck   =   np.array([0.914,1.00,0.823])
    colours         =   np.array([[i,i,i] for i in range(0,255,int(255/len(planesToCheck)))],dtype=dataType)
    green           =   np.array([0,255,0])
    colours[0]      =   green
    statusBar       =   IncrementalBar("Image Lines",max = 5792,suffix = '%(index)d/%(max)d %(elapsed)s/%(eta_td)s')
    

    OUTPUTC = []
    # for _ in range(0,5792,stepSize):
    for i in [4550,20,20,20,20,20,20,20,20]:
        [statusBar.next() for _ in range(stepSize)]
        (centerposition,outputData,image1data,image2data) = shiftImages(centerposition,outputData,image1data,image2data,i)
        edgeData = np.roll(edgeData,stepSize)
        # for y in range(500,2397,stepSize):
        # for y in [1490,1470,1450,1430,1410,1390,1370,1350,1330,1310,1290,1270]:
        for y in range(1270,1490,20):
            placesToCheck = []
            relativeposition1 = (2896,y)# This is the current spot in image 1 we are looking at
            AbsolutePosition1 = (centerposition[0]-relativeposition1[0],y)# Offset from absolute top Center
            theta1 = pixelsToRadians(AbsolutePosition1[0]);phi1 = pixelsToRadians(AbsolutePosition1[1])
            #We must decide how large our sample size will be.
            h,j = 0,True
            while j:
                sampleSize = sampleSizes[h]
                edgeSquare = edgeData[relativeposition1[1]-sampleSize:relativeposition1[1]+sampleSize,relativeposition1[0]-sampleSize:relativeposition1[0]+sampleSize]
                sum = np.sum(edgeSquare,dtype = np.uint64)
                if sum >= (sobelFactor * sampleSize):j = False
                elif h == len(sampleSizes)-1:j = False
                h += 1 
            
            #image1data = Marker(image1data,[relativeposition1[1],relativeposition1[0]],sampleSize)
            square1 = image1data[relativeposition1[1]-sampleSize:relativeposition1[1]+sampleSize,relativeposition1[0]-sampleSize:relativeposition1[0]+sampleSize]
            L = math.tan(phi1) * math.sin(theta1)
            #Now we must generate the list of places to check Correlation
            Delta = np.array([100 for _ in planesToCheck],dtype=np.float64)
            placesToCheck = [(0,0) for _ in planesToCheck]
            for i in range(-250,250,1):
                try:
                    theta2 = pixelsToRadians(i + AbsolutePosition1[0])
                    phi2 = math.atan((L / math.sin(theta2)))
                    if phi2 < 0: phi2 += math.pi
                    distance = AnglesToDistance((theta1,phi1),(theta2,phi2))
                    image2data[radiansToPixels(phi2),centerposition[0]-radiansToPixels(theta2)] = [0,255,0]
                    if distance >= 0:
                        #print(distance)
                        # delta = np.abs(planesToCheck-distance)
                        placesToCheck.append((theta2,phi2))
                        # for h in range(planesToCheck.size):
                        #     if delta[h] < Delta[h]:
                        #         Delta[h] = delta[h]
                        #         placesToCheck[h] = (theta2,phi2)
                                #placesToCheck.append((theta2,phi2))
                except ZeroDivisionError:pass

            
            #We must go through the list of possible locations and calculate correlations
            #std2 = (np.sum(np.square(square2 - mean2,dtype=np.uint64)) / square1.size) ** 0.5
            #stdT = std1 * std2
            correlations = []
            mean1=np.mean(square1,dtype=np.float32)
            stdT = (np.mean(np.square(square1 - mean1,dtype=np.float32)))
            square1 = (square1 - mean1) / stdT
            for place in placesToCheck:
                AbsolutePosition2 = (centerposition[0]-radiansToPixels(place[0]),radiansToPixels(place[1]))
                square2 = image2data[AbsolutePosition2[1]-sampleSize:AbsolutePosition2[1]+sampleSize,AbsolutePosition2[0]-sampleSize:AbsolutePosition2[0]+sampleSize]
                if square2.size != square1.size:correlations.append(0)
                else:correlations.append(np.vdot(square1,(square2 - np.mean(square2,dtype=np.float32))))
           
            #Add distance to output Image
            a = correlations.index(max(correlations))
            bestMatch = placesToCheck[a]
            distance = AnglesToDistance((theta1,phi1),(bestMatch[0],bestMatch[1]))
            colour = [distance,distance,distance]
            print(distance)
            # colour = colours[np.argmin(np.abs(planesToCheck - distance))]
            outputData[relativeposition1[1]-int(stepSize/2):relativeposition1[1]+int(stepSize/2),relativeposition1[0]-int(stepSize/2):relativeposition1[0]+int(stepSize/2)] = colour
            image1data = Marker(image1data,[relativeposition1[1],relativeposition1[0]],20)
            image2data = Marker(image2data,[radiansToPixels(bestMatch[1]),centerposition[0]-radiansToPixels(bestMatch[0])],20)
            #image2data = Marker(image2data,[radiansToPixels(placesToCheck[40][1]),centerposition[0]-radiansToPixels(placesToCheck[40][0])],20)
            #image2data = Marker(image2data,[radiansToPixels(placesToCheck[366][1]),centerposition[0]-radiansToPixels(placesToCheck[366][0])],20)
    # print()
    # plt.plot(correlations)
    # plt.xlabel("Distance along epipolar line")
    # plt.ylabel("Normalized Cross Correlation") 
    # plt.tight_layout()  
    # plt.show()
    
    #outputData = histogramEqualization(outputData)
    Image.fromarray(image1data).save("1.JPG")
    Image.fromarray(image2data).save("2.JPG")
    Image.fromarray(outputData).save("Depth.JPG")

    endTime = time.time()
    print(endTime-startTime)


    #Changes
    #Changed all arrays to C data types
    #Rewrote functions that took a long time
    #Observe that the avergae differnce in standard deviation is about 0.40
    #Observe that we expect standard deviation for matches to be very similar
    #So we only calculate standard deviation for one square
    
