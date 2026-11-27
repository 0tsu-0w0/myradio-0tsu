<h1 align="center">乙ラジオ</h1>

<p align="center"><b>毎朝、気になるニュースを 90 秒で。</b></p>

<p align="center">
  <a href="https://0tsu-0w0.github.io/myradio-0tsu/"><img src="https://img.shields.io/badge/%E2%96%B6%20ON%20AIR-%E4%B9%99%E3%83%A9%E3%82%B8%E3%82%AA-ffd028?style=for-the-badge&labelColor=ff4468" alt="乙ラジオを見る"></a>
</p>

キャラクターがニュースを読む、HTML の番組です。このリポジトリが、そのまま 1 つの局です。毎朝 9 時（日本時間）に放送します。日本語と英語があります。

- 放送ページ：https://0tsu-0w0.github.io/myradio-0tsu/
- 番組の中身は文字の台本（`episodes/`）で、音声はそれを読み上げたものです

## 中身

```
station.json         局の自己紹介（名前・放送の内容・ロゴ・クレジット）
index.html           プレーヤー
episodes.json        回の一覧
episodes/            台本（<日付>-ja.json / -en.json）
audio/               声（mp3。main にはコミットしない）
character/           キャスター（キャラの画像）
templates/           台本のひな形と、お手本の回
tools/voice.py       台本から声（VOICEVOX）とタイミングを作る
tools/publish.sh     GitHub Pages への公開（gh-pages ブランチ）
docs/formats.md      JSON の形
AGENTS.md            AI に局の運用を頼むときの説明
```

台本の作り方と公開の手順は [templates/README.md](templates/README.md) を見てください。

## クレジット・ライセンス

- このリポジトリは、[monoradio102/myradio](https://github.com/monoradio102/myradio) をもとにしています。プログラム（`index.html`、`tools/`）は MIT License（[LICENSE](LICENSE)）です
- お手本の台本（`templates/sample-episodes/`）：CC0
- キャラ（`character/`）：もとのリポジトリのキャラです。公序良俗に反しない使い方なら自由に使えます。AI で生成したキャラクターです
- 声：VOICEVOX:春日部つむぎ
- 天気：Open-Meteo（CC BY 4.0）
