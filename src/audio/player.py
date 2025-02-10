import simpleaudio as sa
import time
from pydub import AudioSegment
import io


class Player:
    def __init__(self):
        self.play_obj_vocals = None
        self.play_obj_accompaniment = None
        self.start_time = None
        self.pause_time = None
        self.audio_path_vocals = None
        self.audio_path_accompaniment = None
        self.audio_segment_vocals = None
        self.audio_segment_accompaniment = None
        self.vocals_volume = 0.5  # 初期音量を設定
        self.accompaniment_volume = 0.5  # 初期音量を設定

    def play(self, audio_path_vocals, audio_path_accompaniment):
        try:
            if (
                self.play_obj_vocals
                and self.play_obj_vocals.is_playing()
                or self.play_obj_accompaniment
                and self.play_obj_accompaniment.is_playing()
            ):
                self.stop()

            # オーディオファイルのパスを保存
            self.audio_path_vocals = audio_path_vocals
            self.audio_path_accompaniment = audio_path_accompaniment

            # mp3しか扱わないことにした
            sound_vocals = AudioSegment.from_file(audio_path_vocals, format="mp3")
            sound_accompaniment = AudioSegment.from_file(
                audio_path_accompaniment, format="mp3"
            )

            # 音量を適用
            sound_vocals = sound_vocals + (20 * (self.vocals_volume - 1))
            sound_accompaniment = sound_accompaniment + (
                20 * (self.accompaniment_volume - 1)
            )

            # WAV形式に変換し、BytesIOオブジェクトとして出力する
            wav_io_vocals = io.BytesIO()
            sound_vocals.export(wav_io_vocals, format="wav")
            wav_io_vocals.seek(0)  # BytesIOの先頭に移動する

            wav_io_accompaniment = io.BytesIO()
            sound_accompaniment.export(wav_io_accompaniment, format="wav")
            wav_io_accompaniment.seek(0)

            # simpleaudioで再生可能なWaveObject
            wave_obj_vocals = sa.WaveObject.from_wave_file(wav_io_vocals)
            wave_obj_accompaniment = sa.WaveObject.from_wave_file(wav_io_accompaniment)

            # 再生する
            self.play_obj_vocals = wave_obj_vocals.play()
            self.play_obj_accompaniment = wave_obj_accompaniment.play()
            self.start_time = time.time()
            self.pause_time = None

            # AudioSegmentを保存
            self.audio_segment_vocals = sound_vocals
            self.audio_segment_accompaniment = sound_accompaniment

        except ValueError as ve:
            print(f"オーディオ再生エラー: {ve}")

        except Exception as e:
            print(f"オーディオ再生エラー: {e}")

    def stop(self):
        if self.play_obj_vocals:
            self.play_obj_vocals.stop()
        if self.play_obj_accompaniment:
            self.play_obj_accompaniment.stop()
        self.start_time = None
        self.pause_time = None
        self.audio_path_vocals = None
        self.audio_path_accompaniment = None
        self.audio_segment_vocals = None
        self.audio_segment_accompaniment = None

    def pause(self):
        if (
            self.play_obj_vocals
            and self.play_obj_vocals.is_playing()
            or self.play_obj_accompaniment
            and self.play_obj_accompaniment.is_playing()
        ):
            self.play_obj_vocals.stop()
            self.play_obj_accompaniment.stop()
            self.pause_time = time.time()

    def resume(self):
        if self.audio_path_vocals and self.audio_path_accompaniment and self.pause_time:
            elapsed_time = int(
                (self.pause_time - self.start_time) * 1000
            )  # ミリ秒単位で経過時間を計算

            # 再生開始位置からAudioSegmentを切り出し
            remaining_segment_vocals = self.audio_segment_vocals[elapsed_time:]
            remaining_segment_accompaniment = self.audio_segment_accompaniment[
                elapsed_time:
            ]

            # 音量を適用
            remaining_segment_vocals = remaining_segment_vocals + (
                20 * (self.vocals_volume - 1)
            )
            remaining_segment_accompaniment = remaining_segment_accompaniment + (
                20 * (self.accompaniment_volume - 1)
            )

            # WAV形式に変換し、BytesIOオブジェクトとして出力する
            wav_io_vocals = io.BytesIO()
            remaining_segment_vocals.export(wav_io_vocals, format="wav")
            wav_io_vocals.seek(0)

            wav_io_accompaniment = io.BytesIO()
            remaining_segment_accompaniment.export(wav_io_accompaniment, format="wav")
            wav_io_accompaniment.seek(0)

            # simpleaudioで再生可能なWaveObject
            wave_obj_vocals = sa.WaveObject.from_wave_file(wav_io_vocals)
            wave_obj_accompaniment = sa.WaveObject.from_wave_file(wav_io_accompaniment)

            # 再生する
            self.play_obj_vocals = wave_obj_vocals.play()
            self.play_obj_accompaniment = wave_obj_accompaniment.play()
            self.start_time = time.time() - (
                self.pause_time - self.start_time
            )  # 再生開始時刻を調整
            self.pause_time = None

    def is_playing(self):
        return (
            self.play_obj_vocals is not None
            and self.play_obj_vocals.is_playing()
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

    def set_vocals_volume(self, volume):
        self.vocals_volume = volume
        if self.is_playing():
            self.pause()
            self.resume()

    def set_accompaniment_volume(self, volume):
        self.accompaniment_volume = volume
        if self.is_playing():
            self.pause()
            self.resume()

    def update_volumes(self, total_volume, vocal_ratio):
        self.vocals_volume = total_volume * vocal_ratio
        self.accompaniment_volume = total_volume * (1 - vocal_ratio)
        if self.is_playing():
            self.pause()
            self.resume()
