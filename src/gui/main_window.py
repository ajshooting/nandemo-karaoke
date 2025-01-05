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

# カスタムウィジェットをインポート
from src.gui.widgets.pitch_bar import PitchBar

# モジュールをインポート
from src.audio.player import Player
from src.audio.recorder import Recorder
from src.audio.separator import Separator
from src.pitch.extractor import PitchExtractor
from src.lyrics.synchronizer import Synchronizer
from src.lyrics.recognizer import Recognizer  # Recognizerのインポート


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # こうしないとpyinstallerでうまくいかない..?
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        ui_path = os.path.join(base_path, "gui/ui/main_window.ui")
        loadUi(ui_path, self)

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
        self.start_processing(file_path)

    def start_processing(self, file_path):
        # 音源分離
        progress_dialog = QProgressDialog("音源分離処理中...", None, 0, 0, self)
        progress_dialog.setCancelButtonText(None)
        progress_dialog.setModal(True)
        progress_dialog.show()

        separator = Separator()
        try:
            separated_paths = separator.separate(file_path)
        except Exception as e:
            progress_dialog.close()
            QMessageBox.critical(
                self, "エラー", f"音源分離中にエラーが発生しました: {e}"
            )
            return
        progress_dialog.close()
        self.separated_song_paths = separated_paths
        self.accompaniment_path = separated_paths.get("accompaniment")
        vocals_path = separated_paths.get("vocals")
        QMessageBox.information(self, "完了", "音源分離が完了しました。")

        # 音声認識
        recognition_progress_dialog = QProgressDialog(
            "音声認識を実行中...", None, 0, 0, self
        )
        recognition_progress_dialog.setCancelButtonText(None)
        recognition_progress_dialog.setModal(True)
        recognition_progress_dialog.show()

        recognizer = Recognizer()
        try:
            lyrics_data = recognizer.recognize_lyrics(
                file_path
            )  # 分離前のファイルパスを渡すように変更
            if not lyrics_data:
                raise ValueError("音声認識に失敗しました。")
        except Exception as e:
            recognition_progress_dialog.close()
            QMessageBox.critical(
                self, "エラー", f"音声認識中にエラーが発生しました: {e}"
            )
            return
        recognition_progress_dialog.close()
        self.recognized_lyrics = lyrics_data
        QMessageBox.information(self, "完了", "音声認識が完了しました。")
        self.current_segment_index = 0  # 音声認識完了時にリセット
        self.lyrics_label.setText("")

        # ピッチ解析
        if not vocals_path:
            QMessageBox.warning(
                self,
                "警告",
                "ボーカルファイルが見つかりませんでした。ピッチ解析をスキップします。",
            )
            return

        pitch_extractor = PitchExtractor()
        try:
            pitch_data = pitch_extractor.extract_pitch(vocals_path)
        except Exception as e:
            QMessageBox.critical(
                self, "エラー", f"ピッチ解析中にエラーが発生しました: {e}"
            )
            return

        self.pitch_data = pitch_data
        QMessageBox.information(self, "完了", "ピッチ解析が完了しました。")
        # ピッチ解析が完了したら、ピッチバーウィジェットにデータを設定
        self.pitch_bar_widget.set_pitch_data(pitch_data)
        self.pitch_bar_widget.reset()

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

    @pyqtSlot()
    def on_stop_clicked(self):
        print("再生停止")
        self.audio_player.stop()
        self.timer.stop()
        self.lyrics_label.setText("")  # 停止時に歌詞表示をクリア
        self.pitch_bar_widget.reset()

        self.current_segment_index = 0  # 停止時にリセット
        self.current_word_index = 0

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


if __name__ == "__main__":
    main()
