import os
from spleeter.separator import Separator as SpleeterSeparator
from spleeter.audio.adapter import AudioAdapter
from multiprocessing import freeze_support

# spleeterを使用して音源分離
# 高速化オプションで位相打ち消しも検討

class Separator:
    def __init__(self, model='spleeter:2stems'):
        self.model = model
        self.spleeter_separator = SpleeterSeparator(self.model)
        self.audio_adapter = AudioAdapter.default()

    def separate(self, input_path):
        filename_without_ext = os.path.splitext(os.path.basename(input_path))[0]
        output_directory = os.path.join('data', 'output', filename_without_ext)
        os.makedirs(output_directory, exist_ok=True)

        self.spleeter_separator.separate_to_file(
            input_path,
            output_directory,
            codec='wav',
            filename_format='{instrument}.{codec}'  # ファイル名を直接指定
        )

        # 分離されたファイルのパスを返す
        vocals_path = os.path.join(output_directory, 'vocals.wav')
        accompaniment_path = os.path.join(output_directory, 'accompaniment.wav')

        return {'vocals': vocals_path, 'accompaniment': accompaniment_path}