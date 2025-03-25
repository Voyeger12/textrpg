import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton,
    QSlider, QDialog, QLabel, QRadioButton, QButtonGroup, QMessageBox
)
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QFont
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

STORY_FILE = "story.txt"
MUSIC_FILE = "assets/Tanz der Ruinen.mp3"
CLICK_SOUND_FILE = "assets/mouse-click.mp3"
BACKGROUND_IMAGE = "assets/paper_bg.png"

class RPGGame(QWidget):
    def __init__(self):
        super().__init__()
        self.init_game()

    def init_game(self):
        self.setWindowTitle("Apokalyptisches RPG")
        self.setGeometry(200, 200, 900, 700)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.set_background(BACKGROUND_IMAGE)
        self.text_speed = 30

        self.title_label = QLabel("Apokalyptisches Abenteuer")
        self.title_label.setFont(QFont("Old English Text MT", 24, QFont.Weight.Bold))
        self.title_label.setStyleSheet("""
            color: #5c3b1e;
            background-color: rgba(255, 255, 255, 0.6);
            border-radius: 10px;
            padding: 10px;
            text-align: center;
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.story_text = QTextBrowser(self)
        self.story_text.setFont(QFont("Palatino Linotype", 16, QFont.Weight.Normal))
        self.story_text.setStyleSheet("""
            background: rgba(255, 255, 255, 0.7);
            border: 3px solid #8b5a2b;
            color: #3D1C00;
            padding: 20px;
            border-radius: 15px;
            selection-background-color: #d2a679;
        """)
        self.layout.addWidget(self.story_text)

        top_bar = QHBoxLayout()

        restart_btn = QPushButton("\U0001F504 Neu starten")
        restart_btn.clicked.connect(self.restart_game)
        restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #a0522d;
                border: 2px solid #5c3b1e;
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8b4513;
            }
        """)
        top_bar.addWidget(restart_btn)

        top_bar.addStretch()

        settings_btn = QPushButton("\u2699 Einstellungen")
        settings_btn.clicked.connect(self.open_settings)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #c7a17a;
                border: 2px solid #5c3b1e;
                border-radius: 8px;
                padding: 8px 12px;
                color: black;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b18c6e;
            }
        """)
        top_bar.addWidget(settings_btn)
        self.layout.addLayout(top_bar)

        self.setup_audio()

        self.button_container = QVBoxLayout()
        self.layout.addLayout(self.button_container)

        self.load_game_data()

    def toggle_mute(self):
        if self.audio_output.volume() > 0:
            self.last_volume = self.audio_output.volume()
            self.audio_output.setVolume(0)
        else:
            self.audio_output.setVolume(self.last_volume)

    def open_settings(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("\u2699 Einstellungen")
        dlg.setFixedSize(360, 300)
        dlg.setStyleSheet("""
            QDialog {
                background-color: rgba(255, 248, 230, 0.95);
                border: 2px solid #8b5a2b;
                border-radius: 15px;
            }
            QLabel {
                font-family: 'Palatino Linotype';
                font-size: 15px;
                font-weight: bold;
                color: #3D1C00;
                padding-top: 8px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                height: 8px;
                background: #d2a679;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #5c3b1e;
                border: 1px solid #3D1C00;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QPushButton {
                background-color: #c7a17a;
                border: 2px solid #5c3b1e;
                border-radius: 6px;
                padding: 6px;
                color: black;
            }
            QPushButton:hover {
                background-color: #b18c6e;
            }
            QRadioButton {
                font-family: 'Palatino Linotype';
                font-size: 14px;
                color: #3D1C00;
            }
        """)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("\U0001F3B5 Musiklautstärke"))
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(int(self.audio_output.volume() * 100))
        volume_slider.valueChanged.connect(lambda val: self.audio_output.setVolume(val / 100))
        layout.addWidget(volume_slider)

        mute_btn = QPushButton("\U0001F507 Mute / Unmute")
        mute_btn.clicked.connect(self.toggle_mute)
        layout.addWidget(mute_btn)

        layout.addWidget(QLabel("\u23F3 Textgeschwindigkeit"))
        speed_group = QButtonGroup(dlg)
        slow = QRadioButton("\U0001F422 Langsam")
        normal = QRadioButton("\U0001F6B6 Normal")
        fast = QRadioButton("\U0001F407 Schnell")
        layout.addWidget(slow)
        layout.addWidget(normal)
        layout.addWidget(fast)

        speed_group.addButton(slow)
        speed_group.addButton(normal)
        speed_group.addButton(fast)

        if self.text_speed <= 10:
            fast.setChecked(True)
        elif self.text_speed >= 50:
            slow.setChecked(True)
        else:
            normal.setChecked(True)

        def update_speed():
            if slow.isChecked():
                self.text_speed = 60
            elif normal.isChecked():
                self.text_speed = 30
            elif fast.isChecked():
                self.text_speed = 10

        speed_group.buttonClicked.connect(update_speed)

        dlg.setLayout(layout)
        dlg.exec()

    def load_game_data(self):
        self.story_data = self.load_story(STORY_FILE)
        self.current_section = "Start"
        self.display_story()

    def restart_game(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("\U0001F504 Spiel neu starten?")
        msg.setText("Willst du wirklich dein Abenteuer von vorne beginnen?")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: rgba(255, 248, 230, 0.95);
                font-family: 'Palatino Linotype';
                font-size: 14px;
            }
            QPushButton {
                background-color: #a0522d;
                border: 2px solid #5c3b1e;
                border-radius: 6px;
                padding: 6px 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #8b4513;
            }
        """)
        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self, 'timer'):
                self.timer.stop()
            self.load_game_data()

    def setup_audio(self):
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.0)
        self.music_player = QMediaPlayer()
        self.music_player.setAudioOutput(self.audio_output)
        self.music_player.setSource(QUrl.fromLocalFile(MUSIC_FILE))
        self.music_player.setLoops(QMediaPlayer.Loops.Infinite)
        self.music_player.play()
        self.fade_in_volume(0, 0.5, 2000)

        self.click_output = QAudioOutput()
        self.click_player = QMediaPlayer()
        self.click_player.setAudioOutput(self.click_output)
        self.click_player.setSource(QUrl.fromLocalFile(CLICK_SOUND_FILE))

    def set_background(self, image_path):
        palette = QPalette()
        pixmap = QPixmap(image_path)
        palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
        self.setPalette(palette)

    def load_story(self, filename):
        story = {}
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()

        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                current_section = line[1:]
                story[current_section] = {"text": "", "choices": []}
            elif line and current_section:
                if "->" in line:
                    choice_text, next_section = map(str.strip, line.split("->"))
                    story[current_section]["choices"].append((choice_text, next_section))
                else:
                    story[current_section]["text"] += line + "\n"

        return story

    def display_story(self):
        section = self.story_data.get(self.current_section, {"text": "Fehler", "choices": []})
        full_text = section["text"]
        self.animate_text(full_text)

        for i in reversed(range(self.button_container.count())):
            self.button_container.itemAt(i).widget().deleteLater()

        is_end_section = self.current_section.lower() in ['ende', 'tod']

        for choice_text, next_section in section["choices"]:
            btn = QPushButton(choice_text)
            btn.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #d2a679;
                    border: 3px solid #8b5a2b;
                    color: black;
                    padding: 12px;
                    border-radius: 10px;
                    margin-bottom: 5px;
                }
                QPushButton:hover {
                    background-color: #b8875b;
                    border: 3px solid #654321;
                    padding: 14px;
                }
            """)
            btn.clicked.connect(lambda _, s=next_section: self.handle_button_click(s))
            self.button_container.addWidget(btn)

        if is_end_section:
            restart_btn = QPushButton("\U0001F504 Spiel neu starten")
            restart_btn.setStyleSheet("""
                QPushButton {
                    background-color: #a0522d;
                    border: 3px solid #5c3b1e;
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    margin-top: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #8b4513;
                }
            """)
            restart_btn.clicked.connect(self.restart_game)
            self.button_container.addWidget(restart_btn)

    def handle_button_click(self, next_section):
        self.click_player.stop()
        self.click_player.play()
        self.update_story(next_section)

    def update_story(self, next_section):
        self.current_section = next_section
        self.display_story()

    def animate_text(self, text):
        self.story_text.clear()
        self.displayed_text = ""
        self.text_index = 0
        self.full_text = text
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_text_animation)
        self.timer.start(self.text_speed)

    def update_text_animation(self):
        if self.text_index < len(self.full_text):
            self.displayed_text += self.full_text[self.text_index]
            self.story_text.setPlainText(self.displayed_text)
            self.text_index += 1
        else:
            self.timer.stop()

    def fade_in_volume(self, start, end, duration_ms):
        steps = 20
        interval = duration_ms // steps
        delta = (end - start) / steps
        self.current_volume = start

        def increase():
            self.current_volume += delta
            self.audio_output.setVolume(min(self.current_volume, end))

        for i in range(1, steps + 1):
            QTimer.singleShot(i * interval, increase)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = RPGGame()
    game.show()
    sys.exit(app.exec())
