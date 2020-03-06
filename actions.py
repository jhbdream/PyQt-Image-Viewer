# -*- coding: utf-8 -*-

from PyQt4.QtGui import QImage, QPixmap, QPainter
from PyQt4 import QtCore, QtGui
import cv2
from matplotlib import pyplot as plt
import numpy as np
from fifo import Loopqueue
from collections import deque


class ImageViewer:
    ''' Basic image viewer class to show an image with zoom and pan functionaities.
        Requirement: Qt's Qlabel widget name where the image will be drawn/displayed.
    '''
    def __init__(self, qlabel):
        self.qlabel_image = qlabel                            # widget/window name where image is displayed (I'm usiing qlabel)
        self.qimage_scaled = QImage()                         # scaled image to fit to the size of qlabel_image
        self.qpixmap = QPixmap()                              # qpixmap to fill the qlabel_image
        self.cvimage = None
        self.srcimg = None
        self.score = None

        self.start_point = (0, 0) 

        # Ending coordinate, here (220, 220) 
        # represents the bottom right corner of rectangle 
        self.end_point = (0, 0) 

        self.zoomX = 1              # zoom factor w.r.t size of qlabel_image
        self.position = [0, 0]      # position of top left corner of qimage_label w.r.t. qimage_scaled
        self.panFlag = False        # to enable or disable pan
        self.pressed = False
        self.mode = 0
        self.history = Loopqueue(40)
        self.qlabel_image.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        self.__connectEvents()
        self.queue = deque()

    def __connectEvents(self):
        # Mouse events
        self.qlabel_image.mousePressEvent = self.mousePressAction
        self.qlabel_image.mouseMoveEvent = self.mouseMoveAction
        self.qlabel_image.mouseReleaseEvent = self.mouseReleaseAction

    def onResize(self):
        ''' things to do when qlabel_image is resized '''
        self.qpixmap = QPixmap(self.qlabel_image.size())
        self.qpixmap.fill(QtCore.Qt.gray)
        #self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
        #self.cvimage_scale =  cv2.resize(self.cvimage, (self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX))
        self.update()

    def loadImage(self, imagePath):
        ''' To load and display new image.'''
        print imagePath
        # open raw file by opencv
        #self.cvimage = cv2.imread(imagePath)
        self.cvimage = cv2.imdecode(np.fromfile(imagePath,dtype=np.uint8),cv2.IMREAD_COLOR)
        # convert image to qimage to show
        self.cvimage = cv2.cvtColor(self.cvimage, cv2.COLOR_BGR2RGB)
        self.zoomX = 1
        self.position = [0, 0]
       
        #cv2.imshow('cvimage', self.cvimage )
        self.update()

    def update(self):
        ''' This function actually draws the scaled image to the qlabel_image.
            It will be repeatedly called when zooming or panning.
            So, I tried to include only the necessary operations required just for these tasks. 
        '''
        
        #dim = self.qlabel_image.width() /  self.cvimage.shape[1]
        #self.cvimage_scale =  cv2.resize(self.cvimage,None,dim,dim,interpolation = cv2.INTER_AREA)
        #self.cvimage_scale = self.process_image(self.cvimage,self.qlabel_image.width() )
        target_size=[self.qlabel_image.height(),self.qlabel_image.width()]

        self.cvimage_scale = self.resize_img_keep_ratio(self.cvimage,target_size)

        
        #self.cvimage_scale = self.cvimage
        self.qimage_scaled = QtGui.QImage(self.cvimage_scale, self.cvimage_scale.shape[1], self.cvimage_scale.shape[0],self.cvimage_scale.strides[0], QtGui.QImage.Format_RGB888)
        ##self.qimage = QImage(imagePath)
        self.qpixmap = QPixmap(self.qlabel_image.size())

        if not self.qimage_scaled.isNull():
            # check if position is within limits to prevent unbounded panning.
            px, py = self.position
            px = px if (px <= self.qimage_scaled.width() - self.qlabel_image.width()) else (self.qimage_scaled.width() - self.qlabel_image.width())
            py = py if (py <= self.qimage_scaled.height() - self.qlabel_image.height()) else (self.qimage_scaled.height() - self.qlabel_image.height())
            px = px if (px >= 0) else 0
            py = py if (py >= 0) else 0
            self.position = (px, py)

            if self.zoomX == 1:
                self.qpixmap.fill(QtCore.Qt.white)

            # the act of painting the qpixamp
            painter = QPainter()
            painter.begin(self.qpixmap)
            painter.drawImage(QtCore.QPoint(0, 0), self.qimage_scaled,
                    QtCore.QRect(self.position[0], self.position[1], self.qlabel_image.width() , self.qlabel_image.height()) )
            painter.end()

            self.qlabel_image.setPixmap(self.qpixmap)
        else:
            pass

    def mousePressAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
       
        if self.panFlag:
            self.pressed = QMouseEvent.pos()    # starting point of drag vector
            self.anchor = self.position         # save the pan position when panning starts
            px, py = self.anchor
           
            #posx =  x - ( self.qlabel_image.width() - self.cvimage_scale.shape[1] ) / 2
            #posy = y
            print 'x:[%d] y:[%d] qlabel_image.width:[%d] cvimage_scale.shape:[%d] '% (x,y,self.qlabel_image.width(),self.cvimage_scale.shape[1])


            x = x  * self.cvimage.shape[1] / self.cvimage_scale.shape[1]
            y = y  * self.cvimage.shape[0] / self.cvimage_scale.shape[0]
            
            #x = posx + px
            #y = posy + py
            if self.mode == 1:
                self.drwaDuiGou( x,y )
                self.update()

            if self.mode == 2:
                #self.start_point=(x * self.cvimage.shape[1] / self.qlabel_image.width(),y* self.cvimage.shape[0] / self.qlabel_image.height())
                #self.srcimg = self.cvimage
                #self.cvimage = self.huarect.dwan()
                #self.update()  
                self.drwaWrong(x,y)
                self.update()
            if self.mode == 3:
                self.drwacuohao(x,y)
                self.update()

            if self.mode == 4:
                self.drwaScore(x,y)
                self.update()


    def mouseMoveAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
        if self.pressed:
            dx, dy = x - self.pressed.x(), y - self.pressed.y()         # calculate the drag vector
            self.position = self.anchor[0] - dx, self.anchor[1] - dy    # update pan position using drag vector
            self.update()                                               # show the image with udated pan position

        #if self.mode == 2:
            #self.end_point=(x * self.cvimage.shape[1] / self.qlabel_image.width(),y* self.cvimage.shape[0] / self.qlabel_image.height())
            #self.cvimage = self.srcimg.copy()
            #cv2.rectangle(self.cvimage, self.start_point, self.end_point, (255,0,0), 1) 
            #self.update()  

    def mouseReleaseAction(self, QMouseEvent):
        self.pressed = None                                             # clear the starting point of drag vector
        

    def zoomPlus(self):
        self.zoomX += 1
        px, py = self.position
        px += self.qlabel_image.width()/2
        py += self.qlabel_image.height()/2
        self.position = (px, py)
        self.cvimage =  cv2.resize(self.cvimage, (self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX))
        self.update()

    def zoomMinus(self):
        if self.zoomX > 1:
            self.zoomX -= 1
            px, py = self.position
            px -= self.qlabel_image.width()/2
            py -= self.qlabel_image.height()/2
            self.position = (px, py)
            self.cvimage =  cv2.resize(self.cvimage, (self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX))
            self.update()

    def resetZoom(self):
        self.zoomX = 1
        self.position = [0, 0]
        self.cvimage =  cv2.resize(self.cvimage, (self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX))
        self.update()

    def enablePan(self, value):
        self.panFlag = value

    def funmode(self, value):
        self.mode = value
        print self.mode
         
    def funundo(self):
        img = self.history.pop()
        if not img.any() == False:
            self.cvimage=img
            self.update()

    def funclear_all(self):
        print "clear all"

    def funredo(self):
        print "redo"

    def drwaDuiGou(self,posx,posy):
        self.history.push(self.cvimage.copy())
        lengthx =  self.qlabel_image.width() * self.zoomX * self.cvimage.shape[1] / self.qlabel_image.width() / 20 
        lengthy =  self.qlabel_image.height() * self.zoomX * self.cvimage.shape[0] / self.qlabel_image.height() / 10
        #posx = posx  * self.cvimage.shape[1] / self.qlabel_image.width()
        #posy = posy  * self.cvimage.shape[0] / self.qlabel_image.height()
        pts = np.array([[posx-lengthx, posy-lengthx],  [posx, posy], [posx+lengthy, posy-lengthy]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(self.cvimage, [pts], False, (255, 0, 0), 2)
    
    def drwaWrong(self,posx,posy):
        print "drwa wrong"
        self.history.push(self.cvimage.copy())
        lengthx =  self.qlabel_image.width() * self.zoomX * self.cvimage.shape[1] / self.qlabel_image.width() / 30 
        lengthy =  self.qlabel_image.height() * self.zoomX * self.cvimage.shape[0] / self.qlabel_image.height() / 10
        #posx = posx  * self.cvimage.shape[1] / self.qlabel_image.width()
        #posy = posy  * self.cvimage.shape[0] / self.qlabel_image.height()
        print posx
        cv2.line(self.cvimage,(posx-lengthx,posy),(posx+lengthx,posy),(255, 0, 0),3)

    def drwaScore(self,posx,posy):
        print "drwa wrong"
        self.history.push(self.cvimage.copy())
        cv2.putText(self.cvimage, self.score, (posx,posy), cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 0, 0), 2)

    def drwacuohao(self,posx,posy):
        self.history.push(self.cvimage.copy())
        lengthx =  self.qlabel_image.width() * self.zoomX * self.cvimage.shape[1] / self.qlabel_image.width() / 50 
        lengthy =  self.qlabel_image.height() * self.zoomX * self.cvimage.shape[0] / self.qlabel_image.height() / 50
        #posx = posx  * self.cvimage.shape[1] / self.qlabel_image.width()
        #posy = posy  * self.cvimage.shape[0] / self.qlabel_image.height()
        print posx
        cv2.line(self.cvimage,(posx-lengthx,posy-lengthy),(posx+lengthx,posy+lengthy),(255, 0, 0),2)
        cv2.line(self.cvimage,(posx+lengthx,posy-lengthy),(posx-lengthx,posy+lengthy),(255, 0, 0),2)


    def process_image(self,img, min_side):
        size = img.shape
        h, w = size[0], size[1]
        #长边缩放为min_side
        scale = max(w, h) / float(min_side)
        new_w, new_h = int(w/scale), int(h/scale)
        resize_img = cv2.resize(img, (new_w, new_h))
        # 填充至min_side * min_side
        if new_w % 2 != 0 and new_h % 2 == 0:
            top, bottom, left, right = (min_side-new_h)/2, (min_side-new_h)/2, (min_side-new_w)/2 + 1, (min_side-new_w)/2
        elif new_h % 2 != 0 and new_w % 2 == 0:
            top, bottom, left, right = (min_side-new_h)/2 + 1, (min_side-new_h)/2, (min_side-new_w)/2, (min_side-new_w)/2
        elif new_h % 2 == 0 and new_w % 2 == 0:
            top, bottom, left, right = (min_side-new_h)/2, (min_side-new_h)/2, (min_side-new_w)/2, (min_side-new_w)/2
        else:
            top, bottom, left, right = (min_side-new_h)/2 + 1, (min_side-new_h)/2, (min_side-new_w)/2 + 1, (min_side-new_w)/2
        pad_img = cv2.copyMakeBorder(resize_img, int(top), int(bottom), int(left), int(right), cv2.BORDER_CONSTANT, value=[0,0,0]) #从图像边界向上,下,左,右扩的像素数目

        return pad_img

    def resize_img_keep_ratio(self,img,target_size):
        old_size= img.shape[0:2]
        print len(old_size)
        #ratio = min(float(target_size)/(old_size))
        ratio = min(float(target_size[i])/(old_size[i]) for i in range(len(old_size)))
        new_size = tuple([int(i*ratio) for i in old_size])
        img = cv2.resize(img,(new_size[1], new_size[0]))
        #pad_w = target_size[1] - new_size[1]
        #pad_h = target_size[0] - new_size[0]
        #top,bottom = pad_h//2, pad_h-(pad_h//2)
        #left,right = pad_w//2, pad_w -(pad_w//2)
        #img_new = cv2.copyMakeBorder(img,top,bottom,left,right,cv2.BORDER_CONSTANT,None,(255,255,255))
        return img
