import pandas as pd
import numpy as np
import argparse
import os

# Paths
FEATURED_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'featured.csv')
MARKET_PATH   = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'market_features.csv')
ANOMALY_PATH  = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'csv', 'daily_anomaly_card.csv')

def load_data():
    featured = pd.read_csv(FEATURED_PATH, parse_dates=['Date'])
    market   = pd.read_csv(MARKET_PATH,   parse_dates=['Date'])
    anomaly  = pd.read_csv(ANOMALY_PATH,  parse_dates=['Date'])
    return featured, market, anomaly

def query_date(date_str):
    featured, market, anomaly = load_data()
    
    try:
        query_dt = pd.to_datetime(date_str)
    except Exception:
        print(f"❌ Invalid date format. Use YYYY-MM-DD")
        return

    print(f"\n{'='*60}")
    print(f"  📅 DATE QUERY: {query_dt.strftime('%B %d, %Y')}")
    print(f"{'='*60}")

    # Market status
    mkt_row = market[market['Date'] == query_dt]
    if mkt_row.empty:
        print(f"\n⚠️  No market data found for {date_str}")
        print("   (Could be a weekend, holiday, or outside dataset range)")
        return

    mkt = mkt_row.iloc[0]
    mkt_status = "🚨 ANOMALOUS" if mkt['market_anomaly_flag'] == 1 else "✅ NORMAL"
    
    print(f"\n📊 MARKET STATUS: {mkt_status}")
    print(f"   Market Return : {mkt['market_ret']*100:+.2f}%")
    print(f"   Breadth       : {mkt['breadth']*100:.1f}% stocks up")
    print(f"   Flag Rate     : {mkt['flag_rate']*100:.1f}% tickers anomalous")

    # Anomalous tickers
    day_anomalies = anomaly[anomaly['Date'] == query_dt]
    
    if day_anomalies.empty:
        print(f"\n✅ No anomalous tickers detected on this day.")
    else:
        print(f"\n🚨 ANOMALOUS TICKERS ({len(day_anomalies)} detected):")
        print(f"   {'Ticker':<8} {'Return':>8} {'ret_z':>8} {'vol_z':>8} {'Type'}")
        print(f"   {'-'*55}")
        for _, row in day_anomalies.iterrows():
            print(f"   {row['Ticker']:<8} {row['ret']*100:>+7.2f}% {row['ret_z']:>8.2f} {row['vol_z']:>8.2f}  {row['type']}")
    
    print(f"\n{'='*60}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stock Market Anomaly Date Query')
    parser.add_argument('--date', type=str, required=True, help='Date to query (YYYY-MM-DD)')
    args = parser.parse_args()
    query_date(args.date)