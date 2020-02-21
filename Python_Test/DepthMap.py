from imaging import *
import time

#We will just deal with the red channel for simplicity.
#We need to define a new function to define cross correlation
#Since this is just a test we will just use it on the linear data
#This can be optimized in two ways; by tracing the image in a Hilbert Curve
#Or by doing it in 2D. The Hilbert curve approach should be more simple to write
#With the same results


"""
We want to find each offset for each pixel, this is vertical and horizontal
however we are just going to calculate the horizontal for now. We check
The correlation between sequences of 31 pixels.
See: http://www.cse.psu.edu/~rtc12/CSE486/lecture07.pdf
"""

def SSD(image1,image2,pixelNumber1,pixelNumber2,width):
    """
    Function calculates the Sum of Squared Differences between two given lists
    See slide 26 of http://www.cse.psu.edu/~rtc12/CSE486/lecture07.pdf
    This was sped up by removing the square and replacing with abs()
    Unrolling the for loop also helped speed this up marginally.
        for j in range(-a,a+1):
        for i in range(-a,a+1):
            total += abs(image1.Rlist[pixelNumber1+i+(image1.size[0]*j)] - image2.Rlist[pixelNumber2+i+(image2.size[0]*j)])
    """
    total =(abs(image1.Rlist[pixelNumber1-1-(image1.size[0])] - image2.Rlist[pixelNumber2-1-(image2.size[0])])
    + abs(image1.Rlist[pixelNumber1+0-(image1.size[0])] - image2.Rlist[pixelNumber2+0-(image2.size[0])])
    + abs(image1.Rlist[pixelNumber1+1-(image1.size[0])] - image2.Rlist[pixelNumber2+1-(image2.size[0])])
    + abs(image1.Rlist[pixelNumber1-1] - image2.Rlist[pixelNumber2-1])
    + abs(image1.Rlist[pixelNumber1+0] - image2.Rlist[pixelNumber2+0])
    + abs(image1.Rlist[pixelNumber1+1] - image2.Rlist[pixelNumber2+1])
    + abs(image1.Rlist[pixelNumber1-1+(image1.size[0])] - image2.Rlist[pixelNumber2-1+(image2.size[0])])
    + abs(image1.Rlist[pixelNumber1+0+(image1.size[0])] - image2.Rlist[pixelNumber2+0+(image2.size[0])])
    + abs(image1.Rlist[pixelNumber1+1+(image1.size[0])] - image2.Rlist[pixelNumber2+1+(image2.size[0])]))
    return(total)

def checkCenterOffset(photo1,photo2,width=3):
    """
        This function calculates the offset of the images from the center
        of the left. Checking this can help accelerate later measurements
        since we can assume other offsets will be similar
        We first find the center of the images, then we measure the SSD
        between samples until the images line up. Our window size may be
        adjusted to make this quicker or more accurate.
        We do not need to compensate for photo differences since the cameras are identical
    """
    centerPoint = int(int(photo1.length / 2)-(photo1.size[0]/2))
    bestMatch = [10000000,0]
    searchWindowWidth = 40
    for pixel in range(centerPoint-searchWindowWidth-200,centerPoint-200+searchWindowWidth + 1,1):
        h = SSD(photo1,photo2,centerPoint,pixel,width)
        if h < bestMatch[0]:bestMatch = [h,pixel]
    return((centerPoint,bestMatch[1],bestMatch[0]))

def Correlate(photo1,photo2,location,centerOffset,width=3):
    """
        This function finds a matching position of photo2 given a point in photo1.
        The centerOffset must be defined.
    """
    bestMatch = [10000000,0]
    searchWindowWidth = 3 #We do not expect it to be too far away from where we predict
    #Assume photos are vertically aligned
    for pixel in range(location-searchWindowWidth-centerOffset,location+searchWindowWidth-centerOffset):
        h = SSD(photo1,photo2,location,pixel,width)
        if h < bestMatch[0]:bestMatch = [h,pixel]
    return((location,bestMatch[1],bestMatch[0],location-bestMatch[1]))

def Marker(data,location,photoWidth,width=10):
    """
        This function can be used to mark an area on an image
        Draws a green box arround the location.
    """
    a = int(width / 2)
    for j in range(-a,a+1):
        for i in range(-a,a+1):
            if abs(j) == a or abs(i) == a:
                data[location + i + (photoWidth * j)] = (0,245,0)
            else:pass
    return(data)

def depthMap(PhotoL,PhotoR,output):
    """
        We assume the photos are vertically matched
    """
    #Calculate the centerOffset of the right from the left
    centerOffset = checkCenterOffset(PhotoL,PhotoR)
    #We correlate all points in PhotoL for PhotoR we save distance from expected
    #Left Photo is padded 250 pixels in all directions.
    k = time.time()
    output = output
    for i in range(500,PhotoL.size[0]-500+1,3):
        for j in range(500,PhotoL.size[1]-500+1,3):
            position = i + (j * PhotoL.size[0])
            a = Correlate(PhotoL,PhotoR,position,centerOffset[0]-centerOffset[1])
            output[position + -1 - PhotoL.size[0]] =    int(4*a[3]+4)
            output[position + -1] =                     int(4*a[3]+4)
            output[position + -1 + PhotoL.size[0]] =    int(4*a[3]+4)
            output[position - PhotoL.size[0]] =         int(4*a[3]+4)
            output[position] =                          int(4*a[3]+4)
            output[position + PhotoL.size[0]] =         int(4*a[3]+4)
            output[position + 1 - PhotoL.size[0]] =     int(4*a[3]+4)
            output[position + 1] =                      int(4*a[3]+4)
            output[position + 1 + PhotoL.size[0]] =     int(4*a[3]+4)
        print(i)
    l = time.time()
    print(l-k)
    return(output)





if __name__ == "__main__":
    a =time.time();print("Starting")
    PhotoL = photo("left.png");PhotoR = photo("right.png")
    PhotoL.flattenChannels();PhotoR.flattenChannels()  
    emptyList = [0 for i in range(0,PhotoL.size[0]* PhotoL.size[1])]
    outputl = Image.new(PhotoL.mode,PhotoL.size,color=0)
    outputr = Image.new(PhotoL.mode,PhotoL.size,color=0)
    depthphoto = Image.new(PhotoL.mode,PhotoL.size,color=0)
    b=time.time();print("Images Imported: ", b-a)
    
    depthData = depthMap(PhotoL,PhotoR,emptyList)
    outputDepth = combineChannelsList(depthData,emptyList,emptyList)
    depthphoto.putdata(outputDepth)
    depthphoto.save("depth.png")
    
    """
    centerOffset = checkCenterOffset(PhotoL,PhotoR)
    chosenPixelr = centerOffset[1]
    chosenPixell = centerOffset[0]
    c=time.time();print("Found and marked center uniformity: ",c-b)

    outputDatal = combineChannelsList(PhotoL.Rlist,emptyList,emptyList)
    outputDatar = combineChannelsList(PhotoR.Rlist,emptyList,emptyList)

    outputDatal = Marker(outputDatal,chosenPixell,PhotoL.size[0])
    outputDatar = Marker(outputDatar,chosenPixelr,PhotoR.size[0])

    outputl.putdata(outputDatal)
    outputl.save("outputl.png")
    outputr.putdata(outputDatar)
    outputr.save("outputr.png")
    d = time.time();print("Photos Exported: ",d-c)
    print("Total Time: ",d-a)
    """