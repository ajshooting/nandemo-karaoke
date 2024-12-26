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


if __name__ == "__main__":
    # Example usage
    player = Player()
    audio_file = "test.wav"  # Replace with the path to your audio file

    # Create a dummy test.wav file if it doesn't exist
    try:
        with open(audio_file, "rb") as f:
            pass
    except FileNotFoundError:
        import wave
        import numpy as np

        sample_rate = 44100
        duration = 2  # seconds
        frequency = 440  # Hz
        num_channels = 1
        sample_width = 2
        num_frames = int(sample_rate * duration)
        frames = np.sin(
            2 * np.pi * np.arange(num_frames) * frequency / sample_rate
        ).astype(np.float32)
        frames_scaled = np.int16(frames * 32767)

        with wave.open(audio_file, "w") as wf:
            wf.setnchannels(num_channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            wf.writeframes(frames_scaled.tobytes())
        print(f"Created dummy audio file: {audio_file}")

    print(f"Playing: {audio_file}")
    player.play(audio_file)

    import time

    time.sleep(1)  # Play for 1 second
    print(f"Current time: {player.get_current_time()}")

    print("Stopping...")
    player.stop()

    time.sleep(0.5)

    print("Playing again...")
    player.play(audio_file)
    time.sleep(0.5)
    print(f"Current time: {player.get_current_time()}")
