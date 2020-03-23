import numpy as np
from PIL import Image
import time
import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from progress.bar import IncrementalBar

"""
    To speed up processing we use the PIL library in conjunction with numpy.
    Since we do not need to define our own flattening functions we omit the
    imaging.py file needed earlier.
"""

def Marker(data,location,width=100,color = [0,255,0]):
    for i in range(-width,width+1):
        for j in range(-width,width+1):
            if abs(j) == width or abs(i) == width:
                data[location[0]+i,location[1]+j] = color
            else:pass
    return(data)

def SSD(square1,square2):
    """
        Inputs two numpy arrays that are the same size and outputs the SSD
        Simplified by reducing square root to absolute value
    """
    try:
        square1 = np.absolute(square1-square2)
    except ValueError:
        pass
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
        Inputs two tuples of angles and outputs the distanct from the camera 1 to the projected position
        p1 and p2 should be tuples of elements theta and phi
    """
    alpha1 = math.acos(math.sin(p1[1])*math.cos(p1[0]))
    alpha2 = math.acos(-math.sin(p2[1])*math.cos(p2[0]))
    #print(alpha1,alpha2)
    if alpha1+alpha2 <= math.pi:pass
    distance = (cameraDistance * math.sin(alpha2)) / (math.sin(alpha2 + alpha1))
    return(distance)

def inList(value,list,error):
    """
        list should be a numpy 1D array
    """
    list = abs(list - value)
    for i in list:
        if i <= error:
            return(True)
        else:pass
    return(False)


def histogramEqualization(image):
    R = image1data[:,:,0]
    G = image1data[:,:,1]
    B = image1data[:,:,2]
    s = image.shape
    # # from http://www.janeriksolem.net/2009/06/histogram-equalization-with-python-and.html
    
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
    #We first import the two photos.
    image1 = Image.open("lab1sphere_pano.jpg")
    image2 = Image.open("lab1sphere_pano.jpg")
    print("Images Imported:", time.time()-startTime)

    #We now convert the images to numpy arrays.
    #numpy arrays are faster and take less memory than python lists
    image1data = np.array(image1)
    image2data = np.array(image2)

    #We now center the images
    #We know the offset from manual calibration 91 pixels for the aisle image
    #We should automate this so the center point can be calculated faster.
    #This is a TO-DO item
    image1data = np.roll(image1data,-3*(91))
    image2data = np.roll(image2data,-3*(91+2896))
    outputData = image1data * 0
    
    #We now histogram equalize input data
    image1data = histogramEqualization(image1data)
    image2data = histogramEqualization(image2data)
    print("Images Equalized:",time.time()-startTime)



    centerposition = (2896,1448)
    #16.10.1147
    #[0.33,0.66,1,1.33,1.66,2,2.33,2.66,3]
    stepSize = 16#Should be even Smaller is more resolution
    sampleSize = 10#Tuning parameter Width of squares
    statusBar = IncrementalBar("Image Lines",max = 5792,suffix = '%(index)d/%(max)d [%(elapsed)d / %(eta)d / %(eta_td)s]')
    for columns in range(0,5793,stepSize):
        [statusBar.next() for i in range(stepSize)]
        (centerposition,outputData,image1data,image2data) = shiftImages(centerposition,outputData,image1data,image2data,stepSize)
        for y in range(400,2496,stepSize):
            relativeposition = (2896,y)
            pixelPosition = (centerposition[0]-relativeposition[0],relativeposition[1]-centerposition[1])    
            theta1 = pixelsToRadians(pixelPosition[0])
            phi1 = pixelsToRadians(pixelPosition[1])
            L = math.sin(phi1) * math.sin(theta1) / math.cos(phi1)
            areaToCheck = list(range(-600,600,1))
            placesToCheck = []
            distances = np.array([0.33,0.66,1,1.33,1.66,2,2.33,2.66,3])
            for i in areaToCheck:
                try:
                    theta2 = pixelsToRadians(i + pixelPosition[0])
                    phi2 = math.atan((L / math.sin(theta2)))
                    distance = AnglesToDistance((theta1,phi1),(theta2,phi2))
                    #print(theta2,phi2)
                    if distance < 3 and distance > 0.3:
                    #if inList(distance,distances,0.09):
                        placesToCheck.append((theta2,phi2))
                    else:pass
                except ZeroDivisionError:pass
                #image2data[1447-radiansToPixels(phi2),centerposition[0] - radiansToPixels(theta2)] = [0,255,0]
            #Image.fromarray(image2data).show()
            #image1data = Marker(image1data,[2896 - relativeposition[1],relativeposition[0]],16)

            x1,y1 = centerposition[0]-radiansToPixels(theta1),1447-radiansToPixels(phi1)
            square1 = image1data[y1-sampleSize:y1+sampleSize,x1-sampleSize:x1+sampleSize]
            bestMatch = [10000000,(0,0)]
            alpha1 = math.acos(math.sin(phi1)*math.cos(theta1))
            for i in placesToCheck:
                x2,y2 = centerposition[0]-radiansToPixels(i[0]),1447-radiansToPixels(i[1])
                p2 = (i[0],i[1])
                alpha2 = math.acos(-math.sin(p2[1])*math.cos(p2[0]))
                #print(alpha1,alpha2)
                square2 = image2data[y2-sampleSize:y2+sampleSize,x2-sampleSize:x2+sampleSize]
                if alpha1+alpha2 <= math.pi:
                    distance = (0.3 * math.sin(alpha2)) / (math.sin(alpha2 + alpha1))
                    #print(distance)
                    try:
                        square2 = np.absolute(square1-square2)
                        #square2 = np.sum(square1*square2)
                    except ValueError:
                        pass
                    h = np.sum(square2)
                else:h = 10000000
                if h < bestMatch[0]:
                    bestMatch = [h,(x2,y2)]
            #image1data = Marker(image1data,[y1,x1],8)
            #image2data = Marker(image2data,[bestMatch[1][1],bestMatch[1][0]],8)
            p2 = (pixelsToRadians(centerposition[0]-bestMatch[1][0]),pixelsToRadians(1447-bestMatch[1][1])) 
            distance = AnglesToDistance((theta1,phi1),p2)
            #print(distance)
            if distance <= 4:
                distance = round(distance)
                distance = 60 * distance
            else:distance = 255
            p1 = 1447-radiansToPixels(phi1)
            p2 = centerposition[0] - radiansToPixels(theta1)
            outputData[p1-int(stepSize/2):p1+int(stepSize/2),p2-int(stepSize/2):p2+int(stepSize/2)] = [distance,distance,distance]

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
    Image.fromarray(image1data).save("1.JPG")
    Image.fromarray(image2data).save("2.JPG")
    Image.fromarray(outputData).save("Depth.JPG")

    endTime = time.time()
    print(endTime-startTime)