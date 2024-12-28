import simpleaudio as sa
import time


class Player:
    def __init__(self):
        self.wave_obj = None
        self.play_obj = None
        self.start_time = None  # 再生開始時間を保存する

    def play(self, audio_path):
        try:
            if self.play_obj and self.play_obj.is_playing():
                self.play_obj.stop()

            self.wave_obj = sa.WaveObject.from_wave_file(audio_path)
            self.play_obj = self.wave_obj.play()
            self.start_time = time.time()  # 再生開始時間を記録
        except Exception as e:
            print(f"Error playing audio file: {e}")

    def stop(self):
        if self.play_obj:
            self.play_obj.stop()
            self.start_time = None  # Stopしたらリセット

    def is_playing(self):
        return self.play_obj is not None and self.play_obj.is_playing()

    def get_current_time(self):
        if self.is_playing():
            # 再生中の場合、現在の時刻から再生開始時刻を引いて経過時間を計算 (秒単位)
            return time.time() - self.start_time
        else:
            # 再生中でない場合は0を返す
            return 0.0
