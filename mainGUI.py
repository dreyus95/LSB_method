__author__ = 'dreyus95'

from PIL import Image
from PyQt4.QtCore import QRectF
from PyQt4.QtGui import *
from PyQt4 import QtCore
import os
import cv2
from QScene import QScene
from LSB_method import LSB_method
from moviepy.editor import ImageSequenceClip,VideoFileClip
import numpy as np

class MainGUI(QWidget):
    """
        Main class that represents the GUI of application
        Usage:
            - uploading a picture
            - cutting a frame out of the picture
            - hiding a frame inside a picture
            - extracting the hidden frame back from stego object
            -------------------------------------
            - selecting folder with frames
            - running LSB method on every frame -> creates a video sequence (stego object)
            - extracting hidden images from every frame of the video sequence
    """

    def __init__(self, parent=None):
        super(MainGUI, self).__init__(parent)

        self.lsb = LSB_method()

        #info on the original image/frames
        self.fileLame = None
        self.filePath = None
        self.framesPath = None

        #image after the process of hiding
        self.combinedImage = None

        #components used for displaying picture in GUI
        self.pixmap = None
        self.scene = QScene(self)
        self.view = QGraphicsView()
        self.view.setScene(self.scene)

        #used for drawing rectangle and saving cropped image as a rectangle
        self.firstCoordinate = None
        self.secondCoordinate = None
        self.rect = None

        self.pen = QPen()
        self.pen.setColor(QtCore.Qt.red)

        vbox = QGridLayout()
        hboxImage = QHBoxLayout()
        hboxVid = QHBoxLayout()

        #creating a box with instructions on how to use the GUI

        instructionText = "Choose an image which will be displayed on the window.\n" \
                          "Click 2 dots to form a rectangle which will be saved for further processing.\n" \
                          "-----------------------------------------------------------------------------------\n" \
                          "Choose folder with video frames (choose the first frame in folder)\n" \
                          "Press \"Hide frames\" button to begin processing.\n" \
                          "Press \" Extract frames\" button to extract frames from newly created video.  "



        instructionBox = QTextEdit(self)
        instructionBox.setDisabled(True)
        instructionBox.setText(instructionText)

        self.selectImageButton = QPushButton("Select image")
        self.selectImageButton.clicked.connect(self.selectImageButtonCLicked)

        self.clearTagsButton = QPushButton("Clear tags")
        self.clearTagsButton.clicked.connect(self.clearTagsButtonClicked)
        self.clearTagsButton.setEnabled(False)

        self.drawFrameButton = QPushButton("Draw frame")
        self.drawFrameButton.clicked.connect(self.drawFrameButtonClicked)

        self.saveFrameButton = QPushButton("Save frame")
        self.saveFrameButton.clicked.connect(self.saveFrameButtonClicked)
        self.saveFrameButton.setEnabled(False)

        self.hideImageButton = QPushButton("Hide Image")
        self.hideImageButton.clicked.connect(self.hideImageButtonClicked)
        self.hideImageButton.setEnabled(False)

        self.extractHiddenImageButton = QPushButton("Extract hidden image")
        self.extractHiddenImageButton.clicked.connect(self.extractHiddenImageButtonClicked)
        self.extractHiddenImageButton.setEnabled(False)

        self.selectFramesButton = QPushButton("Select frames")
        self.selectFramesButton.clicked.connect(self.selectFramesButtonClicked)

        self.hideFramesButton = QPushButton("Hide frames")
        self.hideFramesButton.clicked.connect(self.hideFramesButtonClicked)
        self.hideFramesButton.setEnabled(False)


        self.extractHiddenFramesButton = QPushButton("Extract frames")
        self.extractHiddenFramesButton.clicked.connect(self.extractHiddenFramesButtonClicked)
        self.extractHiddenFramesButton.setEnabled(False)

        instructionBox.setFixedSize(800, 100)
        vbox.addWidget(instructionBox, 1, 0)

        vbox.addWidget(self.view)

        hboxImage.addWidget(self.selectImageButton)
        hboxImage.addWidget(self.clearTagsButton)
        hboxImage.addWidget(self.drawFrameButton)
        hboxImage.addWidget(self.saveFrameButton)
        hboxImage.addWidget(self.hideImageButton)
        hboxImage.addWidget(self.extractHiddenImageButton)

        #hboxImage.addStretch(1)
        vbox.addLayout(hboxImage, 3, 0)

        hboxVid.addWidget(self.selectFramesButton)
        hboxVid.addWidget(self.hideFramesButton)
        hboxVid.addWidget(self.extractHiddenFramesButton)

        #hboxVid.addStretch(1)
        vbox.addLayout(hboxVid, 4, 0)

        self.setLayout(vbox)
        self.setMinimumSize(800, 300)
        self.setWindowTitle('Select a frame from uploaded image, or select frames for a video')


    def selectImageButtonCLicked(self):
        """
            Method for uploading image into GUI
        """

        fileDialog = QFileDialog()
        name = fileDialog.getOpenFileName(self, 'Select file')
        self.load_image(name.__str__())
        self.clearTagsButton.setEnabled(True)
        self.saveFrameButton.setEnabled(True)

    def clearTagsButtonClicked(self):
        """
            Method for clearing tags on the picture such as dots and rectangle.
            Basically, a reset method.
        """
        self.firstCoordinate = None
        self.secondCoordinate = None
        self.drawFrameButton.setEnabled(True)
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        self.scene.update()

    def drawFrameButtonClicked(self):
        """
            Method for drawing a rectangle from 2 pointed dots on the picture.
            Used just to check what is going to be saved as a CROPPED image
            and used as a hidden frame.
        """
        if(self.firstCoordinate and self.secondCoordinate is not None):
            dimensions = self.getRectangleCoordinates()
            x =dimensions[0]
            y = dimensions[1]
            width = dimensions[2]
            height = dimensions[3]
            self.rect = QRectF(x,y,width,height)
            self.scene.addRect(self.rect,self.pen)
            self.scene.update()
            self.drawFrameButton.setEnabled(False)


    def saveFrameButtonClicked(self):
        """
            Method used to save the desired frame and use it as a hidden object
            which we want to hide into a picture and later on extract.
        """
        if(self.filePath and self.fileName is not None):
            fullPath = self.filePath+"/"+self.fileName
            img = cv2.imread(fullPath,cv2.IMREAD_COLOR)
            dimensions = self.getRectangleCoordinates()
            x = dimensions[0]
            y = dimensions[1]
            width = dimensions[2]
            height = dimensions[3]
            crop_img = img[y:y+height,x:x+width]
            cv2.imwrite(os.path.join(self.filePath, "CROPPED" + ".png"), crop_img)
            self.hideImageButton.setEnabled(True)


    def getRectangleCoordinates(self):
        """
            Method for extracting rectangle description:
                coordinates + width,height
        """
        x = min(self.firstCoordinate[0],self.secondCoordinate[0])
        y = min(self.firstCoordinate[1],self.secondCoordinate[1])
        width = abs(self.firstCoordinate[0]-self.secondCoordinate[0])
        height = abs(self.firstCoordinate[1]-self.secondCoordinate[1])
        return [x, y, width, height]


    def hideImageButtonClicked(self):
        """
            Method used to hide a frame inside another image.
        """
        publicImgPath = self.filePath+"/"+self.fileName
        hiddenImgPath = self.filePath+"/"+"CROPPED.png"
        self.combinedImage = self.lsb.hide_image(publicImgPath, hiddenImgPath)
        self.extractHiddenImageButton.setEnabled(True)
        res = np.asarray(self.combinedImage)
        res = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
        cv2.imwrite(self.filePath+"/"+"COMBINED.png", res)


    def selectFramesButtonClicked(self):
        """
            Method used to select a folder with frames that will be used to
            create a stego video sequence object.
        """
        fileDialog = QFileDialog()
        name = fileDialog.getOpenFileName(self, 'Select frames')
        framesPath, frames = os.path.split(str(name))
        self.framesPath = framesPath
        self.hideFramesButton.setEnabled(True)



    def extractHiddenImageButtonClicked(self):
        """
            Method used to extract the hidden image from a stego object
        """
        img = Image.fromarray(np.asarray(self.combinedImage), 'RGB')
        hidden = self.lsb.extract_hiddenImage(img)
        res = np.asarray(hidden)
        cv2.imwrite(self.filePath+"/"+"HIDDEN_prije.png", res)
        res = cv2.cvtColor(res, cv2.COLOR_RGB2BGR)
        cv2.imwrite(self.filePath+"/"+"HIDDEN_poslije.png", res)



    def hideFramesButtonClicked(self):
        """
            Method used to find the largest person in each frame and then save it
            inside that same frame, creating a video sequence of those "stego frames".
        """
        counter = 0
        path = self.framesPath
        dir = os.listdir(path)
        listOfFiles = []
        for file in dir:
            counter += 1

            publicImgPath = path+"/"+str(file)
            hog = cv2.HOGDescriptor()
            hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            img = cv2.imread(publicImgPath)
            (rects, weights) = hog.detectMultiScale(img, winStride=(4, 4),padding=(8, 8), scale=1.05)

            maxw, maxh = -1, -1
            finalX, finalY = 0, 0
            for (x, y, w, h) in rects:
               if w*h > maxw*maxh:
                    maxw, maxh = w, h
                    finalX, finalY = x, y

            crop_img = img[finalY:finalY+maxh, finalX:finalX+maxw]
            cv2.imwrite(os.path.join(path, "CROPPED" + ".png"), crop_img)
            hiddenImgPath = path+"/CROPPED.png"
            combination = self.lsb.hide_image(publicImgPath, hiddenImgPath)
            res = np.asarray(combination)
            listOfFiles.append(res)
            print "Written: ", file

        os.remove(path+"/CROPPED.png")
        out = ImageSequenceClip(listOfFiles, fps=50)
        out.to_videofile("output.avi", fps=50, codec='ffv1')

        print "Finished"
        self.extractHiddenFramesButton.setEnabled(True)


    def extractHiddenFramesButtonClicked(self):
        """
            Method used to divide a video sequence stego object into frames and extract
            hidden images from each frame.
            Method will save each extracted image into "/extracted" folder.
        """
        print "Extracting.................This might take a while!"

        if not os.path.isdir("extracted"):
            os.mkdir("extracted")

        vidcap = VideoFileClip("output.avi")
        counter = 0

        frames = [fr for fr in vidcap.iter_frames()]
        for frame in frames:
            counter += 1
            img = Image.fromarray(frame,'RGB')
            hidden = self.lsb.extract_hiddenImage(img)
            res = np.asarray(hidden)
            res = cv2.cvtColor(res, cv2.COLOR_RGB2BGR)
            cv2.imwrite("extracted/frame%d.png" % counter, res)     # save frame as PNG file
            print "Extracted: frame%d" % counter

        print "Done"






    def load_image(self,name):
        """
            Method that loads and displays image on the GUI
        """
        self.pixmap = QPixmap(name)
        filepath, filename = os.path.split(name)
        self.fileName = filename
        self.filePath = filepath
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        self.view.show()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    gui = MainGUI()
    gui.show()
    sys.exit(app.exec_())