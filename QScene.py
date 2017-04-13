from PyQt4.QtGui import QGraphicsScene
from PyQt4 import QtCore

__author__ = 'dreyus95'


class QScene(QGraphicsScene):
    """
        Extended QGraphicsScene class with added mousePressEvent.
    """
    def __init__(self,mainGUI):
        QGraphicsScene.__init__(self)
        self.mainGUI = mainGUI
        self.counter=0


    def mousePressEvent(self, event):
        """
        - used only to keep track of the dots on the picture used
          for creating a rectangle that will be saved as a frame for hiding.

        :return: None
        """

        x = event.scenePos().x()
        y = event.scenePos().y()
        if event.button()==QtCore.Qt.LeftButton:
            self.counter+=1
            if self.counter%2==0 :
                self.mainGUI.secondCoordinate=(x,y)
                self.mainGUI.scene.addEllipse(x,y,2,2,self.mainGUI.pen)
                self.mainGUI.scene.update()
                self.counter=0
            else:
                self.mainGUI.firstCoordinate=(x,y)
                self.mainGUI.scene.addEllipse(x,y,2,2,self.mainGUI.pen)
                self.mainGUI.scene.update()


