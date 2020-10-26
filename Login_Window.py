from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, cv2
from PIL import Image
import os, glob, numpy as np
from keras.models import load_model
from collections import Counter

import sqlite3

# 네이버 로그인 시키기 위한 모듈
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pyperclip
import time
import AES

class Login_Window(QDialog):

    count = 0

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("cam_exam")
        self.setGeometry(150, 150, 650, 540)

        self.cpt = cv2.VideoCapture(0)
        self.fps = 24
        self.sens = 300
        _, self.img_o = self.cpt.read()
        self.img_o = cv2.cvtColor(self.img_o, cv2.COLOR_BGR2RGB)
        self.cnt = 0

        #프레임 영역
        self.frame = QLabel(self)
        self.frame.resize(640, 480)
        self.frame.setScaledContents(True)
        self.frame.move(5, 5)

        #버튼 및 예측
        self.btn_on = QPushButton("시작", self)
        self.btn_on.resize(100, 25)
        self.btn_on.move(5, 490)
        self.btn_on.clicked.connect(self.link)

        # self.btn_stop = QPushButton("정지", self)
        # self.btn_stop.resize(100, 25)
        # self.btn_stop.move(5 + 100 + 5 , 490)
        # self.btn_stop.clicked.connect(self.stop)

        self.btn_off = QPushButton("종료", self)
        self.btn_off.resize(100, 25)
        self.btn_off.move(5 + 100 + 5, 490)
        self.btn_off.clicked.connect(self.exit)

        self.show()

    def exit(self):
        self.accept()
        Login_Window.count = 0
    def link(self):
        self.text, ok = QInputDialog.getText(self, 'Input', 'Enter your name:')

        if ok:
            self.start()

    def start(self):
        Login_Window.count = 0
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
            cropped = cam[y - int(h / 4):y + h + int(h / 4), x - int(w / 4):x + w + int(w / 4)]
            # 이미지를 저장
            file_name_path = 'Test/login' + '/' + 'new_image' + '.' + str(Login_Window.count) + '.png'
            cv2.imwrite(file_name_path, cropped)
            Login_Window.count += 1

            cv2.rectangle(cam, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cam = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)

            if Login_Window.count == 10:
                cv2.destroyAllWindows()
                self.recognition()

        img = QImage(cam, cam.shape[1], cam.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.frame.setPixmap(pix)
    def recognition(self):
        print(self.text)
        face_id = self.text
        print(face_id)
        caltech_dir = "./Test/login"

        Trian_dir = "./Train"
        categories = os.listdir(Trian_dir)
        print(categories)
        nb_classes = len(categories)

        image_w = 64
        image_h = 64

        pixels = image_h * image_w * 3

        X = []
        filenames = []
        files = glob.glob(caltech_dir + "/*.*")

        for i, f in enumerate(files):
            img = Image.open(f)
            img = img.convert("RGB")
            img = img.resize((image_w, image_h))
            data = np.asarray(img)
            filenames.append(f)
            X.append(data)

        X = np.array(X)
        model = load_model('./model/CNN.h5')

        prediction = []
        prediction = model.predict(X)

        np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
        cnt = 0

        # 이 비교는 그냥 파일들이 있으면 해당 파일과 비교. 카테고리와 함께 비교해서 진행하는 것은 _4 파일.
        name_list = []
        name_count = 0
        pre_ans_str = []
        for i in prediction:
            pre_ans = i.argmax()  # 예측 레이블
            print(i)
            print(pre_ans)

            for j in range(nb_classes):

                if pre_ans == j:
                    pre_ans_str.append(categories[j])
                    print(categories[j])

        c = Counter(pre_ans_str)
        mode = c.most_common(1)
        self.name = mode[0][0]
        cnt += 1

        if (self.text == self.name):
            reply = QMessageBox.question(self, 'Message', '확인되었습니다(Yes: 로그인, NO: 종료).')
            if reply == QMessageBox.Yes:
                self.naver_login()
            else:
                self.exit()
        else:
            reply = QMessageBox.question(self, 'Message', '로그인 실패, 처음으로 돌아갑니다.')
            if reply == QMessageBox.Yes:
                self.exit()
            else:
                self.exit()

    def naver_login(self):
        con = sqlite3.connect('test.db')
        cur = con.cursor()
        cur.execute("select id from log where name=?;", (self.name,))
        data = cur.fetchone()
        id = data[0]

        cur = con.cursor()
        cur.execute("select pw from log where name=?", (self.name,))
        data = cur.fetchone()
        pw = data[0]
        pw = AES.cipherinstance.decrypt(pw)
        con.commit()
        con.close()
        driver = webdriver.Chrome(r'chromedriver.exe')
        driver.implicitly_wait(3)

        driver.get('https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com')
        pyperclip.copy(id)
        driver.find_element_by_xpath('//*[@id="id"]').click()
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        time.sleep(1)
        pyperclip.copy(pw)
        driver.find_element_by_xpath('//*[@id="pw"]').click()
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()


    # def stop(self):
    #     Login_Window.count = 0
    #     self.frame.setPixmap(QPixmap.fromImage(QImage()))
    #     self.timer.stop()
    #     self.who.setText("")
    #     self.show()
    def onOKButtonClicked(self):
        self.accept()

    def onCancelButtonClicked(self):
        self.reject()

    def showModal(self):
        return super().exec_()