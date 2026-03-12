# Stock Market Anomaly Detection

A machine learning system for detecting unusual market behaviour in daily equity price and volume data. The system identifies anomalous stock-days and market-wide stress periods using unsupervised clustering methods, without requiring labelled data or external news signals.

---

## Overview

Financial markets periodically exhibit extreme behaviour — large price swings, unusual trading volumes, or abnormally wide intraday ranges. This project builds a rule-based and clustering-based anomaly detection pipeline applied to a universe of nine NASDAQ-listed equities and the QQQ index ETF, covering the period from January 2018 through April 2020.

The test period (January to March 2020) deliberately spans the onset of the COVID-19 market crash, providing a rigorous real-world evaluation of the detection system.

---

## Project Structure

```
stock-market-anomaly-detection/
├── data/
│   ├── raw/                  # Original OHLCV CSV files from Kaggle
│   └── processed/            # Cleaned data, feature sets, train/val/test splits
├── notebooks/
│   ├── 01_eda.ipynb          # Exploratory data analysis and data loading
│   ├── 02_features.ipynb     # Feature engineering and train/val/test splits
│   └── 03_anomaly_detection.ipynb  # Model training, evaluation, and outputs
├── src/
│   ├── features.py           # Feature computation functions
│   ├── detector.py           # K-Means and DBSCAN detector classes
│   ├── query.py              # Date query command-line tool
│   └── report.py             # Monthly mini-report generator
├── outputs/
│   ├── csv/                  # Daily anomaly card and market-day table
│   └── plots/                # All generated visualisations
├── requirements.txt
└── README.md
```

---

## Dataset

**Source:** [NASDAQ Stock Market Dataset — Kaggle](https://www.kaggle.com/datasets/jacksoncrow/stock-market-dataset)

Daily OHLCV data (Open, High, Low, Close, Adjusted Close, Volume) for individual tickers. Data ends 1 April 2020. Returns are computed on Adjusted Close to account for splits and dividends.

**Ticker Universe:**

| Ticker | Company         |
|--------|-----------------|
| QQQ    | NASDAQ 100 ETF  |
| AAPL   | Apple           |
| MSFT   | Microsoft       |
| NVDA   | NVIDIA          |
| AMZN   | Amazon          |
| GOOGL  | Alphabet        |
| TSLA   | Tesla           |
| NFLX   | Netflix         |
| INTC   | Intel           |

---

## Methodology

### 1. Feature Engineering

Three leakage-safe features are computed per ticker per day using only past observations:

**Return Z-Score**
Standardised daily return relative to the rolling 63-day historical mean and standard deviation.

```
ret_z = (r_t - mean(r, t-63:t-1)) / std(r, t-63:t-1)
```

**Volume Z-Score**
Standardised log-volume relative to the rolling 21-day historical distribution.

```
vol_z = (log(V_t) - mean(log(V), t-21:t-1)) / std(log(V), t-21:t-1)
```

**Intraday Range Percentile**
The percentile rank of today's (High - Low) / Close relative to the past 63 trading days.

A warm-up period of 63 trading days is enforced before any day is scored, eliminating look-ahead bias.

### 2. Train / Validation / Test Split

| Split      | Period                        | Records |
|------------|-------------------------------|---------|
| Train      | April 2018 — December 2018   | 1,683   |
| Validation | January 2019 — December 2019 | 2,268   |
| Test       | January 2020 — April 2020    | 567     |

The StandardScaler is fit exclusively on the training set and applied to validation and test.

### 3. Rule-Based Detector (Baseline)

A point is flagged if any of the following thresholds are breached:

- `|ret_z| > 2.5` — extreme return, labelled crash (negative) or spike (positive)
- `vol_z > 2.5` — volume shock
- `range_pct > 95th percentile` — extreme intraday range

### 4. K-Means Clustering

K is selected by maximising the silhouette score on the training set (optimal K = 3). Per-cluster distance thresholds are set at the 97.5th percentile of training distances within each cluster. A test point is flagged as anomalous if its distance to the nearest centroid exceeds the corresponding cluster threshold.

### 5. DBSCAN Clustering

Epsilon is selected using the k-distance elbow method on the training set (eps = 1.5, min_samples = 10). Walk-forward scoring is applied: before each new block, DBSCAN is refit on an expanding window of past data using fixed hyperparameters. Points assigned label -1 (noise) are treated as anomalies.

### 6. Consensus

- **Union:** flagged by K-Means or DBSCAN — higher recall
- **Intersection:** flagged by both — higher precision

---

## Results

### Detection Performance on Test Set (Jan — Mar 2020)

| Detector          | Anomalies Flagged | Flag Rate |
|-------------------|-------------------|-----------|
| K-Means           | 25 / 567          | 4.41%     |
| DBSCAN            | 3 / 567           | 0.53%     |
| Union (consensus) | 25 / 567          | 4.41%     |

Flag rate is within the target range of 2 — 8%.

### Notable Detections

| Date       | Ticker | Type                        | Return   | ret_z  |
|------------|--------|-----------------------------|----------|--------|
| 2020-01-31 | AMZN   | spike + volume_shock        | +7.38%   | +7.01  |
| 2020-02-03 | TSLA   | spike + volume_shock        | +19.89%  | +6.73  |
| 2020-02-24 | QQQ    | crash + volume_shock        | -3.86%   | -4.94  |
| 2020-02-27 | MSFT   | crash + volume_shock        | -7.05%   | -5.32  |

28 market-wide anomalous days were identified in the test period, corresponding directly to the COVID-19 market stress of February and March 2020.

---

## Installation

**Requirements:** Python 3.10+

```bash
git clone https://github.com/YOUR_USERNAME/stock-market-anomaly-detection.git
cd stock-market-anomaly-detection

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

Place the raw ticker CSV files in `data/raw/` before running the notebooks.

---

## Usage

### Running the Notebooks

Execute the notebooks in order:

```
01_eda.ipynb              -> loads and validates raw data
02_features.ipynb         -> computes features and saves splits
03_anomaly_detection.ipynb -> trains models and generates outputs
```

### Date Query Tool

Query the anomaly status of any date in the dataset:

```bash
python src/query.py --date 2020-02-27
python src/query.py --date 2020-01-15
```

### Monthly Report

Generate a structured anomaly summary for any month:

```bash
python src/report.py --month 2020-02
python src/report.py --month 2020-01
```

---

## Output Files

| File                              | Description                                              |
|-----------------------------------|----------------------------------------------------------|
| `outputs/csv/daily_anomaly_card.csv`  | One row per anomalous stock-day with features and type  |
| `outputs/csv/market_day_table.csv`    | Daily market return, breadth, and anomaly flag          |
| `outputs/plots/05_kmeans_elbow.png`   | Elbow and silhouette curves for K selection             |
| `outputs/plots/06_dbscan_kdist.png`   | K-distance graph for DBSCAN eps selection               |
| `outputs/plots/07_anomalies_on_price.png` | Anomalies plotted on full price history             |

---

## Dependencies

```
pandas
numpy
scikit-learn
matplotlib
seaborn
jupyter
ipykernel
```

Install all dependencies via:

```bash
pip install -r requirements.txt
```

---

## Limitations

- The dataset ends April 2020. The system cannot be applied to more recent data without sourcing updated OHLCV files.
- DBSCAN walk-forward refitting is computationally expensive at scale. For larger universes, approximate nearest-neighbour methods should be considered.
- The rule-based baseline and clustering detectors are unsupervised and produce no probability estimates. Threshold selection involves judgement.
- This project is for educational purposes only and does not constitute investment advice.

---

## License

This project is released under the MIT License.

---

## Acknowledgements

- Dataset: [Jackson Crow — NASDAQ Stock Market Dataset](https://www.kaggle.com/datasets/jacksoncrow/stock-market-dataset)
- Project specification: Indian Institute of Technology Guwahati — Module III Capstone