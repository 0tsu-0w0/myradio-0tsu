# templates/

放送には使われない、作業用のひな形です。

| ファイル | 中身 |
|---|---|
| `episode-ja.json` / `episode-en.json` | 空の台本。【 】や `YYYY-MM-DD` を埋めて使う |
| `sample-episodes/` | お手本の回（ものラジオの台本、CC0）と、その `episodes.json`。形の参考用 |

## 1 回分を手動で作る手順

1. **台本を書く**：`episode-ja.json` を `episodes/<日付>-ja.json` にコピーして埋める（英語は `-en`）。
   - `say` は読み上げ用（英字・数字は読みをカタカナやひらがなに）、`show` は字幕用（ふつうの表記）。
   - ニュースごとに出典 `url` を必ず付ける。事実は出典に書いてあることだけ。
   - リンクカードの `image` は、記事のサイトが出している OGP 画像の URL を書くだけにする（画像は保存しない）。
2. **声とタイミングを作る**：VOICEVOX を起動して、次を実行する。

   ```
   python tools/voice.py episodes/<日付>-ja.json
   ```

   - 春日部つむぎ（話者 8）で `say` を順に読み上げ、`audio/<日付>-ja.mp3` を作る（git には入れない）
   - 台本の `seconds`・`lines_timed`・`segments`・`made_at` を、声に合わせて書き直す
   - `episodes.json` に、その回の題と長さを入れる
   - mp3 にするには ffmpeg（または `pip install lameenc`）が要る。ないときは wav で書く
   - 話す速さは `--speed 1.1` など。台本を直したら、もう一度実行すればよい
3. **コミットして公開**：台本と `episodes.json` を main にコミットして push し、`tools/publish.sh` を実行する。

## メモ
- 声の利用規約（VOICEVOX:春日部つむぎ）に従い、クレジットは `station.json` に入っています。消さないでください。
- 英語版の声は、まだ決まっていません。
