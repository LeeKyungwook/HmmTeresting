#import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import time
import cv2
import json
import requests
import os
import time
import subprocess
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from os import walk

base_url = 'http://112.151.162.170:7000/'
pwd = '/home/pi/crop_image.jpg'

class RaspberryModule():
    '''
    def iniaialize_picam(self):
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 32
        rawCapture = PiRGBArray(camera, size=(640, 480))

        cascade = cv2.CascadeClassifier("/home/pi/opencv-3.3.0/data/haarcascades/haarcascade_frontalface_alt.xml")
       
       #allow the camera to warmup
        time.sleep(0.1)

        
        #capture frames from the camera
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            #grab the raw Numpy array representing the image, then initialize the timestamp
            #and occupied/unoccupied text
            img = frame.array

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)

            return gray
        
    '''    
    def detect(self, img, cascade):
        rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30,30),
                            flags=cv2.CASCADE_SCALE_IMAGE)
        if len(rects) == 0:
            return []
            #return 1
        rects[:,2:] += rects[:,:2]
        return rects

    def draw_rects(self, img, rects, color):
        for x1, y1, x2, y2 in rects:
            rect_image = cv2.rectangle(img, (x1-40, y1-40), (x2+40, y2+40), color, 2)
            print(x1, y1, x2, y2)   #rectangle coordinate
            cv2.imwrite("rect_image.jpg", rect_image)   #save a rectangle-drawn picture
            crop_image = Image.open('rect_image.jpg')
            crop_image = crop_image.crop((x1-40, y1-40, x2+40, y2+40))  #crop the image inside the rectangle
            crop_image.save('crop_image.jpg')   #save crop image
            return 1

    def record_vid():
        # video recording and return file name
        os.system('./video_message.sh')
        vid_name = subprocess.check_output('./getname_test.sh', shell = True)
        return vid_name

    def record_aud():
        #audio recording and return file name
        aud_name = subprocess.check_output('./audio_message.sh', shell = True)
        return aud_name

class RaspberryUI(QWidget):
 
    def __init__(self):
        super(App, self).__init__()
        self.title = 'Hmmteresting....'
        self.left = 10
        self.top = 10
        self.width = 1920   # Change Monitor's width
        self.height = 1080  # Change Monitor's height
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # Set window background color
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)
 
        self.show()
    
    def arrange_UI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

        self.show()

    def close(self): 
        self.close()

if __name__ == '__main__':

    raz_module = RaspberryModule()
    raz_ui = RaspberryUI()

    #Camera setting
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))
    cascade = cv2.CascadeClassifier("/home/pi/opencv-3.3.0/data/haarcascades/haarcascade_frontalface_alt.xml")
    
    time.sleep(0.1)

    while True:

        raz_ui.initUI()
        
	#capture frames from the camera
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            #grab the raw Numpy array representing the image, then initialize the timestamp
            #and occupied/unoccupied text
            img = frame.array

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)

        #if (raz_module.detect(img, cascade) != 1):
            rects = raz_module.detect(gray, cascade)
            vis = img.copy()
        
            if raz_module.draw_rects(vis, rects, (0, 255, 0)) == 1:
                break
            
            #show the frame
            cv2.imshow("Frame", vis)
            rawCapture.truncate(0)

        files = {'media' : open(pwd, 'rb') }
        image_url = base_url + 'file'
        res = requests.post(image_url, files = files)

        #change the color of monitor when server responsed
        if res is not None:
            raz_ui.arrange_UI()

        while True:

            video_url = base_url + 'video'
            res = requests.get(url = video_url)         
            #get request and wait for returing value

            if (res.text == 1):
                #send video name
                video_name = raz_module.record_vid()    
                video_save_url = video_url + '/vsave'
                res = requests.post(video_save_url, data = video_name)
            elif (res.text == 2):
                #send audio name
                audio_name = raz_module.record_aud()
                audio_save_url = audio_url + '/asave'
                res = requests.post(audio_save_url, data = audio_name)
            elif(res.text == 3):
                #turn on the video
                break
            elif(res.text == 4):
                #break inner loop and go to outer loop
                break
            else:
                #innser loop
                time.sleep(2)
                continue
        '''
        else:
            time.sleep(2)
            continue
        '''
