# one-day-world

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/nmlyz/one-day-world/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/nmlyz/one-day-world/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A single-file Python program that draws a newspaper front page summing up the world news of Thursday 26 November 2026 — two more tankers hitting mines in the Strait of Hormuz, U.S. tariff proposals on 14 economies, Ukrainian strikes on two Russian refineries, a Gaza strike killing a Hamas security chief, the Cartagena hostage rescue, Pakistan's first astronaut aboard Shenzhou-24, a storm hitting Thanksgiving travel, and a deadly fuel-truck blaze in Egypt — as one 1024x1024 PNG, drawn entirely with code (a hand-made bitmap font and eight spot illustrations, no external assets) using only the Python standard library.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program writes `entry.png` to the output directory. It uses no network and is fully deterministic: every run produces the same bytes.
