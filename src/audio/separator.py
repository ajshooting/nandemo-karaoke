import os
from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter
from multiprocessing import freeze_support

# spleeterを使用して音源分離
# 高速化オプションで位相打ち消しも検討

class Separator:
    def separate(self, input_path):
        # 音源分離処理を実装
        inst_audio_path = ""
        vocals_audio_path = ""
        
        # これいるのかな
        freeze_support()
        
        separator = Separator('spleeter:2stems')
        
        output_directory = f'data/output/{os.path.basename(input_path)}'

        audio_loader = AudioAdapter.default()
        waveform, sample_rate = audio_loader.load(input_path, sample_rate=44100)

        # 実行/保存
        prediction = separator.separate(waveform)
        separator.separate_to_file(input_path, output_directory, codec='wav')
        
        
        return output_directory