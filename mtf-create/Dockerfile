#Dockerfile, Image, Container
FROM python:3.7

#Needs to run with terminal and inter
ADD mtf-create-flask.py .

#Copy over files
COPY ./static ./static
COPY ./templates ./templates

#STACK
RUN apt-get update ##[edited]
RUN apt-get install ffmpeg libsm6 libxext6  -y

#STACK

RUN pip install matplotlib
RUN pip install scikit-image
RUN pip install numpy
RUN pip install scipy
RUN pip install opencv-python
RUN pip install imutils

RUN pip install flask


RUN pip install redis

CMD [ "python", "./mtf-create-flask.py" ]
