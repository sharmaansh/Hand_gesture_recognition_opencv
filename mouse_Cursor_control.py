import numpy as np
import win32api, win32con
import cv2
import operator
import os

mouseAcc = 1

def bgrToHSV( bgr ):
	return cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)	

def getBoundsForBGR( bgr, tolerance ):
	hsv = bgrToHSV(bgr)[0][0]	
	return (np.array([max((0, hsv[0] - tolerance)), 100, 100]), np.array([min(255, hsv[0] + tolerance), 255, 255]))	

def clamp(min_v, max_v, val):
	return max(min(max_v, val), min_v)

print ("To exit, press ESC\n\n")
print ("Specify the color of the object you want to track(B,G,R):")
colourToTrack = [clamp(0, 255, int(input("Blue (0-255): "))), clamp(0, 255, int(input("Green (0-255): "))), clamp(0, 255, int(input("Red (0-255): ")))]
treshold = int(clamp(5, 50, int(input("Give me sensitivity (5-50): "))))

colourBounds = getBoundsForBGR(colourToTrack, treshold)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))

camera = cv2.VideoCapture(0)
prevBoxPos = None

while(1):

	cursorPos = win32api.GetCursorPos()
	trackObjDelta = (0, 0)

	_, frame = camera.read()
	frame = cv2.flip(frame, 1)
	
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	mask = cv2.inRange(hsv, colourBounds[0], colourBounds[1])	
	mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)		
	
	_,contours,hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	if len(contours) > 0:
		rects = map(lambda c : cv2.minAreaRect(c), contours)
		maxRect = max(rects, key=lambda r : r[1][0] * r[1][1])			
		box = cv2.boxPoints(maxRect)
		box = np.int0(box)
		cv2.drawContours(frame,[box],0,(0,0,255),2)

		boxPos = (int(maxRect[0][0]), int(maxRect[0][1]))		
		cv2.circle(frame, boxPos, 5, (255, 0, 0), 10)

		if prevBoxPos != None:
			delta = ((boxPos[0] - prevBoxPos[0]) * mouseAcc, (boxPos[1] - prevBoxPos[1]) * mouseAcc)
			win32api.SetCursorPos(tuple(map(operator.add, cursorPos, delta)))			
		prevBoxPos = boxPos
	
	cv2.imshow("camera", frame)		

	k = cv2.waitKey(5) & 0xFF
	if k == 27:
		break
	
cv2.destroyAllWindows()
