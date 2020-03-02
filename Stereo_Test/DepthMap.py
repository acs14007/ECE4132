from imaging import *
import time
import multiprocessing

#We will just deal with the red channel for simplicity.
#We need to define a new function to define cross correlation
#Since this is just a test we will just use it on the linear data
#This can be optimized in two ways; by tracing the image in a Hilbert Curve
#Or by doing it in 2D. The Hilbert curve approach should be more simple to write
#With the same results


def SSD(image1,image2,pixelNumber1,pixelNumber2,width=3):
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

def Correlate(photo1,photo2,location,centerOffset=0,width=10):
    """
        This function finds a matching position of photo2 given a point in photo1.
        The centerOffset must be defined.
    """
    bestMatch = [10000000,0]
    searchWindowWidth = 150
    for i in range(location-searchWindowWidth,location+searchWindowWidth):
        for j in range(-100,100):
            pixel = i + (j * photo1.size[0])
            h = SSD(photo1,photo2,location,pixel,width)
            if h < bestMatch[0]:bestMatch = [h,pixel]
    return((location,bestMatch[1],bestMatch[0],abs(location-bestMatch[1])))

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

if __name__ == "__main__":
    startTime = time.time()

    PhotoL = photo("flatLeft.jpg")
    PhotoR = photo("flatRight.jpg")
    PhotoL.flattenChannels()
    PhotoR.flattenChannels()
    emptyList = [0 for i in range(0,PhotoL.size[0]* PhotoL.size[1])]
    outputl = Image.new(PhotoL.mode,PhotoL.size,color=0)
    outputr = Image.new(PhotoL.mode,PhotoL.size,color=0)
    outputDatal = combineChannelsList(PhotoL.Rlist,emptyList,emptyList)
    outputDatar = combineChannelsList(PhotoR.Rlist,emptyList,emptyList)
    print("Finished initial Processing")

    chosenPixell1 = 1490840
    b = Correlate(PhotoL,PhotoR,chosenPixell1)
    chosenPixelr1 = b[1]
    chosenPixell2 = 370000
    b = Correlate(PhotoL,PhotoR,chosenPixell2)
    chosenPixelr2 = b[1]


    outputDatal = Marker(outputDatal,chosenPixell1,PhotoL.size[0])
    outputDatar = Marker(outputDatar,chosenPixelr1,PhotoR.size[0])

    outputDatal = Marker(outputDatal,chosenPixell2,PhotoL.size[0])
    outputDatar = Marker(outputDatar,chosenPixelr2,PhotoR.size[0])

    outputl.putdata(outputDatal)
    outputl.save("outputl.png")
    outputr.putdata(outputDatar)
    outputr.save("outputr.png")




    

    endTime = time.time()
    print(endTime-startTime)