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
2. **声を作る**：VOICEVOX（春日部つむぎ）で、台本の `say` を順に読み上げ、1 本の mp3 にする。`audio/<日付>-ja.mp3` に置く（git には入れない）。
3. **タイミングを書く**：声の長さに合わせて、台本の `seconds`、`lines_timed`（文ごとの `start`/`end`/`show`/`part`）、`segments`（opening / news / closing の区切り）を埋める。食い違うと字幕やスライドがずれる。形は [docs/formats.md](../docs/formats.md)。
4. **一覧に足す**：`episodes.json` の先頭に、その回を足す。
   `{"date": "<日付>", "ja": {"title": "…", "seconds": 90.0}, "en": {"title": "…", "seconds": 90.0}}`
5. **コミットして公開**：台本と `episodes.json` を main にコミットして push し、`tools/publish.sh` を実行する。

## メモ
- 声の利用規約（VOICEVOX:春日部つむぎ）に従い、クレジットは `station.json` に入っています。消さないでください。
- 英語版の声は、まだ決まっていません。
