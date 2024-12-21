from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtCore import pyqtSlot, QTimer
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPixmap

# widgetsフォルダからカスタムウィジェットをインポート
from src.gui.widgets.pitch_bar import PitchBar

# 他の処理系モジュールをインポート (必要に応じて)
from src.audio.player import Player
from src.audio.recorder import Recorder
from src.pitch.extractor import PitchExtractor
from src.lyrics.synchronizer import Synchronizer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("src/gui/ui/main_window.ui", self) # Qt Designerで作成したUIファイルを読み込む

        # ウィジェットの取得 (UIファイルで設定したobjectNameでアクセス)
        self.lyrics_label = self.findChild(QLabel, "lyricsLabel")
        self.pitch_bar_widget = self.findChild(PitchBar, "pitchBarWidget") # UIファイルで設定したPitchBarウィジェット
        self.play_button = self.findChild(QPushButton, "playButton")
        self.stop_button = self.findChild(QPushButton, "stopButton")
        self.score_label = self.findChild(QLabel, "scoreLabel")

        # ボタンのシグナルとスロットを接続
        self.play_button.clicked.connect(self.on_play_clicked)
        self.stop_button.clicked.connect(self.on_stop_clicked)

        # タイマー設定 (例: 音程バーの更新)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pitch_bar)
        self.timer.setInterval(100) # 例: 100msごとに更新

        # 他の処理系モジュールの初期化 (必要に応じて)
        self.audio_player = Player()
        self.audio_recorder = Recorder()
        self.pitch_extractor = PitchExtractor()
        self.lyric_synchronizer = Synchronizer()

        # 初期設定
        self.current_song_path = "" # 現在の曲のパス
        self.lyrics = [] # 歌詞リスト
        self.pitch_data = [] # 音程データ

    @pyqtSlot()
    def on_play_clicked(self):
        print("Playボタンがクリックされました")
        # 再生処理を実装
        # 例: self.audio_player.play(self.current_song_path)
        #     self.timer.start()

    @pyqtSlot()
    def on_stop_clicked(self):
        print("Stopボタンがクリックされました")
        # 停止処理を実装
        # 例: self.audio_player.stop()
        #     self.timer.stop()

    @pyqtSlot()
    def update_pitch_bar(self):
        # 音程バーの更新処理
        # 例: 現在の再生時間に基づいて音程データを取得し、PitchBarに渡す
        #     current_time = self.audio_player.get_current_time()
        #     pitch_value = self.get_pitch_at_time(current_time)
        #     self.pitch_bar_widget.set_pitch(pitch_value)
        pass

    def set_lyrics(self, lyrics):
        self.lyrics = lyrics
        # 歌詞をQLabelに表示する処理 (例: 最初の歌詞を表示)
        if self.lyrics:
            self.lyrics_label.setText(self.lyrics[0])

    def set_pitch_data(self, pitch_data):
        self.pitch_data = pitch_data

    def update_lyrics_display(self, current_time):
        # 現在の再生時間に基づいて歌詞を更新する処理
        # 例: self.lyric_synchronizer.get_current_lyric(current_time) を使用
        pass

    def update_score(self, score):
        self.score_label.setText(f"スコア: {score}")

    # 他の処理からの呼び出し用メソッド (例: 音程データのセット)
    # def set_pitch_data(self, pitch_data):
    #     self.pitch_bar_widget.set_data(pitch_data)

    # 必要に応じて他のスロットやメソッドを追加

def main():
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()