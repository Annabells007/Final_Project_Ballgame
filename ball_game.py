import random
import maya.cmds as cmds

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance

import maya.OpenMayaUI as omui

IMAGE_PATH = r"C:/Users/NB Win11/Documents/maya/2024/scripts/ballGame/images"


class BallCatcherGame(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(BallCatcherGame, self).__init__(parent)

        self.spheres = {}
        self.correct_score = 0
        self.wrong_score = 0
        self.time_left = 30
        self.selection_job = None

        self.spawn_timer = QtCore.QTimer()
        self.spawn_timer.timeout.connect(self.spawn_spheres)

        self.game_timer = QtCore.QTimer()
        self.game_timer.timeout.connect(self.update_timer)

        self.setWindowTitle("🎯 PB - Ball Catcher Game (Image Ver.)")
        self.resize(420, 360)

        main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(main_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f9e7bb, stop:1 #f5b87e);
                font-family: 'Comic Sans MS';
                font-size: 14px;
                color: #333;
            }
            QMessageBox {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f9e7bb, stop:1 #f5b87e);
                font-family: 'Comic Sans MS';
                font-size: 14px;
                color: #333;
            QLabel {
                color: #222;
                font-weight: bold;
            }
            QPushButton {
                border-radius: 8px;
                font-weight: bold;
                color: white;
                padding: 6px 10px;
            }
            QPushButton#newBtn {
                background-color: #4CAF50;
            }
            QPushButton#quitBtn {
                background-color: #E74C3C;
            }
        """)

        self.display = QtWidgets.QLabel()
        field_pix = QtGui.QPixmap(f"{IMAGE_PATH}/field_bg.png")
        self.display.setPixmap(field_pix.scaled(420, 200, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.display.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.display)

        score_layout = QtWidgets.QGridLayout()
        main_layout.addLayout(score_layout)

        correct_icon = QtWidgets.QLabel()
        correct_icon.setPixmap(QtGui.QPixmap(f"{IMAGE_PATH}/correct_icon.png").scaled(400, 40, QtCore.Qt.KeepAspectRatio))
        self.correct_value = QtWidgets.QLabel("0")
        self.correct_value.setStyleSheet("font-weight: bold; font-size: 18px; color: #2ecc71;")

        wrong_icon = QtWidgets.QLabel()
        wrong_icon.setPixmap(QtGui.QPixmap(f"{IMAGE_PATH}/wrong_icon.png").scaled(400, 40, QtCore.Qt.KeepAspectRatio))
        self.wrong_value = QtWidgets.QLabel("0")
        self.wrong_value.setStyleSheet("font-weight: bold; font-size: 18px; color: #e74c3c;")

        time_icon = QtWidgets.QLabel()
        time_icon.setPixmap(QtGui.QPixmap(f"{IMAGE_PATH}/time_icon.png").scaled(400, 40, QtCore.Qt.KeepAspectRatio))
        self.time_value = QtWidgets.QLabel(str(self.time_left))
        self.time_value.setStyleSheet("font-weight: bold; font-size: 18px; color: #34495e;")

        score_layout.addWidget(correct_icon, 0, 0)
        score_layout.addWidget(self.correct_value, 0, 1)
        score_layout.addWidget(wrong_icon, 1, 0)
        score_layout.addWidget(self.wrong_value, 1, 1)
        score_layout.addWidget(time_icon, 2, 0)
        score_layout.addWidget(self.time_value, 2, 1)

        btn_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(btn_layout)

        self.new_btn = QtWidgets.QPushButton()
        self.new_btn.setIcon(QtGui.QIcon(f"{IMAGE_PATH}/newgame_btn.png"))
        self.new_btn.setIconSize(QtCore.QSize(200, 65))
        self.new_btn.setStyleSheet("border:none;")
        self.new_btn.clicked.connect(self.new_game)
        btn_layout.addWidget(self.new_btn)

        self.quit_btn = QtWidgets.QPushButton()
        self.quit_btn.setIcon(QtGui.QIcon(f"{IMAGE_PATH}/quit_btn.png"))
        self.quit_btn.setIconSize(QtCore.QSize(200, 65))
        self.quit_btn.setStyleSheet("border:none;")
        self.quit_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.quit_btn)

    def new_game(self):
        self.cleanup()
        self.correct_score = 0
        self.wrong_score = 0
        self.time_left = 30
        self.update_ui()

        self.spawn_timer.start(2000)
        self.game_timer.start(1000)
        self.selection_job = cmds.scriptJob(e=["SelectionChanged", self.check_selection], protected=True)

    def spawn_spheres(self):
        count = random.randint(1, 4)
        colors = {"green": (0, 1, 0), "red": (1, 0, 0)}

        for _ in range(count):
            name_id = len(self.spheres) + 1
            color_name, rgb = random.choice(list(colors.items()))
            name = f"ball_{name_id:02d}_{color_name}"

            if cmds.objExists(name):
                continue

            sphere = cmds.polySphere(name=name, r=0.5)[0]
            cmds.move(random.uniform(-5, 5), random.uniform(0.5, 5), random.uniform(-5, 5), sphere)

            shader = cmds.shadingNode("lambert", asShader=True, name=f"{name}_mat")
            cmds.setAttr(shader + ".color", rgb[0], rgb[1], rgb[2], type="double3")
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{shader}SG")
            cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader")
            cmds.sets(sphere, e=True, forceElement=sg)

            self.spheres[sphere] = {"life": 3, "color": color_name}

    def check_selection(self):
        sel = cmds.ls(sl=True)
        if not sel:
            return

        obj = sel[0]
        if obj not in self.spheres:
            return

        color = self.spheres[obj]["color"]
        if color == "green":
            self.correct_score += 1
        elif color == "red":
            self.wrong_score += 1

        cmds.delete(obj)
        del self.spheres[obj]
        self.update_ui()

    def update_timer(self):
        self.time_left -= 1

        expired = []
        for s in list(self.spheres.keys()):
            self.spheres[s]["life"] -= 1
            if self.spheres[s]["life"] <= 0:
                expired.append(s)

        for s in expired:
            if cmds.objExists(s):
                color = self.spheres[s]["color"]
                if color == "green":
                    self.wrong_score += 1
                cmds.delete(s)
            del self.spheres[s]

        if self.time_left <= 0:
            self.end_game()

        self.update_ui()

    def update_ui(self):
        self.correct_value.setText(str(self.correct_score))
        self.wrong_value.setText(str(self.wrong_score))
        self.time_value.setText(str(self.time_left))

    def end_game(self):
        self.spawn_timer.stop()
        self.game_timer.stop()
        if self.selection_job:
            try:
                cmds.scriptJob(kill=self.selection_job, force=True)
            except:
                pass

        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("⏰ Game Over")

        custom_widget = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(custom_widget)
        vbox.setAlignment(QtCore.Qt.AlignCenter)

        timeup_label = QtWidgets.QLabel()
        timeup_label.setAlignment(QtCore.Qt.AlignCenter)
        pix = QtGui.QPixmap(f"{IMAGE_PATH}/timeup_icon.png")
        scaled_pix = pix.scaled(180, 180, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        timeup_label.setPixmap(scaled_pix)
        vbox.addWidget(timeup_label)

        score_label = QtWidgets.QLabel(f"✅ Correct: {self.correct_score}\n❌ Wrong: {self.wrong_score}")
        score_label.setAlignment(QtCore.Qt.AlignCenter)
        score_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        vbox.addWidget(score_label)

        layout = msg.layout()
        layout.addWidget(custom_widget, 0, 0, 1, layout.columnCount())

        msg.exec_()

    def cleanup(self):
        for s in list(self.spheres.keys()):
            if cmds.objExists(s):
                cmds.delete(s)
        self.spheres = {}
        if self.selection_job:
            try:
                cmds.scriptJob(kill=self.selection_job, force=True)
            except:
                pass
            self.selection_job = None

    def closeEvent(self, event):
        self.cleanup()
        event.accept()

def run_game():
    global ball_game_ui
    try:
        ball_game_ui.close()
    except:
        pass

    ptr = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
    ball_game_ui = BallCatcherGame(parent=ptr)
    ball_game_ui.show()


run_game()
