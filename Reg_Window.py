import sys, cv2, numpy, time, os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import labeling
import cnn_train
import data_Increase
import AES
import shutil
import dlib
import sqlite3
#from Face_Window import Face_Window

Train_dir = "Train"

class Reg_Window(QDialog):
    face_id = ()
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Reg Window')
        self.setGeometry(600, 400, 400, 300)

        lbl_name = QLabel("아이디", self)
        lbl_name.move(25, 25)
        self.line_name = QLineEdit("",self)
        self.line_name.move(25 + 100, 22)
        self.btn_name = QPushButton("중복확인", self)
        self.btn_name.move(25 + 100 + 170, 20)

        lbl_reg = QLabel("Face_id 등록", self)
        lbl_reg.move(25, 60)
        self.btn_reg = QPushButton("등록", self)
        self.btn_reg.move(25 + 100, 55)
        self.btn_reg.setEnabled(False)

        lbl_naver_id = QLabel("네이버 아이디", self)
        lbl_naver_id.move(25, 95)
        self.line_naver_id = QLineEdit("", self)
        self.line_naver_id.move(25 + 100, 88)

        lbl_naver_pw = QLabel("비밀번호", self)
        lbl_naver_pw.move(25, 130)
        self.line_naver_pw = QLineEdit("", self)
        self.line_naver_pw.setEchoMode(QLineEdit.Password)
        self.line_naver_pw.move(25 + 100, 121)

        self.btn_on = QPushButton("완료", self)
        self.btn_on.resize(100, 25)
        self.btn_on.move(5, 250)

        self.btn_back = QPushButton("뒤로가기", self)
        self.btn_back.resize(100, 25)
        self.btn_back.move(105, 250)

        self.btn_back.clicked.connect(self.back_clicked)
        self.btn_on.clicked.connect(self.naver)
        self.btn_reg.clicked.connect(self.reg_clicked)
        self.btn_name.clicked.connect(self.overlap)

    def back_clicked(self):
        if Face_Window.dir_count == 1:
            if os.path.isdir(Train_dir + '/' + Face_Window.face_id):
                shutil.rmtree(Train_dir + '/' + Face_Window.face_id)
            self.accept()
        else:
            self.accept()

    def cnns(self):
        self.accept()
        self.data_inc()
        self.label()
        self.cnn_train()

    def naver(self):
        name=self.line_name.text()
        id=self.line_naver_id.text()
        pw = AES.cipherinstance.encrypt(self.line_naver_pw.text())
        print(pw)

        con=sqlite3.connect('test.db')
        cur=con.cursor()
        cur.execute("insert into log(name,login_time,id,pw) values(?,datetime('now','localtime'),?,?);",(name,id,pw))
        con.commit()
        con.close()

        self.cnns()

    def overlap(self):
        Reg_Window.face_id = self.line_name.text()
        if os.path.exists(Train_dir + '/' + Reg_Window.face_id): # 파일 있으면 에러
            reply = QMessageBox.question(self, 'Message', '아이디가 중복됩니다.')
        else:
            reply = QMessageBox.question(self, 'Message', '확인되었습니다.')

            if reply == QMessageBox.Yes:
                self.btn_reg.setEnabled(True)


    def reg_clicked(self):
        win = Face_Window()
        r = win.showModal()

    def onCancelButtonClicked(self):
        self.reject()

    def showModal(self):
        return super().exec_()

    #CNN 데이터 증가/라벨링/학습
    def label(self):
        labeling.labeling()
    def cnn_train(self):
        cnn_train.cnn()
    def data_inc(self):
        data_Increase.increase(Face_Window.face_id)

#등록 누를시 Face_id 등록
class Face_Window(QDialog):

    count = 0
    reg_count = 0
    dir_count = 0
    def __init__(self):
        super().__init__()
        self.make_dir()
        self.initUI()

    def make_dir(self):
        Face_Window.face_id = Reg_Window.face_id
        print(Face_Window.face_id)

        if not os.path.isdir(Train_dir + '/' + Face_Window.face_id):
            os.mkdir(Train_dir + '/' + Face_Window.face_id)
            Face_Window.dir_count = 1

    def initUI(self):
        self.setWindowTitle("cam_exam")
        self.setGeometry(150, 150, 650, 540)
        self.cpt = cv2.VideoCapture(0)
        self.fps = 30
        self.sens = 300
        self.cnt = 0
        self.frame = QLabel(self)
        self.frame.resize(640, 480)
        self.frame.setScaledContents(True)
        self.frame.move(5, 5)

        self.btn_on = QPushButton("face_id 등록", self)
        self.btn_on.resize(100, 25)
        self.btn_on.move(5, 490)
        self.btn_on.clicked.connect(self.start)

        self.btn_train = QPushButton("확인", self)
        self.btn_train.resize(100, 25)
        self.btn_train.move(5 + 100 + 5, 490)
        self.btn_train.clicked.connect(self.ok)

        self.prt = QLabel(self)
        self.prt.resize(200, 25)
        self.prt.move(5 + 105 + 105, 490)

    def ok(self):
        self.accept()
    def start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000. / self.fps)

    def nextFrameSlot(self):
        face_cascade_file = "haarcascade_frontalface_default.xml"
        cascade = cv2.CascadeClassifier(face_cascade_file)

        _, cam = self.cpt.read()
        cam = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)
        cam = cv2.flip(cam, 1)
        face_list = cascade.detectMultiScale(cam, 1.3, 5)

        for face in face_list:

            (x, y, w, h) = face
            cam = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)
            cropped = cam[y:y+h, x:x+w]
            # 이미지를 저장
            file_name_path = str(Train_dir) + '/' + str(Face_Window.face_id) + '/' + str(Face_Window.face_id) + str(Face_Window.count) + '.png'
            if (Face_Window.count % 2 == 0):
                cv2.imwrite(file_name_path, cropped)
            Face_Window.count += 1

            cv2.rectangle(cam, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cam = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)

        img = QImage(cam, cam.shape[1], cam.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.frame.setPixmap(pix)

        if Face_Window.count == 60:
            self.stop()

    def stop(self):
        self.frame.setPixmap(QPixmap.fromImage(QImage()))
        self.timer.stop()

    def onCancelButtonClicked(self):
        self.reject()
    def showModal(self):
        return super().exec_()

