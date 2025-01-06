import webbrowser
import urllib.parse
import os

class Search:
    def __init__(self, browser=None):
        # Noneだとデフォルト
        self.browser = browser
        if browser:
            try:
                # 指定ブラウザのコントローラーを取得
                self.browser_controller = webbrowser.get(browser)
            except webbrowser.Error:
                print(f"ブラウザ '{browser}' が見つかりません。")
                print("システムのデフォルトブラウザを使用します。")
                self.browser_controller = None
        else:
            self.browser_controller = None

    def search_lyrics(self, filename):
        try:
            song_title = os.path.basename(filename)
            song_title = os.path.splitext(song_title)[0]
            query = urllib.parse.quote(f"{song_title} 歌詞")

            search_url = f"https://www.google.com/search?q={query}"

            if self.browser_controller:
                self.browser_controller.open_new_tab(search_url)
            else:
                webbrowser.open_new_tab(search_url)
                
            print(f"google検索: {query}")

        except Exception as e:
            print(f"エラーが発生しました: {e}")