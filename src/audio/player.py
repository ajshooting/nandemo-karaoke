import simpleaudio as sa
import time
from pydub import AudioSegment
import io


class Player:
    def __init__(self):
        self.play_obj_raw = None
        self.play_obj_accompaniment = None
        self.start_time = None
        self.pause_time = None
        self.audio_path_raw = None
        self.audio_path_accompaniment = None
        self.audio_segment_raw = None
        self.audio_segment_accompaniment = None
        self.raw_volume = 0.5  # 初期音量を設定
        self.accompaniment_volume = 0.5  # 初期音量を設定

    def play(self, audio_path_raw, audio_path_accompaniment):
        try:
            if (
                self.play_obj_raw
                and self.play_obj_raw.is_playing()
                or self.play_obj_accompaniment
                and self.play_obj_accompaniment.is_playing()
            ):
                self.stop()

            # オーディオファイルのパスを保存
            self.audio_path_raw = audio_path_raw
            self.audio_path_accompaniment = audio_path_accompaniment

            # mp3しか扱わないことにした
            sound_raw = AudioSegment.from_file(audio_path_raw, format="mp3")
            sound_accompaniment = AudioSegment.from_file(
                audio_path_accompaniment, format="mp3"
            )

            # 音量を適用
            sound_raw = sound_raw + (10 * (self.raw_volume - 0.5))
            sound_accompaniment = sound_accompaniment + (
                10 * (self.accompaniment_volume - 0.5)
            )

            # WAV形式に変換し、BytesIOオブジェクトとして出力する
            wav_io_raw = io.BytesIO()
            sound_raw.export(wav_io_raw, format="wav")
            wav_io_raw.seek(0)  # BytesIOの先頭に移動する

            wav_io_accompaniment = io.BytesIO()
            sound_accompaniment.export(wav_io_accompaniment, format="wav")
            wav_io_accompaniment.seek(0)

            # simpleaudioで再生可能なWaveObject
            wave_obj_raw = sa.WaveObject.from_wave_file(wav_io_raw)
            wave_obj_accompaniment = sa.WaveObject.from_wave_file(wav_io_accompaniment)

            # 再生する
            self.play_obj_raw = wave_obj_raw.play()
            self.play_obj_accompaniment = wave_obj_accompaniment.play()
            self.start_time = time.time()
            self.pause_time = None

            # AudioSegmentを保存
            self.audio_segment_raw = sound_raw
            self.audio_segment_accompaniment = sound_accompaniment

        except ValueError as ve:
            print(f"オーディオ再生エラー: {ve}")

        except Exception as e:
            print(f"オーディオ再生エラー: {e}")

    def stop(self):
        if self.play_obj_raw:
            self.play_obj_raw.stop()
        if self.play_obj_accompaniment:
            self.play_obj_accompaniment.stop()
        self.start_time = None
        self.pause_time = None
        self.audio_path_raw = None
        self.audio_path_accompaniment = None
        self.audio_segment_raw = None
        self.audio_segment_accompaniment = None

    def pause(self):
        if (
            self.play_obj_raw
            and self.play_obj_raw.is_playing()
            or self.play_obj_accompaniment
            and self.play_obj_accompaniment.is_playing()
        ):
            self.play_obj_raw.stop()
            self.play_obj_accompaniment.stop()
            self.pause_time = time.time()

    def resume(self):
        if self.audio_path_raw and self.audio_path_accompaniment and self.pause_time:
            elapsed_time = int(
                (self.pause_time - self.start_time) * 1000
            )  # ミリ秒単位で経過時間を計算

            # 再生開始位置からAudioSegmentを切り出し
            remaining_segment_raw = self.audio_segment_raw[elapsed_time:]
            remaining_segment_accompaniment = self.audio_segment_accompaniment[
                elapsed_time:
            ]

            # 音量を適用
            remaining_segment_raw = remaining_segment_raw + (
                10 * (self.raw_volume - 0.5)
            )
            remaining_segment_accompaniment = remaining_segment_accompaniment + (
                10 * (self.accompaniment_volume - 0.5)
            )

            # WAV形式に変換し、BytesIOオブジェクトとして出力する
            wav_io_raw = io.BytesIO()
            remaining_segment_raw.export(wav_io_raw, format="wav")
            wav_io_raw.seek(0)

            wav_io_accompaniment = io.BytesIO()
            remaining_segment_accompaniment.export(wav_io_accompaniment, format="wav")
            wav_io_accompaniment.seek(0)

            # simpleaudioで再生可能なWaveObject
            wave_obj_raw = sa.WaveObject.from_wave_file(wav_io_raw)
            wave_obj_accompaniment = sa.WaveObject.from_wave_file(wav_io_accompaniment)

            # 再生する
            self.play_obj_raw = wave_obj_raw.play()
            self.play_obj_accompaniment = wave_obj_accompaniment.play()
            self.start_time = time.time() - (
                self.pause_time - self.start_time
            )  # 再生開始時刻を調整
            self.pause_time = None

    def is_playing(self):
        return (
            self.play_obj_raw is not None
            and self.play_obj_raw.is_playing()
            or self.play_obj_accompaniment is not None
            and self.play_obj_accompaniment.is_playing()
        )

    def get_current_time(self):
        if self.is_playing():
            return round(time.time() - self.start_time, 2)
        elif self.pause_time:
            return round(self.pause_time - self.start_time, 2)
        else:
            return 0.0

    def set_raw_volume(self, volume):
        if (
            self.audio_segment_raw
            and self.play_obj_raw
            and self.play_obj_raw.is_playing()
        ):
            # 現在の再生位置を取得
            current_time = self.get_current_time()

            # 一時停止
            self.pause()

            # 音量を更新
            self.raw_volume = volume

            # 一時停止した位置から再生を再開
            self.resume()

    def set_accompaniment_volume(self, volume):
        if (
            self.audio_segment_accompaniment
            and self.play_obj_accompaniment
            and self.play_obj_accompaniment.is_playing()
        ):
            # 現在の再生位置を取得
            current_time = self.get_current_time()

            # 一時停止
            self.pause()

            # 音量を更新
            self.accompaniment_volume = volume

            # 一時停止した位置から再生を再開
            self.resume()
