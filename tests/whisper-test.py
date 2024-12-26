import whisper

# モデルの読み込み (モデルサイズは適宜変更してください)
model = whisper.load_model("base")

# 音声ファイルのパス
audio_file = (
    "tests/output/勘ぐれい/vocals.wav"  # Spleeter で分離したボーカルファイルのパス
)

# 音声認識の実行 (単語レベルのタイムスタンプを有効化)
result = model.transcribe(audio_file, word_timestamps=True, fp16=False)

# 結果の表示
# for segment in result["segments"]:
#     for word in segment["words"]:
#         print(f"[{word['start']:.2f} - {word['end']:.2f}] {word['text']}")

print(result)
