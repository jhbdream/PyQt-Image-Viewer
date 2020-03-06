# -*- coding: utf-8 -*-


''' A basic GUi to use ImageViewer class to show its functionalities and use cases. '''

from PyQt4 import QtCore, QtGui, uic

from actions import ImageViewer
import sys, os
import cv2

gui = uic.loadUiType("main.ui")[0]     # load UI file designed in Qt Designer
VALID_FORMAT = ('.BMP', '.GIF', '.JPG', '.JPEG', '.PNG', '.PBM', '.PGM', '.PPM', '.TIFF', '.XBM')  # Image formats supported by Qt

def getImages(folder):
    ''' Get the names and paths of all the images in a directory. '''
    image_list = []
    if os.path.isdir(folder):
        for file in os.listdir(folder):
            print file
            if file.upper().endswith(VALID_FORMAT):
                im_path = os.path.join(folder, file)
                #im_path = unicode(im_path, "utf-8")
                image_obj = {'name': file, 'path': im_path }
                image_list.append(image_obj)
    return image_list

class Iwindow(QtGui.QMainWindow, gui):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.cntr, self.numImages = -1, -1  # self.cntr have the info of which image is selected/displayed

        self.image_viewer = ImageViewer(self.qlabel_image)
        self.__connectEvents()
        self.showMaximized()

    def __connectEvents(self):
        self.open_folder.clicked.connect(self.selectDir)
        self.next_im.clicked.connect(self.nextImg)
        self.prev_im.clicked.connect(self.prevImg)
        self.qlist_images.itemClicked.connect(self.item_click)
        self.save_im.clicked.connect(self.saveImg)

        self.zoom_plus.clicked.connect(self.zoomPlus)
        self.zoom_minus.clicked.connect(self.zoomMinus)
        self.reset_zoom.clicked.connect(self.resetZoom)

        self.toggle_line.toggled.connect(self.action_line)
        self.toggle_rect.toggled.connect(self.action_rect)
        self.toggle_move.toggled.connect(self.action_move)

        self.undo.clicked.connect(self.image_viewer.funundo)
        self.clear_all.clicked.connect(self.action_clear_all)
        self.redo.clicked.connect(self.action_redo)


    def selectDir(self):
        ''' Select a directory, make list of images in it and display the first image in the list. '''
        # open 'select folder' dialog box
        self.folder = unicode(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        print self.folder
        if not self.folder:
            QtGui.QMessageBox.warning(self, 'No Folder Selected', 'Please select a valid Folder')
            return
        
        self.logs = getImages(self.folder)
        self.numImages = len(self.logs)

        # make qitems of the image names
        self.items = [QtGui.QListWidgetItem(log['name']) for log in self.logs]
        for item in self.items:
            self.qlist_images.addItem(item)

        # display first image and enable Pan 
        self.cntr = 0
        self.image_viewer.enablePan(False)
        self.image_viewer.loadImage(self.logs[self.cntr]['path'])
        self.qlist_images.setItemSelected(self.items[self.cntr], True)

        # enable the next image button on the gui if multiple images are loaded
        if self.numImages > 1:
            self.next_im.setEnabled(True)

    def resizeEvent(self, evt):
        if self.cntr >= 0:
            self.image_viewer.onResize()

    def nextImg(self):
        self.qlabel_image.setCursor(QtCore.Qt.CrossCursor)
        self.image_viewer.funmode(4)
        self.image_viewer.score="A"
        self.image_viewer.enablePan(True)

    def prevImg(self):
        self.qlabel_image.setCursor(QtCore.Qt.CrossCursor)
        self.image_viewer.funmode(4)
        self.image_viewer.score="A+"
        self.image_viewer.enablePan(True)

    def zoomPlus(self):
        self.qlabel_image.setCursor(QtCore.Qt.CrossCursor)
        self.image_viewer.funmode(4)
        self.image_viewer.score="A-"
        self.image_viewer.enablePan(True)

    def zoomMinus(self):
        self.qlabel_image.setCursor(QtCore.Qt.CrossCursor)
        self.image_viewer.funmode(4)
        self.image_viewer.score="C"
        self.image_viewer.enablePan(True)

    def resetZoom(self):
        self.qlabel_image.setCursor(QtCore.Qt.CrossCursor)
        self.image_viewer.funmode(4)
        self.image_viewer.score="B"
        self.image_viewer.enablePan(True)

    def saveImg(self):
        #cv2.imwrite(self.logs[self.cntr]['path'],self.image_viewer.cvimage)
        print self.logs[self.cntr]['path']
        path = self.logs[self.cntr]['path'].split('.')
        newpath = path[0] + "OK." + path[1] 
        print newpath
        SAVEIMG = cv2.cvtColor(self.image_viewer.cvimage, cv2.COLOR_RGB2BGR)

        #cv2.imwrite(newpath,SAVEIMG)
        cv2.imencode('.jpg',SAVEIMG)[1].tofile(newpath)#保存图片


    def item_click(self, item):
        self.cntr = self.items.index(item)
        self.image_viewer.loadImage(self.logs[self.cntr]['path'])

    def action_line(self):
        if self.toggle_line.isChecked():
            self.qlabel_image.setCursor(QtCore.Qt.CrossCursor)
            self.image_viewer.funmode(1)
            self.image_viewer.enablePan(True)
        
    def action_rect(self):
        if self.toggle_rect.isChecked():
            self.qlabel_image.setCursor(QtCore.Qt.CrossCursor)
            self.image_viewer.funmode(2)
            self.image_viewer.enablePan(True)

    def action_move(self):
        if self.toggle_move.isChecked():
            self.qlabel_image.setCursor(QtCore.Qt.OpenHandCursor)
            self.image_viewer.funmode(3)
            self.image_viewer.enablePan(True)

    def action_undo(self):
        self.image_viewer.funundo()

    def action_clear_all(self):
        self.image_viewer.clear_all()


    def action_redo(self):
        self.image_viewer.funredo()
   
def main():
    app = QtGui.QApplication(sys.argv)
    app.setStyle(QtGui.QStyleFactory.create("Cleanlooks"))
    app.setPalette(QtGui.QApplication.style().standardPalette())
    parentWindow = Iwindow(None)
    sys.exit(app.exec_())

if __name__ == "__main__":
    print __doc__
    main()