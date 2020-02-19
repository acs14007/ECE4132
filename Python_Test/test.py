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

def getBlock(image,pixelNumber,width):
    """
    This function gets the list for the pixels contained in the image
    centered at the pixel chosen with width specified. Width should be 
    even.
    """
    a = int(width/2)
    output=[]
    for j in range(-a,a):
        for i in range(-a,a):
            output.append(image[pixelNumber+i+(2964*j)])
    return(output)

def SSD(block1,block2):
    """
    Function calculates the Sum of Squared Differences between two given lists
    See slide 26 of http://www.cse.psu.edu/~rtc12/CSE486/lecture07.pdf
    """
    total = 0
    for i in range(len(block1)):total += (block2[i] - block1[i]) ** 2
    return(total)


def checkCenterOffset(photo1,photo2,width=40):
    """
        This function calculates the offset of the images from the center
        of the left. Checking this can help accelerate later measurements
        since we can assume other offsets will be similar
        We first find the center of the images, then we measure the SSD
        between samples until the images line up. Our window size may be
        adjusted to make this quicker or more accurate.
    """
    if photo1.length != photo2.length: raise Exception("Uneven dimension")
    centerPoint = int(int(photo1.length / 2)-(photo1.size[0]/2))
    a = getBlock(photo1.Rlist,centerPoint,width)
    values = []
    searchWindowWidth = 250
    for i in range(centerPoint-searchWindowWidth,centerPoint-100):
        for j in range(-5,5):#We assume small veritcal offset
            h=i+(j*photo1.size[0])
            b = getBlock(photo2.Rlist,h,width)
            values.append((SSD(a,b),h))
    values = sorted(values)
    return(values)


    
if __name__ == "__main__":
    chosenPixell = 2962518
    a =time.time();print("Starting")
    PhotoL = photo("left.png");PhotoR = photo("right.png")
    PhotoL.flattenChannels();PhotoR.flattenChannels()  
    emptyList = [0 for i in range(0,PhotoL.size[0]* PhotoL.size[1])]
    outputl = Image.new(PhotoL.mode,PhotoL.size,color=0)
    outputr = Image.new(PhotoL.mode,PhotoL.size,color=0)
    b=time.time();print("Images Imported: ", b-a)
    #Find Center Point Here and Label it in the right photo
    print("Checking center Offset")
    values = checkCenterOffset(PhotoL,PhotoR)
    chosenPixelr = values[0][1]
    
    Markerl = [i for i in emptyList]
    for j in range(-20,20):
        for i in range(-20,20):
            Markerl[chosenPixell+i-(2964*j)] = 240
    Markerr = [i for i in emptyList]
    for j in range(-20,20):
        for i in range(-20,20):
            Markerr[chosenPixelr+i-(2964*j)] = 240
    
    c=time.time();print("Found and marked center uniformity: ",c-b)
    outputDatal = combineChannelsList(PhotoL.Rlist,Markerl,emptyList)
    outputDatar = combineChannelsList(PhotoR.Rlist,Markerr,emptyList)

    outputl.putdata(outputDatal)
    outputl.save("outputl.png")
    outputr.putdata(outputDatar)
    outputr.save("outputr.png")
    d = time.time();print("Photos Exported: ",d-c)
    print("Total Time: ",d-a)
