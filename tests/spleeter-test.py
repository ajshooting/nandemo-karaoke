# spleeterのテスト
from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter
from multiprocessing import freeze_support

if __name__ == '__main__':
    freeze_support()

    separator = Separator('spleeter:2stems')

    audio_file = 'tests/勘ぐれい.wav'
    output_directory = 'tests/output'

    audio_loader = AudioAdapter.default()
    waveform, sample_rate = audio_loader.load(audio_file, sample_rate=44100)

    # 実行/保存
    prediction = separator.separate(waveform)
    separator.separate_to_file(audio_file, output_directory, codec='wav')