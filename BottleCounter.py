from re import I
from PIL import Image, ImageDraw
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

# https://en.wikipedia.org/wiki/Circle_Hough_Transform
# https://sbme-tutorials.github.io/2018/cv/notes/5_week5.html#hough-circle

def applyFunctionToPixels(edge, imW, imH, function, extra, image):
        result = np.empty((imH, imW), dtype=int)
        for i in range(edge, imW-edge):
            for j in range(edge, imH-edge):
                result[j][i] = function(i, j, extra, image)
        return result
    
def makeBWImage(i, j, th, image):
    result = 0
    if image[j][i] > th:
        result = 255
    return result

def dilateImage(i, j, matrix, image):
    result = 0
    edge = matrix.shape[0]//2
    for x in range(matrix.shape[0]):
        for y in range(matrix.shape[1]):
            if (matrix[y][x] and image[j-edge+y][i-edge+x]):
                return 255
    return result

def erodeImage(i, j, matrix, image):
    result = 255
    edge = matrix.shape[0]//2
    for x in range(matrix.shape[0]):
        for y in range(matrix.shape[1]):
            if (matrix[y][x] and not image[j-edge+y][i-edge+x]):
                return 0
    return result

def edge(i, j, erImg, dilImg):
    if dilImg[j][i] == 0:
        return 0
    else:
        return dilImg[j][i]-erImg[j][i]


# this is AGRESSIVELY SLOW
def findCircles(imW, imH, lrad, urad, image):
    circles = []
    accumulator = np.zeros((imH,imW,urad-lrad), dtype=int)

    for i in range(urad, imW-urad):
        for j in range(urad, imH-urad):
            if image[j][i]:
                for radius in range(urad-lrad):
                    for angle in range(360):
                        b = int(j - (radius+lrad)*np.sin(angle*np.pi/180))
                        a = int(i - (radius+lrad)*np.cos(angle*np.pi/180))
                        
                        accumulator[b][a][radius] += 1
    
    minDist = 2*lrad

    for y in range(accumulator.shape[0]):
        for x in range(accumulator.shape[1]):
            for rad in range(urad-lrad-1, 0, -1):
                if accumulator[y][x][rad] >= 120:
                    circles.append((x,y,rad))
                    for i in range(minDist):
                        for j in range(minDist):
                            for r in range(urad-lrad):
                                accumulator[y+i-int(minDist/2)][x+j-int(minDist/2)][r] = 0
                    break

    return circles
    
def bottleCounter(imageURL):
    image = Image.open(imageURL)
    imageWidth = image.size[0]
    imageHeight = image.size[1]

    # Range of bottle rims
    bottleRimURad = 24
    bottleRimLRad = 16
    # Range of larger bottles and bottle bottoms
    bottleBotURad = 42
    bottleBotLRad = 38
    count = 0

    dilMatrix = np.ones((3,3), dtype=int)
    dilMatrix[0][0]=0
    dilMatrix[2][0]=0
    dilMatrix[0][2]=0
    dilMatrix[2][2]=0


    bwimg = np.array(image)
    bwimg = applyFunctionToPixels(0, imageWidth, imageHeight, makeBWImage, 100, bwimg)
    dilatedImg = applyFunctionToPixels(1, imageWidth, imageHeight, dilateImage, dilMatrix, bwimg)
    edges = applyFunctionToPixels(0, imageWidth, imageHeight, edge, bwimg, dilatedImg)
    circles = findCircles(imageWidth, imageHeight, bottleRimLRad, bottleRimURad, edges)
    lCircles = findCircles(imageWidth, imageHeight, bottleBotLRad, bottleBotURad, edges)
    count += len(circles)
    count += len(lCircles)
        
    rgbimg = image.convert("RGB")
    draw = ImageDraw.Draw(rgbimg)                    
    for i in range(len(circles)):
        draw.ellipse((circles[i][0]-circles[i][2]-bottleRimLRad, circles[i][1]-circles[i][2]-bottleRimLRad, circles[i][0]+circles[i][2]+bottleRimLRad, circles[i][1]+circles[i][2]+bottleRimLRad), outline=(255,0,0))
    for i in range(len(lCircles)):
        draw.ellipse((lCircles[i][0]-lCircles[i][2]-bottleBotLRad, lCircles[i][1]-lCircles[i][2]-bottleBotLRad, lCircles[i][0]+lCircles[i][2]+bottleBotLRad, lCircles[i][1]+lCircles[i][2]+bottleBotLRad), outline=(255,0,0))
    #rgbimg.save(edgeImageURL)
    rgbimg.show()
    print(count)

#bottleCounter([insert own path])