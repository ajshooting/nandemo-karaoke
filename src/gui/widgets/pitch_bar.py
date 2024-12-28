from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QFont
from PyQt6.QtCore import Qt, QRectF
import librosa


class PitchBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pitch_data = []  # 解析されたピッチデータを保持するリスト
        self.current_position = 0  # 現在の再生位置（秒）
        self.note_range = (36, 84)  # 表示するMIDIノートの範囲 (C2からB6)
        self.note_height = 4  # 各ノートの高さ
        self.position_line_x = 100  # 現在の再生位置を示す線のX座標
        self.scroll_offset = 0  # スクロールオフセット

    def set_pitch_data(self, pitch_data):
        self.pitch_data = pitch_data
        self.update()

    def update_position(self, current_time):
        self.current_position = current_time
        self.scroll_offset = max(
            0,
            (self.current_position - 2) * 50,  # 1秒あたり50ピクセルのスクロールスピード
        )
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 背景の描画
        painter.fillRect(self.rect(), QColor(240, 240, 240))

        # ピアノロール風の背景を描画
        self.draw_piano_roll_background(painter)

        # 検出されたピッチの描画
        self.draw_pitch_notes(painter)

        # 現在の再生位置を示す線を描画
        pen = QPen(QColor(255, 0, 0), 2)
        painter.setPen(pen)
        painter.drawLine(self.position_line_x, 0, self.position_line_x, self.height())

    def draw_piano_roll_background(self, painter):
        pen = QPen(QColor(200, 200, 200), 1)
        painter.setPen(pen)
        for midi_note in range(self.note_range[0], self.note_range[1] + 1):
            y = self.note_to_y(midi_note)
            if librosa.midi_to_note(midi_note).endswith("#"):
                # シャープが付いているノートをグレーで塗りつぶし
                painter.fillRect(
                    0, y, self.width(), self.note_height, QColor(220, 220, 220)
                )
            painter.drawLine(0, y, self.width(), y)

        # 一番下のノートの下の線を描画
        painter.drawLine(
            0,
            self.note_to_y(self.note_range[0]) + self.note_height,
            self.width(),
            self.note_to_y(self.note_range[0]) + self.note_height,
        )

        # ノート名を描画
        font = QFont("Arial", 8)
        painter.setFont(font)
        for midi_note in range(self.note_range[0], self.note_range[1] + 1):
            if not librosa.midi_to_note(midi_note).endswith("#"):
                note_name = librosa.midi_to_note(midi_note)
                y = self.note_to_y(midi_note)
                painter.drawText(
                    5, y + self.note_height - 1, f"{note_name}"
                )  # 5はテキストの左マージン

    def draw_pitch_notes(self, painter):
        pen = QPen(QColor(0, 100, 255), 3)
        painter.setPen(pen)

        for note in self.pitch_data:
            start_x = note["start"] * 50 - self.scroll_offset
            end_x = note["end"] * 50 - self.scroll_offset
            width = end_x - start_x

            # 画面外に出たら描画をスキップ
            if end_x < 0:  # バーの終端が画面左端より左にある場合
                continue
            if start_x > self.width():  # バーの始点が画面右端より右にある場合
                break

            # 描画範囲を制限
            if start_x < 0:
                start_x = 0
            if end_x > self.width():
                end_x = self.width()
            width = end_x - start_x

            if note["pitch"] > 0:  # 無音部分はスキップ
                y = self.note_to_y(note["pitch"])
                rect = QRectF(start_x, y, width, self.note_height)
                painter.drawRect(rect)

    def note_to_y(self, midi_note):
        # MIDIノート番号からY座標を計算
        note_index = self.note_range[1] - midi_note
        return note_index * self.note_height

    def reset(self):
        self.current_position = 0
        self.scroll_offset = 0
        self.update()
