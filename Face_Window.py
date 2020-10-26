from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, cv2, numpy, time
import dlib

class Face_Window(QDialog):
    count = 0

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("cam_exam")
        self.setGeometry(150, 150, 650, 540)
        self.cpt = cv2.VideoCapture(0)
        self.fps = 30
        self.sens = 300
        _, self.img_o = self.cpt.read()
        self.img_o = cv2.cvtColor(self.img_o, cv2.COLOR_RGB2GRAY)
        cv2.imwrite('img_o.jpg', self.img_o)

        self.cnt = 0

        self.frame = QLabel(self)
        self.frame.resize(640, 480)
        self.frame.setScaledContents(True)
        self.frame.move(5, 5)

        self.btn_on = QPushButton("켜기", self)
        self.btn_on.resize(100, 25)
        self.btn_on.move(5, 490)
        self.btn_on.clicked.connect(self.start)

        self.btn_off = QPushButton("끄기", self)
        self.btn_off.resize(100, 25)
        self.btn_off.move(5 + 100 + 5, 490)
        self.btn_off.clicked.connect(self.stop)


        self.prt = QLabel(self)
        self.prt.resize(200, 25)
        self.prt.move(5 + 105 + 105, 490)


    def start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000. / self.fps)

    def nextFrameSlot(self):

        face_cascade_file = "haarcascade_frontalface_default.xml"
        cascade = cv2.CascadeClassifier(face_cascade_file)

        #detector = dlib.get_frontal_face_detector()

        _, cam = self.cpt.read()
        cam = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)
        cam = cv2.flip(cam, 1)
        self.img_p = cv2.cvtColor(cam, cv2.COLOR_RGB2GRAY)
        img = QImage(cam, cam.shape[1], cam.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.frame.setPixmap(pix)
        face_list = cascade.detectMultiScale(cam, 1.3, 5)

        for face in face_list:

            (x, y, w, h) = face
            face_x1, face_y1, face_x2, face_y2 = x, y, x + w, y + h
            cam = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)
            cropped = cam[y - int(h / 4):y + h + int(h / 4), x - int(w / 4):x + w + int(w / 4)]
            # 이미지를 저장
            file_name_path = 'O-image' + '/' + 'HH' + '/' + 'HH' + '.' + str(Face_Window.count) + '.jpg'
            cv2.imwrite(file_name_path, cropped)
            Face_Window.count += 1

            if Face_Window.count == 10:
                self.stop()

    def stop(self):
        self.frame.setPixmap(QPixmap.fromImage(QImage()))
        self.timer.stop()

    def compare(self, img_o, img_p):
        err = numpy.sum((img_o.astype("float") - img_p.astype("float")) ** 2)
        err /= float(img_o.shape[0] * img_p.shape[1])

    def onCancelButtonClicked(self):
        self.reject()
    def showModal(self):
        return super().exec_()