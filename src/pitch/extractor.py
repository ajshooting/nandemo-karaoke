import librosa
import numpy as np
import os
import json


class PitchExtractor:
    def __init__(self, cache_dir="data/output"):
        self.cache_dir = cache_dir
        self.volume_threshold = 0.02  # 音量の閾値

    def _get_cache_file_path(self, audio_path):
        # ここでは分離後のpathが渡される
        parent_dir = os.path.dirname(audio_path)
        return os.path.join(parent_dir, "pitch.json")

    def extract_pitch(
        self,
        audio_path,
        sr=None,  # サンプリングレート(Noneだとlibrosaが自動で判断)
        hop_length=2048,  # 分析フレーム間のホップ長(大きいと時間分解能が低くなる)
        frame_length=2048,  # フレーム長(大きいと周波数分解能が低くなる)
        fmin=100,  # 検出する最小周波数
        fmax=1000,  # 検出する最大周波数
    ):

        # 出力は {start: 開始時間, end: 終了時間, pitch: MIDIノート番号} の辞書？

        cache_file_path = self._get_cache_file_path(audio_path)

        # キャッシュが存在するか確認
        if os.path.exists(cache_file_path):
            print(f"ピッチ解析結果のキャッシュが見つかりました: {cache_file_path}")
            try:
                with open(cache_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(
                    f"ピッチ解析結果キャッシュの読み込みに失敗しました。再実行します: {cache_file_path}"
                )
                # キャッシュが壊れている場合は再実行
                pass

        try:
            # 音声ファイルを読み込む
            y, sr = librosa.load(audio_path, sr=sr)

            # 短時間フーリエ変換 (STFT) を計算
            stft = np.abs(librosa.stft(y, hop_length=hop_length, n_fft=frame_length))

            # RMS (Root Mean Square) エネルギーを計算
            rms = librosa.feature.rms(
                S=stft, frame_length=frame_length, hop_length=hop_length
            )[0]

            # YINアルゴリズムでピッチを推定
            f0 = librosa.yin(
                y,
                fmin=fmin,
                fmax=fmax,
                sr=sr,
                hop_length=hop_length,
                frame_length=frame_length,
            )

            # 時間軸を作成
            times = librosa.times_like(f0, sr=sr, hop_length=hop_length)

            # MIDIノート番号に変換
            pitch_midi = [librosa.hz_to_midi(p) if p > 0 else 0 for p in f0]

            # 音量とピッチデータをフィルタリング
            pitch_data = []
            for i in range(len(times) - 1):
                if rms[i] > self.volume_threshold:  # 音量が閾値を超える場合のみ
                    pitch_data.append(
                        {
                            "start": times[i],
                            "end": times[i + 1],
                            "pitch": pitch_midi[i],
                        }
                    )

            # 単音化処理
            filtered_pitch_data = []
            if pitch_data:
                current_time = pitch_data[0]["start"]
                current_pitches = []
                for note in pitch_data:
                    if note["start"] == current_time:
                        current_pitches.append(note)
                    else:
                        if current_pitches:
                            # 最も音量が大きいピッチを選択
                            loudest_pitch = max(
                                current_pitches,
                                key=lambda x: rms[
                                    np.argmin(np.abs(times - x["start"]))
                                ],  # 対応する時刻のRMS値を取得
                            )
                            filtered_pitch_data.append(loudest_pitch)
                        current_time = note["start"]
                        current_pitches = [note]
                if current_pitches:
                    loudest_pitch = max(
                        current_pitches,
                        key=lambda x: rms[np.argmin(np.abs(times - x["start"]))],
                    )
                    filtered_pitch_data.append(loudest_pitch)

            # 音程が同じうちは伸ばす処理
            filtered_pitch_data2 = []
            if filtered_pitch_data:
                current_note = filtered_pitch_data[0]
                for i in range(1, len(filtered_pitch_data)):
                    if (
                        filtered_pitch_data[i]["pitch"] == current_note["pitch"]
                        and rms[
                            np.argmin(np.abs(times - filtered_pitch_data[i]["start"]))
                        ]
                        > self.volume_threshold
                    ):
                        current_note["end"] = filtered_pitch_data[i]["end"]
                    else:
                        filtered_pitch_data2.append(current_note)
                        current_note = filtered_pitch_data[i]
                filtered_pitch_data2.append(current_note)

            # 結果をキャッシュに保存
            try:
                with open(cache_file_path, "w", encoding="utf-8") as f:
                    json.dump(filtered_pitch_data2, f, ensure_ascii=False, indent=4)
                print(f"ピッチ解析結果をキャッシュに保存しました: {cache_file_path}")
            except Exception as e:
                print(f"ピッチ解析結果キャッシュの保存に失敗しました: {e}")

            return filtered_pitch_data2

        except Exception as e:
            print(f"ピッチ解析エラー: {e}")
            return []
