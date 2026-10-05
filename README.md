# Newcastle United 2025/26 — Post-Goal Control Analysis

An event-level football analytics project investigating how Newcastle United
gain, maintain and lose control after scoring.

## Interactive Dashboard

### ⚽ [Open the Live Interactive Dashboard](https://newcastle-united-performance-analysis.streamlit.app/)
### 📄 [Read the One-Page Executive Summary](Newcastle_United_Analytics_Executive_Summary.pdf)
### 📊 [Read the Full 14-Page Analytics Report](Newcastle_United_Complete_Analytics_Report_FIXED.docx)

## Research Question

What allows Newcastle United to retain control after scoring, and why does
that control weaken in other game states — particularly away from home?

## Dataset

- 38 Premier League matches
- 962 shots
- 108 goal events
- 5, 10 and 15-minute post-goal windows
- Shot location, xG, xGOT and shot outcome
- Territorial pressure
- Player and unit combinations

## Key Findings

### 1. Shot quality matters more than simply increasing volume
In the 15 minutes after scoring, Newcastle produced a +0.160 xG differential
and +0.190 SOT differential.

### 2. Post-goal control deteriorates away from home
Post-Goal Control Index:
- Home: 55.6
- Away: 45.8

### 3. Territorial pressure is the clearest tactical mechanism
Positive-pressure post-score periods produced a PGCI of 62.4 compared with
32.9 when Newcastle were pushed into negative territory.

### 4. Player combinations provide video-review targets
The Miley–Tonali combination recorded a PGCI of 80.3 across eight qualifying
windows. This is treated as an association for further tactical investigation,
not evidence of causation.

## Methodology

The analysis combines match-level and event-level data to study shots,
shots on target, xG, shot locations, score state, venue, territorial pressure
and player combinations.

PGCI (Post-Goal Control Index) combines Newcastle's share of shots, shots on
target and xG. A score of 50 represents even control.

Results are treated as descriptive associations rather than causal effects.

## Tools

Python · pandas · NumPy · scikit-learn · Plotly · Streamlit

## Explore the Project

**Interactive dashboard:**  
https://newcastle-united-performance-analysis.streamlit.app/
