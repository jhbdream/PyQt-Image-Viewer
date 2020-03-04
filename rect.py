import cv2
import numpy as np

class dRect:
    def __init__(self):
        # Start coordinate, here (5, 5) 
        # represents the top left corner of rectangle 
        self.start_point = (0, 0) 

        # Ending coordinate, here (220, 220) 
        # represents the bottom right corner of rectangle 
        self.end_point = (0, 0) 

        # Blue color in BGR 
        self.color = (255, 0, 0) 

        # Line thickness of 2 px 
        self.thickness = 2
        self.cp_img = None
        self.src_img=None

    def dwan(self):
        
        cv2.rectangle(self.src_img, self.start_point, self.end_point, self.color, self.thickness) 

        return self.src_img

    def setstart(self,x,y,img):
        self.start_point = (x,y) 
        self.src_img = img.copy()

    def setend(self,x,y):
        self.end_point = (x,y) 
