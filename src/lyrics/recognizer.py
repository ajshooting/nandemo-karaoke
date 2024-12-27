import whisper
import os
import json


class Recognizer:
    def __init__(
        self, model_size="base", language="ja", cache_dir="data/output"
    ):
        self.model_size = model_size
        self.language = language
        self.model = whisper.load_model(self.model_size)
        self.cache_dir = cache_dir
        # os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_file_path(self, audio_path):
        filename_without_ext = os.path.splitext(os.path.basename(audio_path))[0]
        return os.path.join(f"{self.cache_dir}/{filename_without_ext}", "recognized.json")

    def recognize_lyrics(self, audio_path):
        cache_file_path = self._get_cache_file_path(audio_path)

        # キャッシュファイルが存在するか確認
        if os.path.exists(cache_file_path):
            print(f"認識結果のキャッシュが見つかりました: {cache_file_path}")
            try:
                with open(cache_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(
                    f"キャッシュファイルの読み込みに失敗しました。再実行します: {cache_file_path}"
                )
                # キャッシュが壊れている場合は再実行
                pass

        try:
            print(f"音声認識を実行します: {audio_path}")
            # 音声認識の実行 (単語レベルのタイムスタンプを有効化)
            result = self.model.transcribe(
                audio_path, word_timestamps=True, fp16=False, language=self.language
            )

            # 結果を整形して返す (例: 単語、開始時間、終了時間のリスト)
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
                print(f"認識結果をキャッシュに保存しました: {cache_file_path}")
            except Exception as e:
                print(f"キャッシュファイルへの保存に失敗しました: {e}")

            return formatted_result

        except FileNotFoundError:
            print(f"エラー：音声ファイルが見つかりません: {audio_path}")
            return None
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return None


# if __name__ == '__main__':
#     # サンプルの音声ファイルパス (適宜変更してください)
#     audio_file = 'sample.wav'

#     # Recognizerのインスタンスを作成
#     recognizer = Recognizer()

#     # 歌詞認識を実行
#     lyrics_data = recognizer.recognize_lyrics(audio_file)

#     # 認識結果を表示
#     if lyrics_data:
#         print("認識された歌詞データ (単語, 開始時間, 終了時間):")
#         for item in lyrics_data:
#             print(f"{item['word']}, {item['start']:.2f}, {item['end']:.2f}")
#     else:
#         print("歌詞を認識できませんでした。")
