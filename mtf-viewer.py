#Import redis
import redis

#For the visualization of the transfer function
from matplotlib import pyplot as plt
import numpy as np

#Configure connection to the redis server
redisServer = redis.Redis(host='localhost', port=6379, db=0)

#While the program continues to run
while True:

    #Ask for camera name
    camera = input("Enter the name of the camera: ")

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

            print("{"+str(i)+", "+str(j/2)+"} - " + str(getval[j:j+2])+" =>"+ str(contrasts[int(j/2)]))

    #output the contrast array
    print("Contrasts Array: \n " + str(contrasts))
    #NORMALIZE CONTRAST ARRAY
    contrasts = contrasts/np.amax(contrasts)

    #output the contrast array
    print("Normalized Contrasts Array: \n " + str(contrasts))

    #VISUALIZE MTF FUNCTION
    #Plot
    plt.plot(edgeRange,contrasts,linestyle='solid',color='blue')
    plt.title("Mean Angle-Averaged MTF of " + str(camera))
    plt.xscale("log")
    plt.xlabel("Spatial Frequency [px^-1]")
    plt.ylabel("Normalized Contrast")
    plt.show()

    #Ask if the user would like to continue
    response = str(input("Read another set of simulations? (y/[n]): ")).upper()

    #If the response is not y
    if response != 'Y' :

        #Exit the loop
        print("Terminating the program! ")
        break

    #Otherwise
    else:

        #Rerun
        print("Re-running the program")
