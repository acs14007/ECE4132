from imaging import *
import time
import multiprocessing

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


def SSD2(image1,image2):
    """
    Function calculates the Sum of Squared Differences between two given lists
    See slide 26 of http://www.cse.psu.edu/~rtc12/CSE486/lecture07.pdf
    This was sped up by removing the square and replacing with abs()
    Unrolling the for loop also helped speed this up marginally.
        for j in range(-a,a+1):
        for i in range(-a,a+1):
            total += abs(image1.Rlist[pixelNumber1+i+(image1.size[0]*j)] - image2.Rlist[pixelNumber2+i+(image2.size[0]*j)])
    """
    total =     abs(image1[0]-image2[0])
    + abs(image1[1]-image2[1])
    + abs(image1[2]-image2[2])
    + abs(image1[3]-image2[3])
    + abs(image1[4]-image2[4])
    + abs(image1[5]-image2[5])
    + abs(image1[6]-image2[6])
    + abs(image1[7]-image2[7])
    + abs(image1[8]-image2[8])
    return(total)

def SSD3(image1,image2,pixelNumber1,pixelNumber2,width):
    """
    Function calculates the Sum of Squared Differences between two given lists
    See slide 26 of http://www.cse.psu.edu/~rtc12/CSE486/lecture07.pdf
    This was sped up by removing the square and replacing with abs()
    Unrolling the for loop also helped speed this up marginally.
    """ 
    total = 0
    a = int(width / 2)
    for j in range(-a,a+1):
        for i in range(-a,a+1):
            total += abs(image1.Rlist[pixelNumber1+i+(image1.size[0]*j)] - image2.Rlist[pixelNumber2+i+(image2.size[0]*j)])
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
    searchWindowWidth = 200
    for pixel in range(centerPoint-searchWindowWidth,centerPoint+searchWindowWidth + 1,1):
        h = SSD(photo1,photo2,centerPoint,pixel,width)
        if h < bestMatch[0]:bestMatch = [h,pixel]
    return((centerPoint,bestMatch[1],bestMatch[0]))

def Correlate(photo1,photo2,location,centerOffset,width=3):
    """
        This function finds a matching position of photo2 given a point in photo1.
        The centerOffset must be defined.
    """
    bestMatch = [10000000,0]
    searchWindowWidth = 150
    for pixel in range(location-200,location-50):
        h = SSD3(photo1,photo2,location,pixel,width)
        if h < bestMatch[0]:bestMatch = [h,pixel]
    return((location,bestMatch[1],bestMatch[0],abs(location-bestMatch[1])))

def Correlate1(photo1,photo2,location,offsetMax=400,offsetMin=0,step=3,width=3):
    bestMatch = [1000000000000,0]
    for pixel in range(location-offsetMax,location-offsetMin,step):
        h = SSD(photo1,photo2,location,pixel,width)
        if h < bestMatch[0]:bestMatch = [h,pixel]
    return((location,bestMatch[1],bestMatch[0],abs(location-bestMatch[1])))

def Correlate2(photo1,photo2,location,offsetMax=400,offsetMin=0,step=3):
    bestMatch = [1000000000000,0]
    for pixel in range(location-250,location-50,step):
        h = SSD1(photo1,photo2,location,pixel)
        if h < bestMatch[0]:
            bestMatch = [h,pixel]
    return((location,bestMatch[1],bestMatch[0],abs(location-bestMatch[1])))

def Correlate4(photo1,photo2,location,centerOffset,pool,width=3):
    bestMatch = [10000000,0]
    #Assume photos are vertically aligned
    #for pixel in range(location-searchWindowWidth-centerOffset,location+searchWindowWidth-centerOffset):
    a = getBlock(photo1.Rlist,location,3)
    b = range(location-200,location-50)
    results = [pool.apply(SSD2,args=[a,getBlock(photo2.Rlist,pixel,3)]) for pixel in b]
    c = results.index(min(results))
    return((location,b[c],results[c],abs(location-b[c])))

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
    #pool = multiprocessing.Pool(8)
    #Calculate the centerOffset of the right from the left
    centerOffset = checkCenterOffset(PhotoL,PhotoR)
    #We correlate all points in PhotoL for PhotoR we save distance from expected
    #Left Photo is padded 250 pixels in all directions.
    k = time.time()
    output = output
    for i in range(200,PhotoL.size[0]-200+1,5):
        for j in range(200,PhotoL.size[1]-200+1,5):
            position = i + (j * PhotoL.size[0])
            a = Correlate(PhotoL,PhotoR,position,centerOffset[0]-centerOffset[1],5)
            for k in range(-5,5+1):
                for l in range(-5,5+1):
                    p4 =  (i+k) + ((j+l) * PhotoL.size[0])
                    output[(i+k) + ((j+l) * PhotoL.size[0])] = a[3]
            # output[position + -1 - PhotoL.size[0]] =    a[3]
            # output[position + -1] =                     a[3]
            # output[position + -1 + PhotoL.size[0]] =    a[3]
            # output[position - PhotoL.size[0]] =         a[3]
            # output[position] =                          a[3]
            # output[position + PhotoL.size[0]] =         a[3]
            # output[position + 1 - PhotoL.size[0]] =     a[3]
            # output[position + 1] =                      a[3]
            # output[position + 1 + PhotoL.size[0]] =     a[3]
        print(i)
    l = time.time()
    print(l-k)
    #This shifts the colors so everything is "veiwable"
    largest = max(output)
    smallest = min(output)
    shift = 0 - smallest
    multiply = 240 / (largest-smallest)
    output = [int((i+shift)*multiply) for i in output]
    return(output)

def depthMap2(PhotoL,PhotoR,output):
    """
        We assume the photos are vertically matched
    """
    e = time.time()
    output = output
    for i in range(200,PhotoL.size[0]-200+1,27):
        for j in range(200,PhotoL.size[1]-200+1,27):
            position1 = i + (j * PhotoL.size[0])
            a = Correlate1(PhotoL,PhotoR,position1,width=27,step=6,offsetMax=250,offsetMin=50)
            for k in range(-9,10,9):
                for l in range(-9,10,9):
                    position2 = (i+k) + ((j+l) * PhotoL.size[0])
                    b = Correlate1(PhotoL,PhotoR,position2,width=9,step=3,offsetMax=a[3]+27,offsetMin=a[3]-27)
                    for g in range(-3,4,3):
                        for h in range(-3,4,3):
                            position3 = (i+k+g) + ((j+l+h) * PhotoL.size[0])
                            #print(b[3]+4,b[3]+4)
                            c = Correlate1(PhotoL,PhotoR,position3,width=3,step=1,offsetMax=b[3]+9,offsetMin=b[3]-9)
                            #print(position3,c)
                            #input()
                            output[position3 + -1 - PhotoL.size[0]] =    c[3]
                            output[position3 + -1] =                     c[3]
                            output[position3 + -1 + PhotoL.size[0]] =    c[3]
                            output[position3 - PhotoL.size[0]] =         c[3]
                            output[position3] =                          c[3]
                            output[position3 + PhotoL.size[0]] =         c[3]
                            output[position3 + 1 - PhotoL.size[0]] =     c[3]
                            output[position3 + 1] =                      c[3]
                            output[position3 + 1 + PhotoL.size[0]] =     c[3]
        print(i)
    #print(output[295000])
    #input()
    l = time.time()
    print(l-e)
    #This shifts the colors so everything is "veiwable"
    largest = max(output)
    smallest = min(output)
    shift = 0 - smallest
    multiply = 240 / (largest-smallest)
    output = [int((i+shift)*multiply) for i in output]
    return(output)

def depthMap3(PhotoL,PhotoR,output):
    """
        We assume the photos are vertically matched
    """
    e = time.time()
    output = output
    for i in range(200,PhotoL.size[0]-200+1,9):
        for j in range(200,PhotoL.size[1]-200+1,9):
            position1 = i + (j * PhotoL.size[0])
            a = Correlate1(PhotoL,PhotoR,position1,width=3,step=6,offsetMax=200,offsetMin=70)
            for k in range(-3,4,3):
                for l in range(-3,4,3):
                    position2 = (i+k) + ((j+l) * PhotoL.size[0])
                    b = Correlate1(PhotoL,PhotoR,position2,width=3,step=2,offsetMax=a[3]+54,offsetMin=a[3]-54)
                    output[position2 + -1 - PhotoL.size[0]] =    b[3]
                    output[position2 + -1] =                     b[3]
                    output[position2 + -1 + PhotoL.size[0]] =    b[3]
                    output[position2 - PhotoL.size[0]] =         b[3]
                    output[position2] =                          b[3]
                    output[position2 + PhotoL.size[0]] =         b[3]
                    output[position2 + 1 - PhotoL.size[0]] =     b[3]
                    output[position2 + 1] =                      b[3]
                    output[position2 + 1 + PhotoL.size[0]] =     b[3]
        print(i)
    #print(output[295000])
    #input()
    l = time.time()
    print(l-e)
    #This shifts the colors so everything is "veiwable"
    largest = max(output)
    smallest = min(output)
    shift = 0 - smallest
    multiply = 240 / (largest-smallest)
    output = [int((i+shift)*multiply) for i in output]
    return(output)
def depthMap4(PhotoL,PhotoR,output):
    """
        We assume the photos are vertically matched
    """
    startTime = time.time()
    output = output
    e = [-3,3,0,0,0]
    r = [0, 0,0,3,-3]
    for i in range(200,PhotoL.size[0]-200+1,9):
        for j in range(200,PhotoL.size[1]-200+1,9):
            a = []
            for k in [-3,3]:
                for l in [-3,3]:
                    position2 = (i+k) + ((j+l) * PhotoL.size[0])
                    b = Correlate1(PhotoL,PhotoR,position2,width=3,step=2,offsetMax=200,offsetMin=70)
                    a.append(b[3])
                    output[position2 + -1 - PhotoL.size[0]] =    b[3]
                    output[position2 + -1] =                     b[3]
                    output[position2 + -1 + PhotoL.size[0]] =    b[3]
                    output[position2 - PhotoL.size[0]] =         b[3]
                    output[position2] =                          b[3]
                    output[position2 + PhotoL.size[0]] =         b[3]
                    output[position2 + 1 - PhotoL.size[0]] =     b[3]
                    output[position2 + 1] =                      b[3]
                    output[position2 + 1 + PhotoL.size[0]] =     b[3]
            offsetMin = min(a)
            offsetMax = max(a)
            for m in range(5):
                position3 = (i+e[m]) + ((j+r[m]) * PhotoL.size[0])
                b = Correlate1(PhotoL,PhotoR,position3,width=3,step=1,offsetMax=offsetMax+1,offsetMin=offsetMin-1)
                output[position3 + -1 - PhotoL.size[0]] =    b[3]
                output[position3 + -1] =                     b[3]
                output[position3 + -1 + PhotoL.size[0]] =    b[3]
                output[position3 - PhotoL.size[0]] =         b[3]
                output[position3] =                          b[3]
                output[position3 + PhotoL.size[0]] =         b[3]
                output[position3 + 1 - PhotoL.size[0]] =     b[3]
                output[position3 + 1] =                      b[3]
                output[position3 + 1 + PhotoL.size[0]] =     b[3]
        print(i)
    l = time.time()
    print(l-startTime)
    #This shifts the colors so everything is "veiwable"
    largest = max(output)
    smallest = min(output)
    shift = 0 - smallest
    multiply = 240 / (largest-smallest)
    output = [int((i+shift)*multiply) for i in output]
    return(output)


if __name__ == "__main__":
    ag =time.time();print("Starting")
    PhotoL = photo("left.png");PhotoR = photo("right.png")
    PhotoL.flattenChannels();PhotoR.flattenChannels()  
    emptyList = [0 for i in range(0,PhotoL.size[0]* PhotoL.size[1])]
    outputl = Image.new(PhotoL.mode,PhotoL.size,color=0)
    outputr = Image.new(PhotoL.mode,PhotoL.size,color=0)
    depthphoto = Image.new(PhotoL.mode,PhotoL.size,color=0)
    b=time.time();print("Images Imported: ", b-ag)
    
    
    # depthData = depthMap(PhotoL,PhotoR,emptyList)
    # #depthData = depthMap(PhotoL,PhotoR,emptyList)
    # outputDepth = combineChannelsList(depthData,depthData,depthData)
    # depthphoto.putdata(outputDepth)
    # depthphoto.save("depth.png")
    
    
    a = checkCenterOffset(PhotoL,PhotoR,width=3)
    import random
    b = Correlate1(PhotoL,PhotoR,295000,width=3,step=1,offsetMax=200,offsetMin=72)
    print(a)
    print(b)
    chosenPixell = b[0]
    chosenPixelr = b[1]
    outputDatal = combineChannelsList(PhotoL.Greylist,emptyList,emptyList)
    outputDatar = combineChannelsList(PhotoL.Greylist,emptyList,emptyList)
    outputDatal = Marker(outputDatal,chosenPixell,PhotoL.size[0])
    outputDatar = Marker(outputDatar,chosenPixelr,PhotoR.size[0])
    outputl.putdata(outputDatal)
    outputl.save("outputl.png")
    outputr.putdata(outputDatar)
    outputr.save("outputr.png")
    
    d = time.time();print("Photos Exported: ")
    print("Total Time: ",d-ag)