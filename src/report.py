import pandas as pd
import numpy as np
import argparse
import os

ANOMALY_PATH = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'csv', 'daily_anomaly_card.csv')
MARKET_PATH  = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'market_features.csv')

def monthly_report(month_str):
    anomaly = pd.read_csv(ANOMALY_PATH, parse_dates=['Date'])
    market  = pd.read_csv(MARKET_PATH,  parse_dates=['Date'])

    try:
        month_dt = pd.to_datetime(month_str)
        year, month = month_dt.year, month_dt.month
    except Exception:
        print("❌ Invalid format. Use YYYY-MM")
        return

    # Filter to month
    mask_a = (anomaly['Date'].dt.year == year) & (anomaly['Date'].dt.month == month)
    mask_m = (market['Date'].dt.year  == year) & (market['Date'].dt.month  == month)
    
    month_anom = anomaly[mask_a].copy()
    month_mkt  = market[mask_m].copy()

    month_name = month_dt.strftime('%B %Y')
    
    print(f"\n{'='*70}")
    print(f"  📋 MONTHLY ANOMALY REPORT — {month_name}")
    print(f"{'='*70}")

    if month_mkt.empty:
        print(f"\n⚠️  No data for {month_name}")
        return

    # Market summary
    print(f"\n📊 MARKET SUMMARY")
    print(f"   Trading Days    : {len(month_mkt)}")
    print(f"   Anomalous Days  : {month_mkt['market_anomaly_flag'].sum()}")
    print(f"   Avg Market Ret  : {month_mkt['market_ret'].mean()*100:+.2f}%")
    print(f"   Avg Breadth     : {month_mkt['breadth'].mean()*100:.1f}%")
    print(f"   Worst Day       : {month_mkt.loc[month_mkt['market_ret'].idxmin(), 'Date'].strftime('%Y-%m-%d')} ({month_mkt['market_ret'].min()*100:+.2f}%)")
    print(f"   Best Day        : {month_mkt.loc[month_mkt['market_ret'].idxmax(), 'Date'].strftime('%Y-%m-%d')} ({month_mkt['market_ret'].max()*100:+.2f}%)")

    # Stock anomalies
    if month_anom.empty:
        print(f"\n✅ No stock anomalies detected in {month_name}")
    else:
        print(f"\n🚨 STOCK ANOMALIES ({len(month_anom)} total)")
        print(f"\n   {'Date':<12} {'Ticker':<8} {'Type':<30} {'ret':>8} {'ret_z':>8} {'vol_z':>8}")
        print(f"   {'-'*75}")
        for _, row in month_anom.sort_values('Date').iterrows():
            mkt_flag = "🌍" if month_mkt[month_mkt['Date']==row['Date']]['market_anomaly_flag'].values[0] == 1 else "  "
            print(f"   {str(row['Date'].date()):<12} {row['Ticker']:<8} {row['type']:<30} {row['ret']*100:>+7.2f}% {row['ret_z']:>7.2f} {row['vol_z']:>7.2f} {mkt_flag}")
        
        print(f"\n   🌍 = Market also anomalous on that day")
        
        # Top anomalies
        print(f"\n🔥 TOP 3 BIGGEST CRASHES:")
        crashes = month_anom[month_anom['type'].str.contains('crash')].nsmallest(3, 'ret')
        if crashes.empty:
            print("   None this month")
        else:
            for _, r in crashes.iterrows():
                print(f"   {r['Date'].date()} {r['Ticker']:>6}: {r['ret']*100:+.2f}% (ret_z={r['ret_z']:.2f})")

        print(f"\n🚀 TOP 3 BIGGEST SPIKES:")
        spikes = month_anom[month_anom['type'].str.contains('spike')].nlargest(3, 'ret')
        if spikes.empty:
            print("   None this month")
        else:
            for _, r in spikes.iterrows():
                print(f"   {r['Date'].date()} {r['Ticker']:>6}: {r['ret']*100:+.2f}% (ret_z={r['ret_z']:.2f})")

    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monthly Anomaly Report')
    parser.add_argument('--month', type=str, required=True, help='Month to report (YYYY-MM)')
    args = parser.parse_args()
    monthly_report(args.month)