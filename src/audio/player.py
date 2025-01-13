import simpleaudio as sa
import time
from pydub import AudioSegment
import io


class Player:
    def __init__(self):
        self.play_obj = None
        self.start_time = None
        self.pause_time = None
        self.audio_path = None
        self.audio_segment = None

    def play(self, audio_path):
        try:
            if self.play_obj and self.play_obj.is_playing():
                self.play_obj.stop()

            # オーディオファイルのパスを保存
            self.audio_path = audio_path

            # mp3しか扱わないことにした
            sound = AudioSegment.from_file(audio_path, format="mp3")

            # WAV形式に変換し、BytesIOオブジェクトとして出力する
            wav_io = io.BytesIO()
            sound.export(wav_io, format="wav")
            wav_io.seek(0)  # BytesIOの先頭に移動する

            # simpleaudioで再生可能なWaveObject
            wave_obj = sa.WaveObject.from_wave_file(wav_io)

            # 再生する
            self.play_obj = wave_obj.play()
            self.start_time = time.time()
            self.pause_time = None

            # AudioSegmentを保存
            self.audio_segment = sound

        except ValueError as ve:
            print(f"オーディオ再生エラー: {ve}")

        except Exception as e:
            print(f"オーディオ再生エラー: {e}")

    def stop(self):
        if self.play_obj:
            self.play_obj.stop()
            self.start_time = None
            self.pause_time = None
            self.audio_path = None
            self.audio_segment = None

    def pause(self):
        if self.play_obj and self.play_obj.is_playing():
            self.play_obj.stop()
            self.pause_time = time.time()

    def resume(self):
        if self.audio_path and self.pause_time:
            elapsed_time = int(
                (self.pause_time - self.start_time) * 1000
            )  # ミリ秒単位で経過時間を計算

            # 再生開始位置からAudioSegmentを切り出し
            remaining_segment = self.audio_segment[elapsed_time:]

            # WAV形式に変換し、BytesIOオブジェクトとして出力する
            wav_io = io.BytesIO()
            remaining_segment.export(wav_io, format="wav")
            wav_io.seek(0)

            # simpleaudioで再生可能なWaveObject
            wave_obj = sa.WaveObject.from_wave_file(wav_io)

            # 再生する
            self.play_obj = wave_obj.play()
            self.start_time = time.time() - (
                self.pause_time - self.start_time
            )  # 再生開始時刻を調整
            self.pause_time = None

    def is_playing(self):
        return self.play_obj is not None and self.play_obj.is_playing()

    def get_current_time(self):
        if self.is_playing():
            # 現在の時刻 - 再生開始時刻
            return round(time.time() - self.start_time, 2)
        elif self.pause_time:
            # 一時停止中の場合は、一時停止した時点の経過時間を返す
            return round(self.pause_time - self.start_time, 2)
        else:
            return 0.0
