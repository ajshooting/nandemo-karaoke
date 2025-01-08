from youtube_search import YoutubeSearch
import yt_dlp


def download_top_youtube_audio(search_query):
    try:
        # YouTubeで検索
        results = YoutubeSearch(search_query, max_results=1).to_dict()

        if not results:
            print(f"「{search_query}」に一致する動画が見つかりませんでした。")
            return False

        video_url = "https://www.youtube.com" + results[0]["url_suffix"]
        video_title = results[0]["title"]

        print(f"「{video_title}」の音声をダウンロードします...")

        # yt-dlpのオプションを設定
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": "data/%(title)s.%(ext)s",
        }

        # 音声をダウンロード
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        print("ダウンロードが完了しました。")
        return True

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False


# 使用例
if __name__ == "__main__":
    search_query = "嘘じゃない"
    download_top_youtube_audio(search_query)
