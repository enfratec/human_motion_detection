'''
Task : To track the object movement in an video or camera input 

Author : Vigneshwer Dhinakaran

E-mail : dvigneshwer@gmail.com

Version : 1.0

Date : 14th May 2016
'''

#loading modules
import cv2
import numpy as np 
import os
import configparser
import logging as log

#Function to read from the usb id
def findVideoID(USBID):	
	try:
		devices = os.popen("v4l2-ctl --list-devices").read()
		devices = devices.split('\n')
		loc = IDLoc = -1
		for loc,line in enumerate(devices):
			IDLoc = line.find(USBID)
			if IDLoc != -1:
				break
		if IDLoc==-1:
			return USBID #No Id found - improper code
		else:
			#If the USB ID was found, look at the next line for it's videoID
			return devices[loc+1].split("video")[-1]

	except Exception as e:
		raise e

#creating logging
log.basicConfig(filename='HMT_log.log',level=log.DEBUG)

#loading configfile
configReader = configparser.ConfigParser()
configReader.read("./config_HMT.INI")
min_area = int(configReader['thresholds']['min_area'])
max_area = int(configReader['thresholds']['max_area'])
frame_count = int(configReader['thresholds']['frame_count'])
frame_selector = int(configReader['thresholds']['fps'])
min_thres_val = int(configReader['thresholds']['min_thres_val'])
max_thres_val = int(configReader['thresholds']['max_thres_val'])
detection_save_loc = configReader['storage_location']['detection_location']

#Asking user for input 
print "Enter 1 for camera input or 2 for video input \n"
user_choice = raw_input()

if user_choice == "1":
	print "Enter the camera usb id \n"
	usb_id = raw_input()
	log.info("Reading from camera feed")
	#Finding video object 
	video_object = findVideoID(usb_id)
	#creating the video object
	vid = cv2.VideoCapture(video_object)

elif user_choice == "2":
	print "Enter the video location \n"
	video_location = raw_input()
	log.info("Reading from a video")
	#creating an video object
	vid = cv2.VideoCapture(video_location) 

#Reading input till the video object is True
while (vid.isOpened()):
	#reading frame by frame
	ret,frame = vid.read()
	frame_count+=1
	#No more frames
	if not ret:
		break

	log.info("Reading and processing")
	#resizing the frame
	frame_resize = cv2.resize(frame,(640,480))
	#Converting to gray scale
	frame_gray = cv2.cvtColor(frame_resize,cv2.COLOR_BGR2GRAY)
	#Blurring image
	# blur_frame = cv2.GaussianBlur(frame_gray,(21,21),0)

	#setting the first frame
	if (frame_count==1) or (frame_count%frame_selector == 0):
		first_frame = frame_gray
	
	frameDelta = cv2.subtract(first_frame, frame_gray)
	ret, thresh = cv2.threshold(frameDelta, min_thres_val, max_thres_val, cv2.THRESH_BINARY)
 
	# dilate the thresholded image to fill in holes, then find contours
	# thresh = cv2.dilate(thresh, None, iterations=2)
	contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
 
	# loop over the contours
	for c in contours:

		#Ignore really small and big contours, these parameters need to be tuned
		if cv2.contourArea(c) < min_area or cv2.contourArea(c) > max_area:
			continue
 		
 		# print "Contour area is " + str(cv2.contourArea(c) )
 		log.info("Object detected")
		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame_resize, (x, y), (x + w, y + h), (0, 255, 0), 2)
		cv2.imwrite("./detection_data/detection_"+str(frame_count)+".jpg",frame_resize[y:y+h,x:x+w])
		text = "Object Detected"

		cv2.putText(frame_resize, "Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
 
	cv2.imshow("Security Feed", frame_resize)
	# cv2.imshow("Thresh", thresh)
	# cv2.imshow("Frame Delta", frameDelta)
	key = cv2.waitKey(1) & 0xFF
	# if the `q` key is pressed break the loop
	if key == ord("q"):
		break

log.info("Frame input over")
# cleanup the camera object and close any open windows
vid.release()
cv2.destroyAllWindows()





