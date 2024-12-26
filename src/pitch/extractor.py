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

if __name__ == '__main__':
    # サンプルの音声ファイルパス (適宜変更してください)
    audio_file = 'sample.wav'

    # PitchExtractorのインスタンスを作成
    extractor = PitchExtractor()

    # 音程を抽出
    pitch_data = extractor.extract_pitch(audio_file)

    # 抽出された音程データを表示 (最初の10個)
    if pitch_data:
        print("抽出された音程データ (時間[秒], 音程[Hz]):")
        for time, pitch in pitch_data[:10]:
            print(f"{time:.3f}, {pitch:.2f}")
    else:
        print("音程データを抽出できませんでした。")