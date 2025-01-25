from youtube_search import YoutubeSearch
import yt_dlp
import os, re


def sanitize_filename(filename):
    # macOS/Linux
    filename = filename.replace("/", "_").replace("\0", "_")
    # Windows
    filename = re.sub(r'[\\:*\?"<>|]', "_", filename)
    return filename


class Downloader:
    def __init__(self):
        pass

    def download_music(self, query):
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()

            if not results:
                print(f"見つかりませんでした: {query}")
                return

            video_url = "https://youtube.com" + results[0]["url_suffix"]
            video_title = sanitize_filename(results[0]["title"])

            output_dir = os.path.join("data", "output", video_title)
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "music")

            if os.path.exists(output_file + ".mp3"):
                print(f"ダウンロード済みのファイルが存在します: {output_file}")
                return output_file + ".mp3"

            print(f"'{video_title}' のダウンロードを開始します")

            ydl_ops = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "outtmpl": output_file,
            }

            with yt_dlp.YoutubeDL(ydl_ops) as ydl:
                ydl.download([video_url])

            print(f"'{video_title}' のダウンロードが完了")

            # yt_dlpでmp3がくっついちゃうのかな..?
            return output_file + ".mp3"

        except Exception as e:
            print(f"ダウンロードエラー: {e}")
