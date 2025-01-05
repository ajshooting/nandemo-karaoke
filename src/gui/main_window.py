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
import os, sys
import logging

# ロギング設定
logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# カスタムウィジェットをインポート
from src.gui.widgets.pitch_bar import PitchBar

# モジュールをインポート
from src.audio.player import Player
from src.audio.recorder import Recorder
from src.audio.separator import Separator
from src.pitch.extractor import PitchExtractor
from src.lyrics.synchronizer import Synchronizer
from src.lyrics.recognizer import Recognizer  # Recognizerのインポート


class PitchExtractionThread(QThread):
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path
        self.pitch_extractor = PitchExtractor()
        logging.info(f"PitchExtractionThread initialized with audio_path: {audio_path}")

    def run(self):
        logging.info(f"PitchExtractionThread started for: {self.audio_path}")
        try:
            pitch_data = self.pitch_extractor.extract_pitch(self.audio_path)
            self.finished_signal.emit(pitch_data)
            logging.info("PitchExtractionThread finished successfully.")
        except Exception as e:
            error_message = f"Error in PitchExtractionThread: {e}"
            self.error_signal.emit(error_message)
            logging.error(error_message, exc_info=True)


class RecognitionThread(QThread):
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(str)

    def __init__(self, audio_path, parent=None):
        super().__init__(parent)
        self.audio_path = audio_path
        self.recognizer = Recognizer()
        logging.info(f"RecognitionThread initialized with audio_path: {audio_path}")

    def run(self):
        logging.info(f"RecognitionThread started for: {self.audio_path}")
        self.progress_signal.emit("音声認識を実行中...")
        try:
            lyrics_data = self.recognizer.recognize_lyrics(self.audio_path)
            if lyrics_data:
                self.finished_signal.emit(lyrics_data)
                logging.info("RecognitionThread finished successfully.")
            else:
                error_message = "音声認識に失敗しました。"
                self.error_signal.emit(error_message)
                logging.error(error_message)
        except Exception as e:
            error_message = f"音声認識エラー: {e}"
            self.error_signal.emit(error_message)
            logging.error(error_message, exc_info=True)


class SeparationThread(QThread):
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, input_path):
        super().__init__()
        self.input_path = input_path
        self.separator = Separator()
        logging.info(f"SeparationThread initialized with input_path: {input_path}")

    def run(self):
        logging.info(f"SeparationThread started for: {self.input_path}")
        try:
            separated_paths = self.separator.separate(self.input_path)
            self.finished_signal.emit(separated_paths)
            logging.info(
                f"SeparationThread finished successfully. Separated paths: {separated_paths}"
            )
        except Exception as e:
            error_message = f"Error in SeparationThread: {e}"
            self.error_signal.emit(error_message)
            logging.error(error_message, exc_info=True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # こうしないとpyinstallerでうまくいかない..?
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        ui_path = os.path.join(base_path, "gui/ui/main_window.ui")
        loadUi(ui_path, self)
        logging.info(f"UI loaded from: {ui_path}")

        # ウィジェットの取得 (.uiのobjectName)
        self.lyrics_label = self.findChild(QLabel, "lyricsLabel")
        self.pitch_bar_widget = self.findChild(PitchBar, "pitchBarWidget")
        self.play_button = self.findChild(QPushButton, "playButton")
        self.stop_button = self.findChild(QPushButton, "stopButton")
        self.score_label = self.findChild(QLabel, "scoreLabel")

        # ドロップ/選択エリアの作成
        self.drop_area = QLabel("ここに音源ファイルをドロップしてください", self)
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setFrameStyle(QLabel.Shape.StyledPanel | QLabel.Shadow.Sunken)
        self.drop_area.setAcceptDrops(True)
        # verticalLayoutの先頭に挿入
        self.findChild(QVBoxLayout, "verticalLayout").insertWidget(0, self.drop_area)

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

        # 他の処理系モジュールの初期化
        self.audio_player = Player()
        self.audio_recorder = Recorder()
        self.pitch_extractor = PitchExtractor()
        self.lyric_synchronizer = Synchronizer()
        self.recognizer = Recognizer()
        self.recognition_thread = None

        # 初期設定
        self.current_song_path = ""  # 現在の曲のパス
        # 分離後の曲のパスを格納する辞書 (例: {'vocals': '...', 'accompaniment': '...' })
        self.separated_song_paths = {}
        self.lyrics = []  # 歌詞リスト
        self.pitch_data = []  # 音程データ
        self.accompaniment_path = None  # 分離後の伴奏ファイルのパスを保存する変数
        self.recognized_lyrics = []  # 音声認識された歌詞を保存するリスト
        self.current_lyric_index = 0  # 現在表示中の歌詞のインデックス

        self.current_segment_index = 0  # 現在表示中のフレーズのインデックス
        self.current_word_index = 0  # 現在色付け中の単語のインデックス

        self.lyrics_label = self.findChild(QLabel, "lyricsLabel")
        self.lyrics_label.setTextFormat(Qt.TextFormat.RichText)  # リッチテキストを有効

        # 各種スレッドを保持する変数を初期化
        self.separation_thread = None
        self.recognition_thread = None
        self.pitch_extraction_thread = None

        logging.info("MainWindow initialized")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            logging.info(f"File dropped: {file_path}")
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
            logging.info(f"File selected: {file_name}")
            self.process_audio_file(file_name)

    def process_audio_file(self, file_path):
        self.current_song_path = file_path
        logging.info(f"Processing audio file: {file_path}")
        self.start_separation(file_path)
        self.start_recognition(file_path)
        # self.start_pitch_extraction(file_path)

    def start_pitch_extraction(self, audio_path):
        logging.info(f"Starting pitch extraction for: {audio_path}")
        self.pitch_extraction_thread = PitchExtractionThread(audio_path)
        self.pitch_extraction_thread.finished_signal.connect(
            self.on_pitch_extraction_finished
        )
        self.pitch_extraction_thread.error_signal.connect(
            self.on_pitch_extraction_error
        )
        self.pitch_extraction_thread.start()

    def on_pitch_extraction_finished(self, pitch_data):
        self.pitch_data = pitch_data
        QMessageBox.information(self, "完了", "ピッチ解析が完了しました。")
        # ピッチ解析が完了したら、ピッチバーウィジェットにデータを設定
        self.pitch_bar_widget.set_pitch_data(pitch_data)
        self.pitch_bar_widget.reset()
        logging.info("Pitch extraction finished successfully.")

    def on_pitch_extraction_error(self, error_message):
        QMessageBox.critical(
            self, "エラー", f"ピッチ解析中にエラーが発生しました: {error_message}"
        )
        logging.error(f"Error during pitch extraction: {error_message}")

    def start_recognition(self, audio_path):
        logging.info(f"Starting recognition for: {audio_path}")
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
        self.current_segment_index = 0  # 音声認識完了時にリセット
        self.lyrics_label.setText("")
        logging.info("Recognition finished successfully.")

    def on_recognition_error(self, error_message):
        self.recognition_progress_dialog.close()
        QMessageBox.critical(
            self, "エラー", f"音声認識中にエラーが発生しました: {error_message}"
        )
        logging.error(f"Error during recognition: {error_message}")

    def start_separation(self, input_path):
        logging.info(f"Starting separation for: {input_path}")
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

        # 分離が完了したら、伴奏ファイルのパスを保存
        self.accompaniment_path = self.separated_song_paths.get("accompaniment")
        vocals_path = self.separated_song_paths.get("vocals")

        # vocalに音声認識をする予定だったが、音源そのままを認識させた方が精度が高かった..
        # if vocals_path:
        #     self.start_recognition(vocals_path)
        # else:
        #     QMessageBox.warning(
        #         self, "警告", "ボーカルファイルが見つかりませんでした。"
        #     )

        # ピッチ解析を開始 (ボーカルに対して実行)
        if vocals_path:
            self.start_pitch_extraction(vocals_path)
        else:
            QMessageBox.warning(
                self, "警告", "ボーカルファイルが見つかりませんでした。"
            )

        # ここにおけばOK押す前に次の処理が開始されると予想
        QMessageBox.information(self, "完了", "音源分離が完了しました。")
        logging.info(
            f"Separation finished successfully. Separated paths: {separated_paths}"
        )

    def on_separation_error(self, error_message):
        self.progress_dialog.close()
        QMessageBox.critical(
            self, "エラー", f"音源分離中にエラーが発生しました: {error_message}"
        )
        logging.error(f"Error during separation: {error_message}")

    @pyqtSlot()
    def on_play_clicked(self):
        if not self.current_song_path:
            QMessageBox.warning(self, "警告", "音源ファイルが選択されていません。")
            return

        if not self.recognized_lyrics:
            QMessageBox.warning(self, "警告", "音声認識が完了していません。")
            return

        if not self.pitch_data:
            QMessageBox.warning(self, "警告", "ピッチ解析が完了していません。")
            return

        if self.accompaniment_path:
            print(f"再生: {self.accompaniment_path}")
            self.audio_player.play(self.accompaniment_path)
        else:
            QMessageBox.warning(
                self,
                "警告",
                "音源ファイルが選択されていません。先に音源ファイルをドロップまたは選択してください。",
            )
            return

        self.lyrics_label.setText("")
        self.pitch_bar_widget.reset()

        self.timer.start()
        self.current_lyric_index = 0  # 再生開始時にインデックスをリセット

        self.current_word_index = 0
        self.update_lyrics_display()  # 初期表示のため呼び出す
        logging.info(f"Playing audio: {self.accompaniment_path}")

    @pyqtSlot()
    def on_stop_clicked(self):
        print("再生停止")
        self.audio_player.stop()
        self.timer.stop()
        self.lyrics_label.setText("")  # 停止時に歌詞表示をクリア
        self.pitch_bar_widget.reset()

        self.current_segment_index = 0  # 停止時にリセット
        self.current_word_index = 0
        logging.info("Stopping audio playback.")

    @pyqtSlot()
    def update_pitch_bar(self):
        # 音程バーの更新処理
        if self.audio_player.is_playing():
            current_time = self.audio_player.get_current_time()
            self.pitch_bar_widget.update_position(current_time)

    # ! これ使われてなくない？
    def set_lyrics(self, lyrics):
        self.lyrics = lyrics
        # 歌詞をQLabelに表示する処理 (例: 最初の歌詞を表示)
        if self.lyrics:
            self.lyrics_label.setText(self.lyrics[0])

    def set_pitch_data(self, pitch_data):
        self.pitch_data = pitch_data

    def update_lyrics_display(self):
        if not self.audio_player.is_playing() or not self.recognized_lyrics:
            return

        current_time = self.audio_player.get_current_time()

        if self.current_segment_index < len(self.recognized_lyrics):
            segment = self.recognized_lyrics[self.current_segment_index]
            next_segment = (
                self.recognized_lyrics[self.current_segment_index + 1]
                if self.current_segment_index + 1 < len(self.recognized_lyrics)
                else None
            )
            if segment["start"] <= current_time < segment["end"]:
                # 現在のフレーズを表示
                self.display_karaoke_text(segment, next_segment)
            elif current_time >= segment["end"]:
                # 現在のフレーズの終了時間を過ぎたら、次のフレーズへ
                self.current_segment_index += 1
                self.lyrics_label.setText("")  # 次のフレーズ表示前にクリア
                # 次のフレーズが存在すれば、すぐに表示
                if self.current_segment_index < len(self.recognized_lyrics):
                    self.display_karaoke_text(
                        self.recognized_lyrics[self.current_segment_index], next_segment
                    )
            else:
                # まだフレーズの開始時間になっていない
                self.display_karaoke_text(segment, next_segment)
                pass
        elif (
            self.recognized_lyrics and current_time >= self.recognized_lyrics[-1]["end"]
        ):
            # 全てのフレーズを表示し終えた場合
            self.lyrics_label.setText("")
            self.timer.stop()

    def display_karaoke_text(self, segment, next_segment):
        karaoke_text = ""
        current_time = self.audio_player.get_current_time()

        for word_info in segment["words"]:
            if segment["start"] <= current_time < segment["end"]:
                ratio = (
                    (current_time - word_info["start"])
                    / (word_info["end"] - word_info["start"])
                    if (word_info["end"] - word_info["start"]) > 0
                    else 0
                )
                highlight_length = int(len(word_info["word"]) * ratio)
                highlighted_word = f"<span style='color: red; font-size: 20px;'>{word_info['word'][:highlight_length]}</span>{word_info['word'][highlight_length:]}"
                karaoke_text += " " + highlighted_word
            elif current_time >= word_info["end"]:
                karaoke_text += (
                    " " + f"<span style='color: red;'>{word_info['word']}</span>"
                )
            else:
                karaoke_text += " " + word_info["word"]

        # TODO いい感じに調整
        karaoke_text += (
            "<br><br><span style='font-size: 10px;'>" + next_segment["text"] + "</span>"
            if next_segment
            else ""
        )

        self.lyrics_label.setText(karaoke_text)

    # TODO: さいてん、する、、？
    def update_score(self, score):
        self.score_label.setText(f"スコア: {score}")


def main():
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec()
    logging.info("Application started")


if __name__ == "__main__":
    main()
