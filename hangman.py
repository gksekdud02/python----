import os
import sys
import random
import json

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QLabel
from PyQt5 import uic
from PyQt5.QtGui import QPixmap

def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_path, relative_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Resource file not found: {full_path}")
    return full_path

# UI 파일 로드
form_1 = resource_path('start.ui')
form_class_1 = uic.loadUiType(form_1)[0]
form_2 = resource_path('hangman.ui')
form_class_2 = uic.loadUiType(form_2)[0]

image_folder = resource_path("image")

# 단어 파일 로드
def load_words():
    words_file = resource_path("words.json")
    with open(words_file, "r") as file:
        return json.load(file)

class MainApp(QMainWindow, form_class_1):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("행맨 게임")  # 창 이름 설정

        self.startBtn.clicked.connect(self.game_start) # 게임시작버튼을 누를 때 함수연결
        
    def game_start(self):
        self.hide()
        page1 = gamePage(self)
        page1.show()

class gamePage(QMainWindow, form_class_2):
    def __init__(self, parent):
        super().__init__(parent)

        self.setupUi(self)
        self.setWindowTitle("행맨 게임")
        self.life = 7  # 최대생명

        for char in "abcdefghijklmnopqrstuvwxyz":  # 알파벳 a-z 반복
            btn = getattr(self, f"btn_{char}")  
            if isinstance(btn, QPushButton):  # 버튼인지 확인
                btn.clicked.connect(self.guess)  # 각 버튼을 함수에 연결

        words = load_words()
        self.category = random.choice(list(words.keys())) # 카테고리 랜덤 선택
        self.word = random.choice(words[self.category]) # 카테고리안의 단어 랜덤 선택
        self.hidden_word = ['_ '] * len(self.word) # 단어 수만큼 _ 추가

        self.hintlabel.setText(self.category)
        self.answerlabel.setText(" ".join(self.hidden_word))

        self.used_char = []
        self.uselabel.setText("")

        self.answer_list = []
        for i in self.word:
            self.answer_list.append(i)

    def guess(self):
        sender = self.sender()  # 버튼 객체 가져오기
        btn_name = sender.text().lower()  # 버튼 이름 가져오기
        sender.setEnabled(False)  # 버튼을 비활성화

        self.used_char.append(btn_name)
        self.uselabel.setText(" ".join(self.used_char))
        print(self.word)

        if btn_name in self.word:  # 정답에 포함된 문자라면
            for idx, char in enumerate(self.word):
                if char == btn_name:
                    self.hidden_word[idx] = char  # 맞춘 위치에 문자 업데이트
            self.answerlabel.setText(" ".join(self.hidden_word))  # 갱신된 단어 표시
        else:
            self.life -= 1  # 틀리면 생명 1 차감

        self.image_show()  # 이미지 업데이트

        if "_ " not in self.hidden_word: # 단어를 다 맞추면
            self.image_show("win")
            winmessage = QMessageBox()
            winmessage.setWindowTitle("승리")
            winmessage.setText("승리했습니다.")
            winmessage.finished.connect(self.restart_game)
            winmessage.exec_()
        elif self.life <= 0: # 생명이 다 차감되면
            self.image_show("lose")
            losemessage = QMessageBox()
            losemessage.setWindowTitle("패배")
            losemessage.setText(f"패배했습니다. 단어는 {self.word}였습니다.")
            losemessage.finished.connect(self.restart_game)
            losemessage.exec_()

    def image_show(self, result=None):
        if result == "win":  # 승리했을 때
            image_path = os.path.join(image_folder, "image9.png")
        elif result == "lose":  # 패배했을 때
            image_path = os.path.join(image_folder, "image10.png")
        else:  # 남은 생명에 따라 이미지 변경 (life는 7에서 시작하여 0까지 감소)
            image_path = os.path.join(image_folder, f"image{8 - self.life}.png")

        pixmap = QPixmap(image_path)

        if pixmap.isNull():  # 이미지가 로드되지 않으면
            print(f"Image {image_path} not found.")  # 어떤 이미지가 로드되지 않았는지 출력
        else:
            self.imagelabel.setPixmap(pixmap)  # QPixmap을 QLabel에 설정
            self.imagelabel.setScaledContents(True)  # QLabel 크기에 맞게 이미지 크기 조정

    def restart_game(self):
        self.close()  # 현재 게임 화면을 닫고
        parent = self.parent()  # 부모 창 (MainApp)을 가져옴
        parent.show()  # 부모 창 (MainApp)을 보이게 함
        self.deleteLater()  # 현재 게임 화면을 메모리에서 제거


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
