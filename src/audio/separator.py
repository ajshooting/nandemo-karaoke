import os
from spleeter.separator import Separator as SpleeterSeparator
from spleeter.audio.adapter import AudioAdapter


class Separator:
    def __init__(self, model="spleeter:2stems"):
        self.model = model
        self.spleeter_separator = SpleeterSeparator(self.model)
        self.audio_adapter = AudioAdapter.default()

    def separate(self, input_path):
        # ここでは音源ファイルのpathが渡される
        music_name = os.path.basename(os.path.dirname(input_path))
        output_directory = os.path.join("data", "output", music_name)
        vocals_path = os.path.join(output_directory, "vocals.mp3")
        accompaniment_path = os.path.join(output_directory, "accompaniment.mp3")

        # すでに存在するかどうか
        if os.path.exists(vocals_path) and os.path.exists(accompaniment_path):
            print(f"分離済みファイルが見つかりました: {output_directory}")
            return {"vocals": vocals_path, "accompaniment": accompaniment_path}
        else:
            print(f"分離処理を開始します: {input_path}")
            os.makedirs(output_directory, exist_ok=True)

            self.spleeter_separator.separate_to_file(
                input_path,
                output_directory,
                codec="mp3",
                filename_format="{instrument}.{codec}",  # ファイル名を直接指定
            )

            print(f"分離処理が完了しました: {output_directory}")
            return {"vocals": vocals_path, "accompaniment": accompaniment_path}
