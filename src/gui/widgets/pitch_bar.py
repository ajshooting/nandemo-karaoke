from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt

class PitchBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pitch_value = 0  # 現在の音程値 (例: MIDIノート番号)
        self.target_pitch = 0 # 目標音程

    def set_pitch(self, pitch):
        self.pitch_value = pitch
        self.update() # 再描画

    def set_target_pitch(self, target_pitch):
        self.target_pitch = target_pitch
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 背景の描画 (必要に応じて)
        painter.fillRect(self.rect(), QColor(240, 240, 240))

        # 目標音程バーの描画 (例: 緑色)
        pen = QPen(QColor(0, 200, 0), 3)
        painter.setPen(pen)
        center_y = self.height() // 2
        target_y = center_y - self.target_pitch * 5  # 音程値に応じて位置を調整 (調整が必要)
        painter.drawLine(0, target_y, self.width(), target_y)

        # 現在の音程バーの描画 (例: 青色)
        pen = QPen(QColor(0, 0, 200), 5)
        painter.setPen(pen)
        current_y = center_y - self.pitch_value * 5 # 音程値に応じて位置を調整 (調整が必要)
        painter.drawLine(0, current_y, self.width(), current_y)

        # 必要に応じて、目盛りやラベルなどを描画