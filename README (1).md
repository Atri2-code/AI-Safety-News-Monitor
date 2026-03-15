# AI Safety Media & Parliamentary Tracker

Two Python tools built specifically to support the work of an AI safety
media relations team — monitoring news coverage and tracking parliamentary
discourse on superintelligence risk.

---

## Projects

### 1. AI Safety News Monitor (`1_news_monitor/monitor.py`)

Aggregates and categorises daily AI safety news from 10+ sources into a
structured digest — directly mirroring the "daily news roundups" requirement
of a media relations role at an AI safety organisation.

**Sources covered:**
MIT Technology Review · The Guardian · Wired · BBC Technology · TechCrunch ·
VentureBeat · Future of Life Institute · 80,000 Hours · AI Alignment Forum

**Categories:**
- Superintelligence & Existential Risk
- AI Regulation & Policy
- AI Capabilities & Research
- Industry & Companies
- Ethics & Society

**Outputs:** `output/digest_YYYY-MM-DD.txt` + structured JSON

```bash
pip install feedparser
python 1_news_monitor/monitor.py
```

---

### 2. Parliamentary AI Coverage Tracker (`2_parliamentary_tracker/tracker.py`)

Analyses UK parliamentary Hansard debate data to track how often MPs mention
AI, superintelligence, and related terms — and whether that discourse is
accelerating over time.

Directly mirrors ControlAI's UK legislative engagement work, having briefed
150+ parliamentarians since September 2024.

**Tracks:**
- Monthly AI mention frequency (trend line)
- Top 15 MPs by AI mention count
- AI term frequency breakdown
- Party distribution of AI discourse
- Year-on-year growth in parliamentary AI coverage

**Data source:** Official UK Parliament Hansard API (free, no key required)

**Outputs:** Interactive Plotly dashboard + CSV + JSON summary

```bash
pip install plotly requests pandas
python 2_parliamentary_tracker/tracker.py
open output/parliamentary_tracker.html
```

---

## Relevance to AI Safety Media Work

| Tool | JD requirement it addresses |
|---|---|
| News Monitor | "Produce daily news roundups to keep the entire team at the forefront of AI news developments" |
| Parliamentary Tracker | "Spotting opportunities where ControlAI can contribute to news cycles" |
| Both | "Highly reactive and adaptive to ongoing AI developments and media events" |

---

## Dependencies

```
feedparser>=6.0.0
requests>=2.28.0
pandas>=2.0.0
plotly>=5.0.0
```

---

## Author

Atrija Haldar
[LinkedIn](https://www.linkedin.com/in/atrija-haldar-196a3b221/)
MSc Engineering, Technology and Business Management — University of Leeds
