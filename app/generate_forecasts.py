"""Build reproducible synthetic forecast records; Excel authoring is separate."""
from pathlib import Path
import json
import pandas as pd
from analyze import load_data

def generate(path):
    reg,b,a=load_data(path)
    result=[]
    for quarter,cutoff in [(1,3),(2,6),(3,9)]:
        asof=pd.Timestamp(2026,cutoff,1)+pd.offsets.MonthEnd(0)
        known=a[a['Posting Month'].dt.month<=cutoff].copy()
        # Only information posted on or before the snapshot is available.
        for bid,plan in b.groupby('Budget ID',sort=True):
            hist=known[known['Budget ID']==bid]
            recent=hist[hist['Posting Month'].dt.month>cutoff-3]
            planned_recent=plan[plan['Month'].dt.month.between(cutoff-2,cutoff)]['Budget Units'].sum()
            observed_units=recent['Units'].sum()
            usage_ratio=max(0,min(1.6,observed_units/planned_recent)) if planned_recent else 1
            positive=recent[recent['Units']>0]
            observed_rate=positive['Amount USD'].sum()/positive['Units'].sum() if len(positive) else plan['Unit Rate USD'].iloc[0]
            n=int(bid[-4:]);blend={1:.35,2:.60,3:.85}[quarter]
            # Independent synthetic planning assumptions; never reference future actuals or answer key.
            usage_factor=(1-blend)+blend*usage_ratio
            planning_change=((n%9)-4)*.012
            rate_factor=1+((n%7)-3)*.008
            vendor=plan['Planned Vendor'].iloc[0]
            if len(positive): vendor=positive.groupby('Actual Vendor')['Amount USD'].sum().idxmax()
            for _,r in plan.iterrows():
                m=r['Month'].month;locked=m<=cutoff
                if locked:
                    posted=hist[hist['Posting Month'].dt.month==m]
                    units=round(posted['Units'].sum(),4);amount=round(posted['Amount USD'].sum(),2)
                    rate=round(amount/units,6) if units else 0
                    note='Closed actual postings through snapshot date; expense amount is authoritative.'
                    row_vendor='Multiple actual vendors' if posted['Actual Vendor'].nunique()>1 else (posted['Actual Vendor'].iloc[0] if len(posted) else r['Planned Vendor'])
                else:
                    if r['Budget Units']>0:
                        units=round(r['Budget Units']*max(0,usage_factor+planning_change))
                        if hist.empty: units=round(r['Budget Units']*{1:.35,2:.1,3:0}[quarter])
                        rate=round(((1-blend)*r['Unit Rate USD']+blend*observed_rate)*rate_factor,2)
                        note='Estimate from recent posted usage and rates, blended with seasonal plan and synthetic planning adjustment.'
                    else:
                        start=8+(n%3)
                        units=(round(observed_units/3) if observed_units>0 else (18+n%45)) if m>=start else 0
                        rate=round(observed_rate*rate_factor,2)
                        note=f'Synthetic new commitment expected from month {start:02}; no original budget.'
                    amount=round(units*rate,2);row_vendor=vendor
                result.append({'Scenario ID':f'FQ{quarter}','Scenario':f'Q{quarter} forecast','As Of Date':asof.strftime('%Y-%m-%d'),'Actual Through Month':cutoff,'Month':r['Month'].strftime('%Y-%m-%d'),'Year':2026,'Month Number':m,'Budget ID':bid,**{c:r[c] for c in ['Cost Center ID','Cost Center Name','Account ID','Account Name','Account Group ID','Account Group']},'Planned Vendor':row_vendor,'Period Type':'Closed actual' if locked else 'Estimate','Forecast Units':units,'Unit Rate USD':rate,'Forecast USD':amount,'Currency':'USD','Assumption':note})
    return result

if __name__=='__main__':
    rows=generate(Path(__file__).with_name('Synthetic_FPA_2026_Grouped.xlsx'))
    output=Path(__file__).with_name('forecast_data.json')
    output.write_text(json.dumps(rows),encoding='utf-8')
    print(f'Generated {len(rows)} forecast rows across three snapshots.')
