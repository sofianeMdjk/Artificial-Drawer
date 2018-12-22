from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow
import cv2
import drawer.utils as utils
import numpy as np

class Ui_Form(QMainWindow):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowTitle("Artificial drawer")
        Form.resize(1056, 723)
        self.horizontalLayoutWidget = QtWidgets.QWidget(Form)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 1061, 631))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.first_vide_label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.first_vide_label.setText("")
        self.first_vide_label.setObjectName("first_vide_label")
        self.horizontalLayout.addWidget(self.first_vide_label)
        self.second_video_label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.second_video_label.setText("")
        self.second_video_label.setObjectName("second_video_label")
        self.horizontalLayout.addWidget(self.second_video_label)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(Form)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(30, 650, 971, 51))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.remove_eraser_btn = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.remove_eraser_btn.setText("Remove eraser")
        self.remove_eraser_btn.setObjectName("remove_eraser_btn")
        self.remove_eraser_btn.clicked.connect(self.remove_eraser)
        self.horizontalLayout_2.addWidget(self.remove_eraser_btn)
        self.eraser_color_btn = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.eraser_color_btn.setText("Pick eraser color")
        self.eraser_color_btn.setObjectName("eraser_color_btn")
        self.horizontalLayout_2.addWidget(self.eraser_color_btn)
        self.color_chooser_btn = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.color_chooser_btn.setText("Pick colors")
        self.color_chooser_btn.setObjectName("color_chooser_btn")
        self.horizontalLayout_2.addWidget(self.color_chooser_btn)
        self.start_btn = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.start_btn.setText("Start drawing")
        self.start_btn.setObjectName("start_btn")
        self.horizontalLayout_2.addWidget(self.start_btn)
        self.clean_btn = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.clean_btn.setText("Clean board")
        self.clean_btn.clicked.connect(self.clean_board)
        self.clean_btn.setObjectName("clean_btn")
        self.horizontalLayout_2.addWidget(self.clean_btn)
        QtCore.QMetaObject.connectSlotsByName(Form)
        self.frame_width = 650
        self.frame_height = 750
        self.central1_width = int(self.frame_width / 2 - 45); self.central1_height = int(self.frame_height / 2)
        self.central2_width = int(self.frame_width / 2 + 45); self.central2_height = int(self.frame_height / 2)
        self.central_width = int(self.frame_width / 2); self.central_height = int(self.frame_height / 2)
        self.lower1 = None; self.upper1 = None
        self.lower2 = None; self.upper2 = None
        self.lower_eraser = None; self.upper_eraser = None
        '''Drawer cam timer'''
        self.timer = QTimer()
        self.timer.timeout.connect(self.choose_cam)
        self.start_btn.clicked.connect(self.controlTimer)
        '''Color picker timer'''
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.view_color_cam)
        self.color_chooser_btn.clicked.connect(self.control_color_timer)
        '''Eraser color picker timer'''
        self.color_eraser_timer = QTimer()
        self.color_eraser_timer.timeout.connect(self.view_eraser_color_cam)
        self.eraser_color_btn.clicked.connect(self.control_eraser_color_timer)
        self.black_board_frame = utils.init_black_board()
        self.cap = None
        self.hsv = None
        self.erase_mode = False

    def choose_cam(self):
        if self.upper1 is None or self.upper2 is None :
            self.control_color_timer()
        else:
            if self.upper_eraser == None:
                self.viewCam()
            else:
                self.view_erase_cam()

    def view_erase_cam(self):
        lower = {"color1": self.lower1, "color2": self.lower2, "eraser": self.lower_eraser}
        upper = {"color1": self.upper1, "color2": self.upper2, "eraser": self.upper_eraser}
        (grabbed, frame) = self.cap.read()
        frame = self.format_frame(frame)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        self.hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        colors_collision = []
        for key, value in upper.items():
            cnts = self.generate_contours(lower=lower[key], upper=upper[key])
            if len(cnts) > 1:
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                if key == "eraser":
                    self.erase_mode = True
                    print("Yeah here")
                else:
                    colors_collision.append((x, y))

            # detecting collision
            if len(colors_collision) == 2: #If we have two colors that can colid
                x1, y1 = colors_collision.pop(0)
                x2, y2 = colors_collision.pop(0)

                if utils.color_colision(x1, y1, x2, y2, colision_distance=120):
                    print("yes collision here")
                    drawing_width = int(x1 + x2 / 2)
                    drawing_height = int(y1 + y2 / 2)
                    print(self.erase_mode)
                    if self.erase_mode:
                        utils.erase_shape(drawing_width, drawing_height, frame=self.black_board_frame)
                        print("YES ERASING")
                    else:
                        utils.draw_shape(drawing_width, drawing_height, frame=self.black_board_frame)
                    '''clearing the colors collision for the upcoming collision'''
                    colors_collision.clear()

            self.draw_frame_label(frame, label_id=1)
            self.draw_frame_label(self.black_board_frame, label_id=2)

    def viewCam(self):
        lower = {"color1": self.lower1, "color2": self.lower2}
        upper = {"color1": self.upper1, "color2": self.upper2}
        (grabbed, frame) = self.cap.read()
        frame = self.format_frame(frame)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        self.hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        colors_collision = []

        for key, value in upper.items():
            cnts = self.generate_contours(lower=lower[key], upper=upper[key])
            if len(cnts) > 1:
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                cv2.circle(frame, (int(x), int(y)), int(radius), (255, 255, 255), 4)
                colors_collision.append((x, y))

            # detecting collision
            if len(colors_collision) == 2:  # If we have two colors that can colid
                x1, y1 = colors_collision.pop(0)
                x2, y2 = colors_collision.pop(0)

                if utils.color_colision(x1, y1, x2, y2, colision_distance=120):
                    print("yes collision here")
                    drawing_width = int(x1 + x2 / 2)
                    drawing_height = int(y1 + y2 / 2)
                    utils.draw_shape(drawing_width, drawing_height, frame=self.black_board_frame)
                    '''clearing the colors collision for the upcoming collision'''
                    colors_collision.clear()

            self.draw_frame_label(frame, label_id=1)
            self.draw_frame_label(self.black_board_frame, label_id=2)

    def controlTimer(self):
        if not self.timer.isActive():
            self.stop_other_timers()
            self.cap = cv2.VideoCapture(0)
            self.timer.start(20)
            self.start_btn.setText("Stop Drawing")
        else:
            self.timer.stop()
            self.cap.release()
            self.start_btn.setText("Start Drawing")
            self.color_chooser_btn.setText("Pick colors")
            self.eraser_color_btn.setText("Pick eraser color")

    def view_color_cam(self):
        ret, frame = self.cap.read()
        frame = self.format_frame(frame)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        self.hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        cv2.circle(frame, (self.central1_width, self.central1_height), radius=40, color=(0, 255, 0), thickness=6)
        cv2.circle(frame, (self.central2_width, self.central2_height), radius=40, color=(0, 255, 0), thickness=6)
        '''Getting image info to add it to our label, needed informations are, width, height and step'''
        self.draw_frame_label(frame, label_id=1)
        self.second_video_label.clear()

    def control_color_timer(self):
        '''When clicking on the button if timer is not active start capturing image and each 20 ms a callback signal is sent'''
        if not self.color_timer.isActive():
            self.stop_other_timers()
            self.cap = cv2.VideoCapture(0)
            self.color_timer.start(20)
            self.color_chooser_btn.setText("Validate colors")

        else:
            '''When clicking on the same button we retrieve the colors inside our circles and stop the cam'''
            self.lower1, self.upper1 = utils.get_hsv_range(self.hsv[self.central1_height,self.central1_width])
            self.lower2, self.upper2 = utils.get_hsv_range(self.hsv[self.central2_height,self.central2_width])
            print(self.lower1,self.upper1)
            print(self.lower2,self.upper2)
            self.color_timer.stop()
            self.cap.release()
            self.color_chooser_btn.setText("Pick colors")
            self.start_btn.setText("Start Drawing")
            self.color_chooser_btn.setText("Pick colors")
            self.eraser_color_btn.setText("Pick eraser color")

    def view_eraser_color_cam(self):
        ret, frame = self.cap.read()
        frame = self.format_frame(frame)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        self.hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        cv2.circle(frame, (self.central_width, self.central_height), radius=40, color=(0, 255, 0), thickness=8)
        '''Getting image info to add it to our label, needed informations are, width, height and step'''
        self.draw_frame_label(frame, label_id=1)
        self.second_video_label.clear()

    def control_eraser_color_timer(self):
        '''When clicking on the button if timer is not active start capturing image and each 20 ms a callback signal is sent'''
        if not self.color_eraser_timer.isActive():
            self.stop_other_timers()
            self.cap = cv2.VideoCapture(0)
            self.color_eraser_timer.start(20)
            self.eraser_color_btn.setText("Validate color")
        else:
            '''When clicking on the same button we retrieve the color inside our circle and stop the cam'''
            self.lower_eraser, self.upper_eraser = utils.get_hsv_range(self.hsv[self.central_height,self.central_width])
            self.color_eraser_timer.stop()
            self.cap.release()
            self.eraser_color_btn.setText("Pick eraser color")

    def remove_eraser(self):
        self.erase_mode = False
        self.upper_eraser = None
        self.lower_eraser = None

    def clean_board(self):
        self.black_board_frame = utils.init_black_board()

    def stop_other_timers(self):
        if self.color_timer.isActive():
            self.color_timer.stop()
        if self.color_eraser_timer.isActive():
            self.color_eraser_timer.stop()
        if self.timer.isActive():
            self.timer.stop()
        if self.cap is not None:
            self.cap.release()

    def draw_frame_label(self, frame, label_id=1):
        height, width, channel = frame.shape
        step = channel * width
        qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
        if label_id == 1:
            self.first_vide_label.setPixmap(QPixmap.fromImage(qImg))
        else:
            self.second_video_label.setPixmap(QPixmap.fromImage(qImg))
    
    def format_frame(self, frame):
        self.frame_width = 650
        self.frame_height = 750
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        frame = cv2.flip(frame, 1)
        return frame

    def generate_contours(self, lower, upper):
        kernel = np.ones((9, 9), np.uint8)
        mask = cv2.inRange(self.hsv, lower, upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        return cnts

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

