# Creates bytecode representing contrast at different spatial frequencies, at a particular angle and 
# Gaussian blur, bytecode is pushed to regis cache list
# Sanjayan Kulendran - skulend2@uwo.ca

from flask import Flask, request, render_template, send_file

import matplotlib
matplotlib.use('Agg') #Prevent viewing within window

from matplotlib import pyplot as plt

import skimage
from skimage.viewer import ImageViewer #Needs QT
import numpy as np
import scipy

#Import opencv for faster Gaussians
import cv2
import imutils

#Import redis to store generated contrast data
import redis

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('index.html', transferName = 'Example Run', angDef = "45", sigmaDef = "100", nameDef = "camera1")

@app.route('/', methods=['POST'])
def my_form_post():

    #Read in the given values
    angle = float( request.form['angle'] )
    sigma = int ( request.form['sigma'] )
    cname = request.form['cname']
    
    #Generates image set, and determines contrast at different spatial freq, given angle and gauss sigma
    set_mtf_image(angle, sigma, cname)

    #Name that will be passed to the template
    figTitle = "Sample of test set for " + cname

    return render_template('index.html', transferName = figTitle, angDef = str(angle), sigmaDef = str(sigma), nameDef = str(cname))

#Internal function used to generate
def set_mtf_image(edgeAngle, sigma, name):

    #Initialize the redis server connection
    redisServer = redis.Redis(host='redis-service', port=6379, db=0)

    #Parameters for imager/setup

    #Original Image Source (before rotation)
    sourceW = 2000 #Image Width
    sourceH = 2000 #Image Height

    #Rotation frame (the size of the viewing frame such that the image is visible), always square
    frameWidth = np.floor((np.minimum([sourceW],[sourceH])/np.sqrt(2)))

    #range of edge widths to try
    edgeRange = np.arange(1000,50, -50) 

    #Which edge sizes should be visualized
    visualize = [100]

    #Empty string for storing the recorded contrasts in the database
    contrastString = ""

    #Index of contrasts array
    edgeIndex = 0

    #For every image width
    #For every spacing requirement
    for edgeSize in edgeRange:

        #Intitate blank array with original image dims
        sourceImage = np.zeros((sourceH, sourceW), dtype=np.uint8)

        #For every line required
        for lineNumber in range(0, (sourceW + 2*edgeSize), 2*edgeSize):

            #Convert the corresponding parts of the array into white
            sourceImage[:,lineNumber:(min((lineNumber+edgeSize),(sourceW-1)))] = 255

        #Apply the rotation step
        rotated = imutils.rotate(sourceImage, edgeAngle)
        #Crop to rotation frame
        rotatedCrop = rotated[int(sourceH/2-frameWidth/2):int(sourceH/2+frameWidth/2), int(sourceW/2-frameWidth/2):int(sourceW/2+frameWidth/2)]

        #Apply a Gaussian blur, using cv2 now for better performance
        #blurred = skimage.filters.gaussian(sourceImage, sigma=(sigma, sigma),  multichannel=False, preserve_range=True)
        blurred = cv2.GaussianBlur(rotatedCrop, [0,0], sigma, sigma,  cv2.BORDER_DEFAULT)

        #Sample from interior to avoid edge effects
        blurredSample = blurred[int(frameWidth/4):int(3*frameWidth/4),int(frameWidth/4):int(3*frameWidth/4)]

        #Append the difference between the minimum and maximum values in the image to the contrast string 
        contrastString +=  '{:0>2x}'.format((blurredSample.max() - blurredSample.min()))

        #Print the appended value
        #print(format((blurredSample.max() - blurredSample.min()), "x"))

        #If this is a step to visualize
        if edgeSize in visualize:

            #Set up subplots
            fig, (ax1, ax2) = plt.subplots(1,2)
            fig.suptitle(str(edgeSize) + 'px width, with '+str(sigma) + ' sigma Gaussian, at bar angle ' + str(edgeAngle))

            #Display the image
            ax1.imshow(rotatedCrop[int(frameWidth/4):int(3*frameWidth/4),int(frameWidth/4):int(3*frameWidth/4)].astype(np.uint8), cmap='gray', vmin=0, vmax=255)
            ax2.imshow(blurredSample.astype(np.uint8), cmap='gray', vmin=0, vmax=255)
            fig.savefig('./static/image.jpg')

            #Display the blur
            #plt.imshow(blurredSample.astype(np.uint8), cmap='gray', vmin=0, vmax=255)
            #plt.title(str(edgeSize) + 'px Width, with '+str(sigma) +' sigma Gaussian')
            #plt.show()

        #Increment Contrasts Array
        edgeIndex += 1
        
    #Append the value from this test onto the database
    redisServer.rpush(name,contrastString)


if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')