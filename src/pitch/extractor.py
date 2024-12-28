import librosa
import numpy as np

class PitchExtractor:
    def extract_pitch(self, audio_path, sr=None, hop_length=512):
        """
        音声ファイルから音程を抽出します。

        Args:
            audio_path (str): 音声ファイルのパス。
            sr (int, optional): サンプリングレート。Noneの場合、librosaが自動で判断します。
            hop_length (int, optional): 分析フレーム間のホップ長。デフォルトは512です。

        Returns:
            list: (時間[秒], 音程[Hz]) のタプルのリスト。
        """
        try:
            # 音声ファイルを読み込む
            y, sr = librosa.load(audio_path, sr=sr)

            # ピッチを推定 (YINアルゴリズムを使用)
            f0, voiced_flag, voiced_probs = librosa.pyin(y,
                                                           fmin=librosa.note_to_hz('C1'),
                                                           fmax=librosa.note_to_hz('B7'),
                                                           sr=sr,
                                                           hop_length=hop_length)

            # 時間軸を作成
            times = librosa.times_like(f0, sr=sr, hop_length=hop_length)

            # 音程データを作成 (非発声区間は無視)
            pitch_data = [(time, pitch) for time, pitch in zip(times, f0) if pitch > 0]

            return pitch_data

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return []
