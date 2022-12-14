import cv2
import numpy as np
# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
from PyQt5 import QtCore

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#from PyQt4 import QtTest

import pyqtgraph as pg
import sys
import time
from process import Process
from webcam import Webcam
from video import Video
from interface import waitKey, plotXY

class Communicate(QObject):
    closeApp = pyqtSignal()
    
    
class GUI(QMainWindow, QThread):
    def __init__(self):
        super(GUI,self).__init__()
        self.initUI()
        self.webcam = Webcam()
        self.video = Video()
        self.input = self.webcam
        self.dirname = ""
        print("Input: webcam")
        self.statusBar.showMessage("Input: webcam",5000)
        self.btnOpen.setEnabled(False)
        self.process = Process()
        self.status = False
        self.frame = np.zeros((10,10,3),np.uint8)
        #self.plot = np.zeros((10,10,3),np.uint8)
        self.bpm = 0
        
    def initUI(self):
    
        #set font
        font = QFont()
        font.setPointSize(16)
        
        #widgets
        self.btnStart = QPushButton("Start", self)
        self.btnStart.move(440,520)
        self.btnStart.setFixedWidth(200)
        self.btnStart.setFixedHeight(50)
        self.btnStart.setFont(font)
        self.btnStart.clicked.connect(self.run)
        
        self.btnOpen = QPushButton("Open", self)
        self.btnOpen.move(230,520)
        self.btnOpen.setFixedWidth(200)
        self.btnOpen.setFixedHeight(50)
        self.btnOpen.setFont(font)
        self.btnOpen.clicked.connect(self.openFileDialog)
        
        self.cbbInput = QComboBox(self)
        self.cbbInput.addItem("Webcam")
        self.cbbInput.addItem("Video")
        self.cbbInput.setCurrentIndex(0)
        self.cbbInput.setFixedWidth(200)
        self.cbbInput.setFixedHeight(50)
        self.cbbInput.move(20,520)
        self.cbbInput.setFont(font)
        self.cbbInput.activated.connect(self.selectInput)
        #-------------------
        
        self.lblDisplay = QLabel(self) #label to show frame from camera
        self.lblDisplay.setGeometry(10,10,640,480)
        self.lblDisplay.setStyleSheet("background-color: #000000")
        
        self.lblHR2 = QLabel(self) #label to show stable HR
        self.lblHR2.setGeometry(700,10,300,40)
        self.lblHR2.setFont(font)
        self.lblHR2.setText("Heart rate: ")

        #self.lblHR3 = QLabel(self) #label to show Respitation
        #self.lblHR3.setGeometry(900,110,300,40)
        #self.lblHR3.setFont(font)
        #self.lblHR3.setText("Respiration rate: ")

        
        #self.lblHR4 = QLabel(self) #label to show Respitation
        #self.lblHR4.setGeometry(900,150,300,40)
        #self.lblHR4.setFont(font)
        #self.lblHR4.setText("Spo2: ")
        
        
        # self.lbl_Age = QLabel(self) #label to show stable HR
        # self.lbl_Age.setGeometry(900,120,300,40)
        # self.lbl_Age.setFont(font)
        # self.lbl_Age.setText("Age: ")
        
        # self.lbl_Gender = QLabel(self) #label to show stable HR
        # self.lbl_Gender.setGeometry(900,170,300,40)
        # self.lbl_Gender.setFont(font)
        # self.lbl_Gender.setText("Gender: ")
        self.psd_Plt = pg.PlotWidget(self)
        
        self.psd_Plt.move(660,50)
        self.psd_Plt.resize(450,150)
        self.psd_Plt.setLabel('bottom', "PSD") 
        #dynamic plot
        self.signal_Plt = pg.PlotWidget(self)
        
        self.signal_Plt.move(660,250)
        self.signal_Plt.resize(450,150)
        self.signal_Plt.setLabel('bottom', "Signal") 
        
        self.fft_Plt = pg.PlotWidget(self)
        
        self.fft_Plt.move(660,425)
        self.fft_Plt.resize(450,150)
        self.fft_Plt.setLabel('bottom', "FFT") 
        
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(200)
        
        
        self.statusBar = QStatusBar()
        self.statusBar.setFont(font)
        self.setStatusBar(self.statusBar)
        
        #event close
        self.c = Communicate()
        self.c.closeApp.connect(self.close)
        
        #event change combobox index
        
        #config main window
        self.setGeometry(100,100,1160,640)
        #self.center()
        self.setWindowTitle("Heart rate monitor")
        self.show()
        
        
    def update(self):
        #z = np.random.normal(size=1)
        self.psd_Plt.clear()
        #u = np.random.normal(size=1)
        self.signal_Plt.clear()
        #self.signal_Plt.plot(np.column_stack((self.process.frame_count, self.process.angle)),pen='g')

        self.fft_Plt.clear()
        #self.fft_Plt.plot(np.column_stack((self.process.freqs_forehead, self.process.power_forehead)), pen = 'g')
        
        
   
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def closeEvent(self, event):
        reply = QMessageBox.question(self,"Message", "Are you sure want to quit",
            QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            event.accept()
            self.input.stop()
            cv2.destroyAllWindows()
        else: 
            event.ignore()
    
    def selectInput(self):
        self.reset()
        if self.cbbInput.currentIndex() == 0:
            self.input = self.webcam
            print("Input: webcam")
            self.btnOpen.setEnabled(False)
            #self.statusBar.showMessage("Input: webcam",5000)
        elif self.cbbInput.currentIndex() == 1:
            self.input = self.video
            print("Input: video")
            self.btnOpen.setEnabled(True)
            #self.statusBar.showMessage("Input: video",5000)
        
    
    def mousePressEvent(self, event):
        self.c.closeApp.emit()    
    
    # def make_bpm_plot(self):
    
        # plotXY([[self.process.times[20:],
                     # self.process.samples[20:]],
                    # [self.process.freqs,
                     # self.process.fft]],
                    # labels=[False, True],
                    # showmax=[False, "bpm"],
                    # label_ndigits=[0, 0],
                    # showmax_digits=[0, 1],
                    # skip=[3, 3],
                    # name="Plot",
                    # bg=None)
        
        # fplot = QImage(self.plot, 640, 280, QImage.Format_RGB888)
        # self.lblPlot.setGeometry(10,520,640,280)
        # self.lblPlot.setPixmap(QPixmap.fromImage(fplot))
    
    def key_handler(self):
        """
        cv2 window must be focused for keypresses to be detected.
        """
        self.pressed = waitKey(1) & 255  # wait for keypress for 10 ms
        if self.pressed == 27:  # exit program on 'esc'
            print("[INFO] Exiting")
            self.webcam.stop()
            sys.exit()
    
    def openFileDialog(self):
        self.dirname = QFileDialog.getOpenFileName(self, 'OpenFile',r"C:\Users\uidh2238\Desktop\test videos")
        #self.statusBar.showMessage("File name: " + self.dirname,5000)
    
    def reset(self):
        self.process.reset()
        self.lblDisplay.clear()
        self.lblDisplay.setStyleSheet("background-color: #000000")

    @QtCore.pyqtSlot()
    def main_loop(self):
        frame = self.input.get_frame()

        self.process.frame_in = frame
        self.process.run()
        
        #cv2.imshow("Processed", frame)
        
        self.frame = self.process.frame_in #get the frame to show in GUI
        frame_ROI = self.frame
        a = np.array(self.process.forehead_ROI)
        b = np.array(self.process.nose_ROI)
        c = np.array(self.process.face_ROI)

        frame_ROI = cv2.drawContours(frame_ROI, [a], 0, (255,0,0), 2)
        frame_ROI = cv2.drawContours(frame_ROI, [b] , 0, (0,255,0), 2)
        frame_ROI = cv2.drawContours(frame_ROI, [c] , 0, (0,0,255), 2)
        #print(self.f_fr.shape)        
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
        cv2.putText(self.frame, "FPS "+str(float("{:.2f}".format(self.process.fps))),
                       (20,460), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255),2)
        img = QImage(self.frame, self.frame.shape[1], self.frame.shape[0], 
                        self.frame.strides[0], QImage.Format_RGB888)
        self.lblDisplay.setPixmap(QPixmap.fromImage(img))
                
        if self.process.bpms.__len__() > 30:
            if(max(self.process.bpms-np.mean(self.process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
                self.lblHR2.setText("Heart rate: " + str(float("{:.2f}".format(np.mean(self.process.bpms)))) + " bpm")
        #if self.process.bpms.__len__() >50:
                #self.lblHR3.setText("Respiration rate: " + str(float("{:.2f}".format(self.process.respiration))) + " bpm")
        
        #if self.process.spo2 > 0:
            #self.lblHR4.setText("Spo2: " + str(float("{:.2f}".format(self.process.spo2))))
        #self.lbl_Age.setText("Age: "+str(self.process.age))
        #self.lbl_Gender.setText("Gender: "+str(self.process.gender))
        #self.make_bpm_plot()#need to open a cv2.imshow() window to handle a pause 
        #QtTest.QTest.qWait(10)#wait for the GUI to respond
        self.key_handler()  #if not the GUI cant show anything


    def run(self, input):
        self.reset()
        input = self.input
        self.input.dirname = self.dirname
        if self.input.dirname == "" and self.input == self.video:
            print("choose a video first")
            #self.statusBar.showMessage("choose a video first",5000)
            return
        if self.status == False:
            self.status = True
            input.start()
            self.btnStart.setText("Stop")
            self.cbbInput.setEnabled(False)
            self.btnOpen.setEnabled(False)
            self.lblHR2.clear()
            #self.lblHR3.clear()
            while self.status == True:
                self.main_loop()
        elif self.status == True:
            self.status = False
            input.stop()
            self.btnStart.setText("Start")
            self.cbbInput.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GUI()
    while ex.status == True:
        ex.main_loop()

    sys.exit(app.exec_())
