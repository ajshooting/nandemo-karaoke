import simpleaudio as sa


class Player:
    def __init__(self):
        self.wave_obj = None

    def play(self, audio_path):
        try:
            self.wave_obj = sa.WaveObject.from_wave_file(audio_path)
            self.play_obj = self.wave_obj.play()
        except Exception as e:
            print(f"Error playing audio file: {e}")

    def stop(self):
        if self.play_obj:
            self.play_obj.stop()

    def get_current_time(self):
        if self.play_obj and self.wave_obj:
            return self.play_obj.time_played / self.wave_obj.frame_rate
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
