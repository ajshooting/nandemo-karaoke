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

## ToDo

- [x] 楽曲分離 -> spleeter
- [x] メロディ/ピッチ検出 -> YIN
- [ ] 歌詞認識/検索/同期 -> whisper/検索は権利的に△?
- [ ] 採点機能
- [ ] exe/app化 -> pyinstallerがうまくいかない
