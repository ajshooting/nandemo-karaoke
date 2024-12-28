# nandemo-karaoke

なんでもカラオケ！

do this to execute this program

```cli
python3 -m src.main
```

to install package

```cli
pip install -r requirements.txt
```

to generate requirements.txt

```cli
pip freeze > requirements.txt
```

なにこれ興味ある

```cli
# ターミナルでプロファイリングを実行
python -m cProfile -o profile.out main_window.py 
# (main_window.py はあなたのアプリケーションのメインファイル)

# snakeviz を使ってプロファイル結果を可視化
snakeviz profile.out
```

## メモ

- 楽曲分離
- メロディ検出
- 歌詞認識/検索/同期
- ピッチ検出
- exe/app化できるの？ありえないくらい重くなりそう
