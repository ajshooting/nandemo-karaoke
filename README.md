# nandemo-karaoke

任意の音源ファイルでカラオケできるアプリケーション。  
音源を音源分離、ピッチ解析、音声認識して、歌詞とピッチを同期して表示します。

python3.10想定です

```cli
python -m venv venv
pip install -r requirements.txt
python3 -m src.main
```

```cli
pip freeze > requirements.txt
```

## メモ

- 楽曲分離
- メロディ検出
- 歌詞認識/検索/同期
- ピッチ検出
- exe/app化できるの？ありえないくらい重くなりそう
