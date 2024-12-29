import whisper
import os
import json


class Recognizer:
    def __init__(self, model_size="base", language="ja", cache_dir="data/output"):
        self.model_size = model_size
        self.language = language
        self.model = whisper.load_model(self.model_size)
        self.cache_dir = cache_dir
        # os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_file_path(self, audio_path):
        parent_dir = os.path.dirname(audio_path)
        return os.path.join(parent_dir, "recognized.json")

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

            return formatted_result

        except FileNotFoundError:
            print(f"音声ファイルが見つかりません: {audio_path}")
            return None
        except Exception as e:
            print(f"音声認識エラー: {e}")
            return None
