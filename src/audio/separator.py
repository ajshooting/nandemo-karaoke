import os
from spleeter.separator import Separator as SpleeterSeparator
from spleeter.audio.adapter import AudioAdapter


class Separator:
    def __init__(self, model="spleeter:2stems"):
        self.model = model
        self.spleeter_separator = SpleeterSeparator(self.model)
        self.audio_adapter = AudioAdapter.default()

    def separate(self, input_path):
        filename_without_ext = os.path.splitext(os.path.basename(input_path))[0]
        output_directory = os.path.join("data", "output", filename_without_ext)
        vocals_path = os.path.join(output_directory, "vocals.wav")
        accompaniment_path = os.path.join(output_directory, "accompaniment.wav")

        # 分離済みファイルが存在するか確認
        if os.path.exists(vocals_path) and os.path.exists(accompaniment_path):
            print(f"分離済みファイルが見つかりました: {output_directory}")
            return {"vocals": vocals_path, "accompaniment": accompaniment_path}
        else:
            print(f"分離処理を開始します: {input_path}")
            os.makedirs(output_directory, exist_ok=True)

            self.spleeter_separator.separate_to_file(
                input_path,
                output_directory,
                codec="wav",
                filename_format="{instrument}.{codec}",  # ファイル名を直接指定
            )

            print(f"分離処理が完了しました: {output_directory}")
            return {"vocals": vocals_path, "accompaniment": accompaniment_path}
