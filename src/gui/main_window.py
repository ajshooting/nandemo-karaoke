from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QFileDialog,
    QMessageBox,
    QApplication,
    QProgressDialog,
)
from PyQt6.QtCore import pyqtSlot, QTimer, Qt, QThread, pyqtSignal
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent

# widgetsフォルダからカスタムウィジェットをインポート
from src.gui.widgets.pitch_bar import PitchBar

# 他の処理系モジュールをインポート (必要に応じて)
from src.audio.player import Player
from src.audio.recorder import Recorder
from src.audio.separator import Separator
from src.pitch.extractor import PitchExtractor
from src.lyrics.synchronizer import Synchronizer
from src.lyrics.recognizer import Recognizer  # Recognizerのインポート


class RecognitionThread(QThread):
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(str)

    def __init__(self, audio_path, parent=None):
        super().__init__(parent)
        self.audio_path = audio_path
        self.recognizer = Recognizer()

    def run(self):
        self.progress_signal.emit("音声認識を実行中...")
        try:
            lyrics_data = self.recognizer.recognize_lyrics(self.audio_path)
            if lyrics_data:
                self.finished_signal.emit(lyrics_data)
            else:
                self.error_signal.emit("音声認識に失敗しました。")
        except Exception as e:
            self.error_signal.emit(f"音声認識エラー: {e}")


class SeparationThread(QThread):
    finished_signal = pyqtSignal(dict)  # 分離されたファイルのパスを辞書で送信
    error_signal = pyqtSignal(str)

    def __init__(self, input_path):
        super().__init__()
        self.input_path = input_path
        self.separator = Separator()  # Separatorクラスのインスタンスを作成

    def run(self):
        try:
            separated_paths = self.separator.separate(
                self.input_path
            )  # separateメソッドを呼び出す
            self.finished_signal.emit(separated_paths)  # 分離されたパスを送信
        except Exception as e:
            self.error_signal.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(
            "src/gui/ui/main_window.ui", self
        )  # Qt Designerで作成したUIファイルを読み込む

        # ウィジェットの取得 (UIファイルで設定したobjectNameでアクセス)
        self.lyrics_label = self.findChild(QLabel, "lyricsLabel")
        self.pitch_bar_widget = self.findChild(
            PitchBar, "pitchBarWidget"
        )  # UIファイルで設定したPitchBarウィジェット
        self.play_button = self.findChild(QPushButton, "playButton")
        self.stop_button = self.findChild(QPushButton, "stopButton")
        self.score_label = self.findChild(QLabel, "scoreLabel")

        # ドロップ/選択エリアの作成
        self.drop_area = QLabel("ここに音源ファイルをドロップしてください", self)
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setFrameStyle(QLabel.Shape.StyledPanel | QLabel.Shadow.Sunken)
        self.drop_area.setAcceptDrops(True)
        self.findChild(QVBoxLayout, "verticalLayout").insertWidget(
            0, self.drop_area
        )  # verticalLayoutの先頭に挿入

        # ボタンのシグナルとスロットを接続
        self.play_button.clicked.connect(self.on_play_clicked)
        self.stop_button.clicked.connect(self.on_stop_clicked)
        self.drop_area.mousePressEvent = self.on_drop_area_clicked  # クリックイベント

        # ドロップイベントのオーバーライド
        self.drop_area.dragEnterEvent = self.dragEnterEvent
        self.drop_area.dropEvent = self.dropEvent

        # タイマー設定 (例: 音程バーと歌詞の更新)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pitch_bar)
        self.timer.timeout.connect(self.update_lyrics_display)  # 歌詞更新処理を追加
        self.timer.setInterval(100)  # 例: 100msごとに更新

        # 他の処理系モジュールの初期化 (必要に応じて)
        self.audio_player = Player()
        self.audio_recorder = Recorder()
        self.pitch_extractor = PitchExtractor()
        self.lyric_synchronizer = Synchronizer()
        self.recognizer = Recognizer()  # Recognizerのインスタンス化
        self.recognition_thread = None

        # 初期設定
        self.current_song_path = ""  # 現在の曲のパス
        self.separated_song_paths = (
            {}
        )  # 分離後の曲のパスを格納する辞書 (例: {'vocals': '...', 'accompaniment': '...' })
        self.lyrics = []  # 歌詞リスト
        self.pitch_data = []  # 音程データ
        self.accompaniment_path = None  # 分離後の伴奏ファイルのパスを保存する変数
        self.recognized_lyrics = []  # 音声認識された歌詞を保存するリスト
        self.current_lyric_index = 0  # 現在表示中の歌詞のインデックス

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            self.process_audio_file(file_path)

    def on_drop_area_clicked(self, event):
        options = QFileDialog.Option.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "音源ファイルを選択してください",
            "",
            "Audio Files (*.mp3 *.wav *.ogg)",
            options=options,
        )
        if file_name:
            self.process_audio_file(file_name)

    def process_audio_file(self, file_path):
        self.current_song_path = file_path
        self.start_separation(file_path)
        self.start_recognition(file_path)  # 音声認識の開始

    def start_recognition(self, audio_path):
        self.recognition_progress_dialog = QProgressDialog(
            "音声認識を実行中...", None, 0, 0, self
        )
        self.recognition_progress_dialog.setCancelButtonText(None)
        self.recognition_progress_dialog.setModal(True)
        self.recognition_progress_dialog.show()

        self.recognition_thread = RecognitionThread(audio_path, self)
        self.recognition_thread.finished_signal.connect(self.on_recognition_finished)
        self.recognition_thread.error_signal.connect(self.on_recognition_error)
        self.recognition_thread.progress_signal.connect(
            self.recognition_progress_dialog.setLabelText
        )
        self.recognition_thread.start()

    def on_recognition_finished(self, lyrics_data):
        self.recognition_progress_dialog.close()
        self.recognized_lyrics = lyrics_data
        QMessageBox.information(self, "完了", "音声認識が完了しました。")

    def on_recognition_error(self, error_message):
        self.recognition_progress_dialog.close()
        QMessageBox.critical(
            self, "エラー", f"音声認識中にエラーが発生しました: {error_message}"
        )

    def start_separation(self, input_path):
        self.progress_dialog = QProgressDialog("音源分離処理中...", None, 0, 0, self)
        self.progress_dialog.setCancelButtonText(None)
        self.progress_dialog.setModal(True)
        self.progress_dialog.show()

        self.separation_thread = SeparationThread(input_path)
        self.separation_thread.finished_signal.connect(self.on_separation_finished)
        self.separation_thread.error_signal.connect(self.on_separation_error)
        self.separation_thread.start()

    def on_separation_finished(self, separated_paths):
        self.progress_dialog.close()
        self.separated_song_paths = separated_paths
        QMessageBox.information(self, "完了", "音源分離が完了しました。")

        # 分離が完了したら、伴奏ファイルのパスを保存
        self.accompaniment_path = self.separated_song_paths.get("accompaniment")

    def on_separation_error(self, error_message):
        self.progress_dialog.close()
        QMessageBox.critical(
            self, "エラー", f"音源分離中にエラーが発生しました: {error_message}"
        )

    @pyqtSlot()
    def on_play_clicked(self):
        if not self.current_song_path:
            QMessageBox.warning(self, "警告", "音源ファイルが選択されていません。")
            return

        if not self.recognized_lyrics:
            QMessageBox.warning(self, "警告", "音声認識が完了していません。")
            return

        if self.accompaniment_path:
            print(
                f"再生ボタンがクリックされました。再生ファイル: {self.accompaniment_path}"
            )
            self.audio_player.play(self.accompaniment_path)
        elif self.current_song_path:  # 分離前のオリジナル音源を再生
            print(
                f"再生ボタンがクリックされました。再生ファイル: {self.current_song_path}"
            )
            self.audio_player.play(self.current_song_path)
        else:
            QMessageBox.warning(
                self,
                "警告",
                "音源ファイルが選択されていません。先に音源ファイルをドロップまたは選択してください。",
            )
            return

        self.timer.start()
        self.current_lyric_index = 0  # 再生開始時にインデックスをリセット

    @pyqtSlot()
    def on_stop_clicked(self):
        print("Stopボタンがクリックされました")
        self.audio_player.stop()
        self.timer.stop()
        self.lyrics_label.setText("")  # 停止時に歌詞表示をクリア

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

    def update_lyrics_display(self):
        if not self.audio_player.is_playing():
            return

        current_time = self.audio_player.get_current_time()  # 秒単位で取得

        for i, lyric_info in enumerate(
            self.recognized_lyrics[self.current_lyric_index :]
        ):
            if lyric_info["start"] <= current_time < lyric_info["end"]:
                if (
                    self.current_lyric_index + i < len(self.recognized_lyrics)
                    and self.lyrics_label.text()
                    != self.recognized_lyrics[self.current_lyric_index + i]["word"]
                ):
                    self.lyrics_label.setText(lyric_info["word"])

                self.current_lyric_index += i
                return
            elif current_time >= lyric_info["end"]:
                # 現在時刻が歌詞の終了時刻を超えている場合は次の歌詞へ
                continue
            else:
                # まだ歌詞の開始時刻に達していない
                break
        else:
            # 全ての歌詞を表示し終えた場合
            if (
                self.recognized_lyrics
                and current_time >= self.recognized_lyrics[-1]["end"]
            ):
                self.lyrics_label.setText("")  # 最後の歌詞を表示し終えたらクリア
                self.timer.stop()  # タイマー停止

    def update_score(self, score):
        self.score_label.setText(f"スコア: {score}")


def main():
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec()


if __name__ == "__main__":
    main()
