"""
        Code Written By Aaron Spaulding
"""
from PIL import Image
import time

class photo():
        def __init__(self,filename):
                """
                        This class is just a simple wrapper for some PILLOW
                        functions and provides a more simple way to access
                        common variables.
                """
                self.name = str(filename)
                self.image = Image.open(self.name)
                self.size = self.image.size
                self.length = self.size[0] * self.size[1]
                self.data = list(self.image.getdata())
                self.mode = self.image.mode
        
        def flattenChannelsIterator(self,singleChannel="all"):
                """
                        This function is very slow and should only be used if 
                        the iterator types are needed.
                        (e.g. The image is very large)

                        This function converts a RGB photo to lists containing
                        pixel data for each color channel.
                """
                if self.mode != "RGB":
                        raise Exception("This is only tested on RGB images")
                if(singleChannel == "R" or singleChannel == "all"):
                        self.R = (x[0] for x in self.data)
                        self.Rlist = [x[0] for x in self.data]
                if(singleChannel == "G" or singleChannel == "all"):
                        self.G = (x[1] for x in self.data)
                        self.Glist = [x[1] for x in self.data]
                if(singleChannel == "B" or singleChannel == "all"):
                        self.B = (x[2] for x in self.data)
                        self.Blist = [x[2] for x in self.data]
                return(1)
        def flattenChannels(self):
                """
                        This function converts a RGB photo to lists containing
                        pixel data for each color channel.
                """
                if self.mode != "RGB":
                        raise Exception("This is only tested on RGB images")
                self.Rlist = list(self.image.getdata(0))
                self.Glist = list(self.image.getdata(1))
                self.Blist = list(self.image.getdata(2))
                self.Greylist = [int((i+j+k)/3) for i in self.Rlist for j in self.Glist for k in self.Blist]

        def flattenData(self):
                """
                        This function converts a RGB photo to one list
                        containing all pixel data for the image concatenated
                        together.
                """
                if self.mode != "RGB":
                        raise Exception("This is only tested on RGB images")
                self.flatData = []
                for i in self.data:
                        self.flatData.extend(i)
                return(self.flatData)

def combineChannels(R,G,B,length):
        """
                This function creates a list of RGB tuples for the pixels.
                Each tuple represents one pixel in the image.
        """
        return(map(lambda R,G,B:(R,G,B),R,G,B))

def combineChannelsList(R,G,B):
        return(list(zip(R,G,B)))

def unFlatten(flattenedList):
        """
                FUNCTION DOES NOT WORK. IF YOU WANT TO FIX THIS PLEASE FEEL
                FREE TO. DO NOT USE UNlESS FIXED
                This function takes a flattened list of RGB values and outputs
                a tuple containing the RGB channels.
        """
        raise Exception("FUNCTION DOES NOT WORK, DO NOT USE UNLESS EDITED")
       # if len(flattenedList) % 3 != 0:
       #         raise Exception("Check input list length")
        channels = [[],[],[]]
        for i in range(len(flattenedList)):
                channels[i % 3].append(flattenedList[i])
        channels2 = (channels[0],channels[1],channels[2])
        return(channels2)

def getBlock(image,pixelNumber,width):
    """
    This function gets the list for the pixels contained in the image
    centered at the pixel chosen with width specified. Width should be 
    even.
    """
    a = int(width/2)
    output=[]
    for j in range(-a,a+1):
        for i in range(-a,a+1):
            output.append(image[pixelNumber+i+(2964*j)])
    return(output)


if __name__ == "__main__":
        print("1")
        inputPhoto = photo("left.png");print("2")
        inputPhoto.flattenChannels();print("3")
        data1 = combineChannelsList(inputPhoto.Rlist,inputPhoto.Glist,inputPhoto.Blist)
        print("4")
        output1 = Image.new(inputPhoto.mode,inputPhoto.size,color=0);print("5")
        """
        a = [];h=0;n=100
        for i in data1:
                if h < n:
                        a.append(i)
                        h+=1
                elif h == n:
                        n+=100
                        a.append(i)
                        sys.stdout.write('\r')
                        sys.stdout.write(str(h/inputPhoto.length))
                        sys.stdout.flush()
                        h+=1
        """
        output1.putdata(data1);print("6")
        output1.save("test1.png");print("7")
