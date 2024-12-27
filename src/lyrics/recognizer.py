import whisper


class Recognizer:
    def __init__(self, model_size="base", language="ja"):
        self.model_size = model_size
        self.language = language
        self.model = whisper.load_model(self.model_size)

    def recognize_lyrics(self, audio_path):
        try:
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
