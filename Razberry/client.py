#-*-coding:utf-8
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

reload(sys)
sys.setdefaultencoding('utf-8')

from os import walk

base_url = 'http://112.151.162.170:7000/init'
raz_url = 'http://112.151.162.170:7000/raz_client'
pwd = '/home/pi/Hmmteresting/Razberry/test_image.jpg'

class RaspberryModule():

    def detect(self, img, cascade):
        rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30,30),
                            flags=cv2.CASCADE_SCALE_IMAGE)
        if len(rects) == 0:
            return []

        rects[:,2:] += rects[:,:2]
        return rects

    def draw_rects(self, img, rects, color):
        for x1, y1, x2, y2 in rects:
            cv2.imwrite("test_image.jpg", img)
            rect_image = cv2.rectangle(img, (x1-40, y1-40), (x2+40, y2+40), color, 2)
            print(x1, y1, x2, y2)   #rectangle coordinate
            cv2.imwrite("rect_image.jpg", rect_image)   #save a rectangle-drawn picture
            crop_image = Image.open('rect_image.jpg')
            crop_image = crop_image.crop((x1-40, y1-40, x2+40, y2+40))  #crop the image inside the rectangle
            crop_image.save('crop_image.jpg')   #save crop image
            return 1

    def start_record_vid(self):
        #start video recording
        os.system('./video_start.sh')

    def stop_record_vid(self):
        #stop video recording
        os.system('./video_stop.sh')
        vid_name = subprocess.check_output('./getname_test.sh', shell = True)
        return vid_name

    def record_aud(self):
        #audio recording and return file name
        aud_name = subprocess.check_output('./audio_message.sh', shell = True)
        return aud_name

if __name__ == '__main__':
    
    raz_module = RaspberryModule()

    #Camera setting
    camera = PiCamera()
    camera.resolution = (612, 816)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(612, 816))
    cascade = cv2.CascadeClassifier("/home/pi/opencv-3.3.0/data/haarcascades/haarcascade_frontalface_alt.xml")
    
    time.sleep(0.1)

    '''
    os.system('python init.py &')
    time.sleep(3)
    os.system('pkill -9 -ef schedule.py')
    '''

    while True:
        os.system('python init.py &')
        time.sleep(3)
        os.system('pkill -9 -ef schedule.py')

	#capture frames from the camera
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            #grab the raw Numpy array representing the image, then initialize the timestamp
            #and occupied/unoccupied text
            img = frame.array

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)

            rects = raz_module.detect(gray, cascade)
            vis = img.copy()
        
            if raz_module.draw_rects(vis, rects, (0, 255, 0)) == 1:
                
                files = {'media' : open(pwd, 'rb') }
                image_url = base_url
                res = requests.post(image_url, files = files)
	        
                if res.text == 'cannot find face':
                    print res.text
                elif res.text == 'who are you?':
                    print res.text
                elif res.text == 'Too Many Faces':
                    print res.text
                else :
                    print("detected!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print res.text
                    
                    #make json file named test.json
                    #json_data = ast.literal_eval(res.text)
                    json_data = json.loads(res.text)
                    with open('test.json', 'w') as make_file:
                        json.dump(json_data, make_file, ensure_ascii=False)

                    break
                    
            #show the frame
            #cv2.imshow("Frame", vis)
            rawCapture.truncate(0)

        rawCapture.truncate(0)
        camera.close()
        
        #change the color of monitor when server responsed
        os.system('python schedule.py &')
        time.sleep(3)
        os.system('pkill -9 -ef init.py')
        time.sleep(3)

        while True:
        
            try: 
                print ("Sending.............................") 
                res = requests.post(raz_url)
            #get request and wait for returing value
            except requests.exceptions.ConnectionError:
                print("zzzzzzzzzzzzzzzzzz")
                time.sleep(5)
                print("..................")
                continue
            
            
            input_data = json.loads(res.text)
            client_Param = input_data["client_Param"]
            print client_Param

            if (client_Param == "1"):
                #record and send video name
                raz_module.start_record_vid()
                now = time.time()
                time.sleep(5)
                video_name = raz_module.stop_record_vid()
                
                print ("tttttttttttttttttttttttttttssssssssssssssssssssss")
                video_save_url = base_url + '/sendMessage'
                data = {"title" : "abc.ts"}
                #headers = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
                res = requests.post(video_save_url, data = data)
            # elif (client_Param == 2):
            #    #record and send audio name
            #    #turn on the video
            #    
            #    audio_name = raz_module.record_aud()
            #    audio_save_url = base_url + '/sendAudioMessage'
            #    res = requests.post(audio_save_url, data = audio_name)
                
            elif (client_Param == "2"):
                continue
                #turn on the video
            elif (client_Param == "3"):
                #break inner loop and go to outer loop
                break
            else :
                #innser loop
                print("pppppppppppppppppppppeaceeeeeeeeeeeee")
                time.sleep(5)
                continue
