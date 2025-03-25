import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextBrowser, QPushButton
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QFont
from PyQt6.QtCore import Qt, QTimer

# Datei mit der Story laden
STORY_FILE = "story.txt"

class RPGGame(QWidget):
    def __init__(self):
        super().__init__()

        # Fenster-Einstellungen
        self.setWindowTitle("Apokalyptisches RPG")
        self.setGeometry(200, 200, 800, 600)

        # Layout für die UI
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Hintergrund mit altem Papier-Design setzen
        self.set_background("assets/old_paper_bg.png")

        # Story-Textbox mit besserer Lesbarkeit
        self.story_text = QTextBrowser(self)
        self.story_text.setFont(QFont("Times New Roman", 16, QFont.Weight.Bold))  # Größere, fettere Schrift
        self.story_text.setStyleSheet("""
            background: rgba(255, 255, 255, 0.5);  /* Leicht transparenter Hintergrund */
            border: 2px solid #8b5a2b;
            color: #3D1C00;  /* Dunkelbraun für besseren Kontrast */
            padding: 15px;
            border-radius: 10px;
        """)
        self.layout.addWidget(self.story_text)

        # Container für Buttons
        self.button_container = QVBoxLayout()
        self.layout.addLayout(self.button_container)

        # Story starten
        self.story_data = self.load_story(STORY_FILE)
        self.current_section = "Start"
        self.display_story()

    def set_background(self, image_path):
        """Setzt das Hintergrundbild für die gesamte UI"""
        palette = QPalette()
        pixmap = QPixmap(image_path)
        palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
        self.setPalette(palette)

    def load_story(self, filename):
        """Lädt die Story aus einer Datei und speichert sie als Dictionary"""
        story = {}
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()

        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith("#"):  # Abschnittstitel
                current_section = line[1:]
                story[current_section] = {"text": "", "choices": []}
            elif line and current_section:
                if "->" in line:  # Entscheidung
                    choice_text, next_section = map(str.strip, line.split("->"))
                    story[current_section]["choices"].append((choice_text, next_section))
                else:
                    story[current_section]["text"] += line + "\n"

        return story

    def display_story(self):
        """Sanfte Überblendung & Anzeige des Story-Abschnitts"""
        section = self.story_data.get(self.current_section, {"text": "Fehler: Abschnitt nicht gefunden", "choices": []})
        
        # Sanfte Überblendung (Text ausblenden, dann wieder einblenden)
        self.story_text.setStyleSheet("opacity: 0;")  
        QTimer.singleShot(200, lambda: self.story_text.setText(section["text"]))
        QTimer.singleShot(300, lambda: self.story_text.setStyleSheet("""
            background: rgba(255, 255, 255, 0.5);
            border: 2px solid #8b5a2b;
            color: #3D1C00;
            padding: 15px;
            border-radius: 10px;
            opacity: 1;
        """))

        # Alte Buttons entfernen
        for i in reversed(range(self.button_container.count())):
            self.button_container.itemAt(i).widget().deleteLater()

        # Neue Buttons generieren
        for choice_text, next_section in section["choices"]:
            btn = QPushButton(choice_text)
            btn.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))  # Größere Schrift für bessere Lesbarkeit
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #d2a679; /* Helleres Braun für bessere Sichtbarkeit */
                    border: 3px solid #8b5a2b;
                    color: black;
                    padding: 12px;
                    border-radius: 5px;
                    margin-bottom: 5px;
                }
                QPushButton:hover {
                    background-color: #b8875b; /* Kräftigeres Braun für Hover */
                    border: 3px solid #654321;
                    padding: 14px; /* Simuliert ein leichtes „Wachsen“ */
                }
            """)
            btn.clicked.connect(lambda _, s=next_section: self.update_story(s))
            self.button_container.addWidget(btn)

    def update_story(self, next_section):
        """Wechselt zum nächsten Story-Abschnitt mit sanftem Übergang"""
        self.current_section = next_section
        self.display_story()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = RPGGame()
    game.show()
    sys.exit(app.exec())
