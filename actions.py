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
        self.start_point = (0, 0) 

        # Ending coordinate, here (220, 220) 
        # represents the bottom right corner of rectangle 
        self.end_point = (0, 0) 

        self.zoomX = 1              # zoom factor w.r.t size of qlabel_image
        self.position = [0, 0]      # position of top left corner of qimage_label w.r.t. qimage_scaled
        self.panFlag = False        # to enable or disable pan
        self.pressed = False
        self.mode = 0
        self.history = Loopqueue(20)
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
        self.cvimage_scale =  cv2.resize(self.cvimage, (self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX))
        self.update()

    def loadImage(self, imagePath):
        ''' To load and display new image.'''
        # open raw file by opencv
        self.cvimage = cv2.imread(imagePath)
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
        
        self.cvimage_scale =  cv2.resize(self.cvimage, (self.qlabel_image.width(), self.qlabel_image.height()))

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
            
            if self.mode == 1:
                self.drwaDuiGou(x,y)
                self.update()

            if self.mode == 2:
                self.start_point=(x * self.cvimage.shape[1] / self.qlabel_image.width(),y* self.cvimage.shape[0] / self.qlabel_image.height())
                self.srcimg = self.cvimage
                #self.cvimage = self.huarect.dwan()
                #self.update()  

    def mouseMoveAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
        if self.pressed:
            dx, dy = x - self.pressed.x(), y - self.pressed.y()         # calculate the drag vector
            self.position = self.anchor[0] - dx, self.anchor[1] - dy    # update pan position using drag vector
            self.update()                                               # show the image with udated pan position

        if self.mode == 2:
            self.end_point=(x * self.cvimage.shape[1] / self.qlabel_image.width(),y* self.cvimage.shape[0] / self.qlabel_image.height())
            self.cvimage = self.srcimg.copy()
            cv2.rectangle(self.cvimage, self.start_point, self.end_point, (255,0,0), 1) 
            self.update()  

    def mouseReleaseAction(self, QMouseEvent):
        self.pressed = None                                             # clear the starting point of drag vector
        if self.mode == 2:    
            #self.cvimage = self.huarect.dwan().copy()
            self.update()  

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
        posx = posx  * self.cvimage.shape[1] / self.qlabel_image.width()
        posy = posy  * self.cvimage.shape[0] / self.qlabel_image.height()
        pts = np.array([[posx-lengthx, posy-lengthx],  [posx, posy], [posx+lengthy, posy-lengthy]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(self.cvimage, [pts], False, (255, 0, 0), 2)
