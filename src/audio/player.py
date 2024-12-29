import simpleaudio as sa
import time


class Player:
    def __init__(self):
        self.wave_obj = None
        self.play_obj = None
        self.start_time = None

    def play(self, audio_path):
        try:
            if self.play_obj and self.play_obj.is_playing():
                self.play_obj.stop()

            self.wave_obj = sa.WaveObject.from_wave_file(audio_path)
            self.play_obj = self.wave_obj.play()
            self.start_time = time.time()
        except Exception as e:
            print(f"オーディオ再生エラー: {e}")

    def stop(self):
        if self.play_obj:
            self.play_obj.stop()
            self.start_time = None

    def is_playing(self):
        return self.play_obj is not None and self.play_obj.is_playing()

    def get_current_time(self):
        if self.is_playing():
            # 現在の時刻 - 再生開始時刻
            return time.time() - self.start_time
        else:
            return 0.0
