# one-day-world

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/nmlyz/one-day-world/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/nmlyz/one-day-world/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A program that draws Thursday 26 November 2026's world news as a single newspaper front page: eight stories, from the tankers hit by mines in the Strait of Hormuz to the Thanksgiving storm on the US East Coast, laid out as a broadsheet with a lead story, hand-drawn spot illustrations and three fact lines per story. Each story names its numbers: 2 tankers, 20% and 35%, 800 km and 5 jets, 16 hours, 08:18, 81.5 million, 30 killed.

## How it works

`main.py` uses only the Python standard library. It draws every letter with a small built-in bitmap face and encodes the PNG by hand (zlib), so it runs offline with nothing installed. The output is a 1024×1024 PNG at `entry.png`, and running it twice writes byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## The day in the picture

- Strait of Hormuz: two tankers hit mines, Iran's claim noted as unconfirmed
- Washington: USTR proposes tariffs on 14 economies
- Ukraine: drones hit two refineries and five jets
- Gaza: strike kills a Hamas security chief
- Cartagena: all hostages freed after a 16-hour siege
- China: Shenzhou-24 carries Pakistan's first astronaut to Tiangong
- United States: a storm hits Thanksgiving travel
- Egypt: a fuel-truck fire kills 30 in Giza

---

<sub>Entered on [make.fun](https://make.fun/?ref=23ae7fx0&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · A one-day newspaper drawn in code</sub>
