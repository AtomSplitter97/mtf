# MTF viewing app, reads bytecode from regis cache list and plot of effective resolution
# Sanjayan Kulendran - skulend2@uwo.ca

from flask import Flask, request, render_template, send_file
import matplotlib
matplotlib.use('Agg') #Prevent viewing within window
from matplotlib import pyplot as plt
import numpy as np
import redis #Import redis to store generated contrast data

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('index.html', transferName = 'Example Run',  nameDef = "camera1")

@app.route('/', methods=['POST'])
def my_form_post():

    #Read in the given values
    cname = request.form['cname']
    
    #Reads available contrasts and generates MTF
    read_mtf_image(cname)

    #Name that will be passed to the template
    figTitle = "Current MTF for " + cname

    return render_template('index.html', transferName = figTitle, nameDef = str(cname))

#Internal function used to read contrasts for the associated camera
def read_mtf_image(camera):

    #Initialize the redis server connection
    redisServer = redis.Redis(host='redis-service', port=6379, db=0)

    #USE LLEN TO GET RANGE OF REDIS LIST
    listSize = redisServer.llen(camera)

    #CREATE AN ARRAY OF CONTRASTS vs SPATIAL FREQUENCY, hardcoded size for now (1000 px to 50px in increments of -50)
    edgeRange = np.reciprocal(np.arange(1000,50,-50).astype(float))
    contrasts = np.zeros(len(edgeRange))

    #FOR EVERY BYTE STRING IN REDIS LIST ENTRY
    for i in range(0, listSize):

        #Print the value, pop and push for O(1) complexity
        getval = redisServer.rpoplpush(camera, camera)
        print("Contrast string: " + str(getval) + " | " +str(len(getval)))

        #FOR EVERY 2 CHARACTERS
        for j in range(0,len(getval), 2):

            #Sum the hex value to the total
            contrasts[int(j/2)] += int(getval[j:j+2],16)

            #print("{"+str(i)+", "+str(j/2)+"} - " + str(getval[j:j+2])+" =>"+ str(contrasts[int(j/2)]))

    #output the contrast array
    #print("Contrasts Array: \n " + str(contrasts))
    #NORMALIZE CONTRAST ARRAY
    contrasts = contrasts/np.amax(contrasts)

    #output the contrast array
    #print("Normalized Contrasts Array: \n " + str(contrasts))

    #VISUALIZE MTF FUNCTION
    fig, ax = plt.subplots()
    ax = plt.plot(edgeRange,contrasts,linestyle='solid',color='blue')
    ax = plt.title("Mean Angle-Averaged MTF of " + str(camera))
    ax = plt.xscale("log")
    ax = plt.xlabel("Spatial Frequency [px^-1]")
    ax = plt.ylabel("Normalized Contrast")
    fig.savefig('./static/image.jpg')
    


if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')