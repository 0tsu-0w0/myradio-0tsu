#!/usr/bin/env python3
"""台本（episodes/<日付>-<言語>.json）から、VOICEVOX で声を作り、タイミングを書き込む。

  python tools/voice.py episodes/2026-11-27-ja.json

やること：
  1. opening → news[].lines → closing の順に、各文の "say" を VOICEVOX で読み上げる
  2. 無音をはさんで 1 本につなぎ、audio/<日付>-<言語>.mp3 に書く（mp3 にできないときは .wav）
  3. 台本の seconds・lines_timed・segments・made_at を、声に合わせて書き直す
  4. episodes.json に、その回の題と長さを入れる（同じ日付があれば上書き、新しい順に並べる）

VOICEVOX（エンジン）を起動しておくこと。既定は http://127.0.0.1:50021、春日部つむぎ ノーマル（話者 8）。
mp3 にするには、ffmpeg（PATH に置くか --ffmpeg で指定）か、Python の lameenc が要る。
標準ライブラリだけで動く（mp3 の変換を除く）。
"""
import argparse
import datetime
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 無音の長さ（秒）。お手本の局（ものラジオ）の回に合わせてある
LEAD = 0.6        # 最初の文の前
GAP_LINE = 0.25   # 同じパートの文と文の間
GAP_PART = 1.05   # パート（オープニング・ニュースごと・締め）の間
TAIL = 2.05       # 最後の文のあと


def post(host, path, params, body=None, timeout=120):
    url = f"{host}{path}?{urllib.parse.urlencode(params)}"
    data = json.dumps(body).encode("utf-8") if body is not None else b""
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def synth(host, speaker, text, speed):
    """1 文を読み上げて、(サンプリング周波数, PCM のバイト列) を返す。前後の無音はこちらで足すので 0 にする"""
    q = json.loads(post(host, "/audio_query", {"text": text, "speaker": speaker}))
    q["speedScale"] = speed
    q["prePhonemeLength"] = 0.0
    q["postPhonemeLength"] = 0.0
    q["outputStereo"] = False
    wav = post(host, "/synthesis", {"speaker": speaker}, q)
    with wave.open(io.BytesIO(wav)) as w:
        if w.getnchannels() != 1 or w.getsampwidth() != 2:
            sys.exit(f"想定外の音声の形です（{w.getnchannels()}ch, {w.getsampwidth() * 8}bit）")
        return w.getframerate(), w.readframes(w.getnframes())


def parts_of(ep):
    """[(kind, index, [文…]), …]：opening、news ごと、closing"""
    parts = [("opening", None, ep.get("opening", []))]
    parts += [("news", i, n.get("lines", [])) for i, n in enumerate(ep.get("news", []))]
    parts.append(("closing", None, ep.get("closing", [])))
    return [p for p in parts if p[2]]


def to_mp3(wav_path, mp3_path, ffmpeg):
    exe = ffmpeg or shutil.which("ffmpeg")
    if exe:
        subprocess.run([exe, "-y", "-loglevel", "error", "-i", wav_path,
                        "-codec:a", "libmp3lame", "-b:a", "96k", mp3_path], check=True)
        return True
    try:
        import lameenc
    except ImportError:
        return False
    with wave.open(wav_path) as w:
        enc = lameenc.Encoder()
        enc.set_bit_rate(96)
        enc.set_in_sample_rate(w.getframerate())
        enc.set_channels(1)
        enc.set_quality(2)
        data = enc.encode(w.readframes(w.getnframes())) + enc.flush()
    with open(mp3_path, "wb") as f:
        f.write(data)
    return True


def update_list(ep, lang, single):
    """episodes.json に、その回の題と長さを入れる"""
    path = os.path.join(ROOT, "episodes.json")
    items = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []
    entry = next((e for e in items if e.get("date") == ep["date"]), None)
    if entry is None:
        entry = {"date": ep["date"]}
        items.append(entry)
    info = {"title": ep["title"], "seconds": ep["seconds"]}
    if single:
        entry.update(info)
    else:
        entry[lang] = info
    items.sort(key=lambda e: e["date"], reverse=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(items, f, ensure_ascii=False)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode", help="台本の JSON（episodes/<日付>-<言語>.json）")
    ap.add_argument("--host", default=os.environ.get("VOICEVOX_HOST", "http://127.0.0.1:50021"))
    ap.add_argument("--speaker", type=int, default=int(os.environ.get("VOICEVOX_SPEAKER", "8")),
                    help="VOICEVOX の話者 ID（既定 8：春日部つむぎ ノーマル）")
    ap.add_argument("--speed", type=float, default=1.0, help="話す速さ（既定 1.0）")
    ap.add_argument("--ffmpeg", help="ffmpeg の場所（PATH になければ）")
    ap.add_argument("--no-list", action="store_true", help="episodes.json を書き換えない")
    a = ap.parse_args()

    path = os.path.abspath(a.episode)
    ep = json.load(open(path, encoding="utf-8"))
    for k in ("date", "title"):
        if not ep.get(k) or "YYYY" in str(ep[k]) or "【" in str(ep[k]):
            sys.exit(f"台本の {k} がまだ埋まっていません：{ep.get(k)!r}")
    base = os.path.splitext(os.path.basename(path))[0]          # 2026-11-27-ja（1 言語の局なら 2026-11-27）
    lang = ep.get("lang") or (base[11:] if len(base) > 10 else None)
    single = len(base) == 10

    try:
        urllib.request.urlopen(f"{a.host}/version", timeout=5).read()
    except Exception as e:
        sys.exit(f"VOICEVOX に繋がりません（{a.host}）。エンジンを起動してください：{e}")

    rate, pcm = None, bytearray()
    lines_timed, segments = [], []
    t = LEAD
    parts = parts_of(ep)

    def silence(sec):
        pcm.extend(b"\0\0" * int(round(sec * rate)))

    for pi, (kind, index, lines) in enumerate(parts):
        if pi > 0:
            t += GAP_PART
        seg = {"kind": kind, "index": index, "start": round(t, 3), "end": None}
        for li, line in enumerate(lines):
            say, show = line.get("say", ""), line.get("show", line.get("say", ""))
            if not say or "【" in say:
                sys.exit(f"まだ埋まっていない文があります（{kind} {'' if index is None else index}）：{say!r}")
            if li > 0:
                t += GAP_LINE
            r, clip = synth(a.host, a.speaker, say, a.speed)
            if rate is None:
                rate = r
                silence(LEAD)
            elif r != rate:
                sys.exit("文ごとにサンプリング周波数が違います")
            # 区切りの無音をここで足す（pcm の長さと t をそろえる）
            want = int(round(t * rate)) * 2
            if len(pcm) < want:
                pcm.extend(b"\0" * (want - len(pcm)))
            pcm.extend(clip)
            dur = len(clip) / 2 / rate
            lines_timed.append({"start": round(t, 3), "end": round(t + dur, 3), "show": show, "part": pi})
            t += dur
            print(f"  {pi}:{li}  {t:7.2f}s  {show[:40]}")
        segments.append(seg)

    t += TAIL
    want = int(round(t * rate)) * 2
    pcm.extend(b"\0" * (want - len(pcm)))
    total = len(pcm) / 2 / rate
    for i, s in enumerate(segments):
        s["end"] = segments[i + 1]["start"] if i + 1 < len(segments) else round(total, 3)

    # 書き出し
    audio_dir = os.path.join(ROOT, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    mp3 = os.path.join(audio_dir, base + ".mp3")
    with tempfile.TemporaryDirectory() as td:
        wav_path = os.path.join(td, base + ".wav")
        with wave.open(wav_path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(bytes(pcm))
        if to_mp3(wav_path, mp3, a.ffmpeg):
            out = mp3
        else:
            out = os.path.join(audio_dir, base + ".wav")
            shutil.copy(wav_path, out)
            print("※ mp3 にできませんでした（ffmpeg も lameenc もない）。wav で書きました。"
                  "放送には mp3 が要るので、ffmpeg を入れてからもう一度実行してください", file=sys.stderr)

    ep["seconds"] = round(total, 2)
    ep["lines_timed"] = lines_timed
    ep["segments"] = segments
    ep["made_at"] = datetime.datetime.now().replace(microsecond=0).isoformat()
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ep, f, ensure_ascii=False, indent=1)
        f.write("\n")
    if not a.no_list:
        update_list(ep, lang, single)

    print(f"声：{os.path.relpath(out, ROOT)}（{total:.2f} 秒）")
    print(f"台本：{os.path.relpath(path, ROOT)} に lines_timed {len(lines_timed)} 文・segments {len(segments)} を書きました")
    if not a.no_list:
        print("一覧：episodes.json を更新しました")


if __name__ == "__main__":
    main()
