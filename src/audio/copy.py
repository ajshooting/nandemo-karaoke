import os
import shutil
from pydub import AudioSegment


class Copy:
    def __init__(self):
        pass

    def copy_music(self, input_path):
        try:
            filename, ext = os.path.splitext(os.path.basename(input_path))
            output_dir = os.path.join("data", "output", filename)
            os.makedirs(output_dir, exist_ok=True)

            output_path = os.path.join(output_dir, "music.mp3")

            if os.path.exists(output_path):
                print(f"コピー済みのファイルが存在: {output_path}")
            else:
                if ext.lower() == "mp3":
                    shutil.copy2(input_path, output_path)
                else:
                    try:
                        sound = AudioSegment.from_file(input_path)
                        sound.export(output_path, format="mp3")
                    except Exception as e:
                        print(f"変換エラー(copy.py): {e}")
                        return None
                print(f"ファイルをコピーしました: {input_path}, {output_path}")
            return output_path

        except Exception as e:
            print(f"コピーエラー: {e}")
