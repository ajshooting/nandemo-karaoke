import whisper
import os
import json
import time


class Recognizer:
    def __init__(self, model_size="base", language="ja", cache_dir="data/output"):
        self.model_size = model_size
        self.language = language
        self.model = whisper.load_model(self.model_size)
        self.cache_dir = cache_dir
        # os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_file_path(self, audio_path):
        # ここでは音源ファイルのpathが渡される
        music_name = os.path.basename(os.path.dirname(audio_path))
        output_directory = os.path.join("data", "output", music_name)
        return os.path.join(output_directory, "recognized.json")

    def recognize_lyrics(self, audio_path):
        cache_file_path = self._get_cache_file_path(audio_path)

        # キャッシュが存在するか確認
        if os.path.exists(cache_file_path):
            print(f"音声認識結果のキャッシュが見つかりました: {cache_file_path}")
            try:
                with open(cache_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(
                    f"音声認識結果キャッシュの読み込みに失敗しました。再実行します: {cache_file_path}"
                )
                # キャッシュが壊れている場合は再実行
                pass

        try:
            print(f"音声認識を実行します: {audio_path}")

            start_time = time.time()

            # 音声認識の実行 (単語レベルのタイムスタンプを有効化)
            result = self.model.transcribe(
                audio_path, word_timestamps=True, fp16=False, language=self.language
            )

            # 結果を整形して返す (単語、開始時間、終了時間)
            formatted_result = []
            for segment in result["segments"]:
                formatted_result.append(
                    {
                        "text": segment["text"].strip(),
                        "start": segment["start"],
                        "end": segment["end"],
                        "words": [
                            {
                                "word": word["word"].strip(),
                                "start": word["start"],
                                "end": word["end"],
                            }
                            for word in segment["words"]
                        ],
                    }
                )

            # 結果をキャッシュに保存
            try:
                with open(cache_file_path, "w", encoding="utf-8") as f:
                    json.dump(formatted_result, f, ensure_ascii=False, indent=4)
                print(f"音声認識結果を保存しました: {cache_file_path}")
            except Exception as e:
                print(f"音声認識結果キャッシュの保存に失敗しました: {e}")

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"音声認識処理時間: {elapsed_time:.2f}秒")

            return formatted_result

        except FileNotFoundError as e:
            print(f"音声ファイルが見つかりません: {audio_path}")
            print(e)
            return None
        except Exception as e:
            print(f"音声認識エラー: {e}")
            return None
