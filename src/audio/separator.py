import os
from spleeter.separator import Separator as SpleeterSeparator
from spleeter.audio.adapter import AudioAdapter


class Separator:
    def __init__(self, model="spleeter:2stems"):

        # model_path = os.environ.get("MODEL_PATH")
        # print(f"MODEL_PATH (before): {model_path}")

        # # 環境変数が設定されていない場合のみ、値を設定する
        # if model_path is None:
        #     os.environ["MODEL_PATH"] = "spleeter/pretrained_models"

        # model_path = os.environ.get("MODEL_PATH")
        # print(f"MODEL_PATH (after): {model_path}")

        try:
            self.model = model
            self.spleeter_separator = SpleeterSeparator(self.model)
            
            # self.audio_adapter = AudioAdapter.default()

        except Exception as e:
            print("initだよ")
            print(e)

    def separate(self, input_path):

        try:

            # model_path = os.environ.get("MODEL_PATH")
            # print(f"MODEL_PATH (before): {model_path}")

            # # 環境変数が設定されていない場合のみ、値を設定する
            # if model_path is None:
            #     os.environ["MODEL_PATH"] = "spleeter/pretrained_models"

            # model_path = os.environ.get("MODEL_PATH")
            # print(f"MODEL_PATH (after): {model_path}")

            # ここでは音源ファイルのpathが渡される
            filename = os.path.splitext(os.path.basename(input_path))[0]
            output_directory = os.path.join("data", "output", filename)
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

        except Exception as e:
            print("separateだよ")
            print(e)
