"""Offline FP&A variance analysis. Run: python analyze.py workbook.xlsx --open."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import webbrowser
import pandas as pd
import numpy as np

DIM = ['Budget ID', 'Cost Center ID', 'Cost Center Name', 'Account ID', 'Account Name', 'Account Group ID', 'Account Group']
METRICS = ['actual', 'budget', 'variance', 'service_actual', 'volume', 'rate_mix', 'unbudgeted', 'timing']

def load_data(path):
    """Read only the three source tables; never read the scenario answer key."""
    frames = {n: pd.read_excel(path, sheet_name=n, dtype={'Budget ID':str, 'Cost Center ID':str, 'Account ID':str, 'Account Group ID':str}) for n in ['Budget ID Register','Budget','Actuals']}
    reg, budget, actual = [frames[n] for n in frames]
    required = {'Budget ID Register':DIM+['Planned Vendor'], 'Budget':DIM+['Month','Budget USD','Budget Units','Unit Rate USD','Planned Vendor'], 'Actuals':DIM+['Transaction ID','Posting Date','Posting Month','Service Month','Actual Vendor','Transaction Type','Units','Unit Rate USD','Amount USD','Description']}
    for n, df in frames.items():
        missing = set(required[n])-set(df.columns)
        if missing: raise ValueError(f'{n}: missing columns {sorted(missing)}')
        if df[DIM].isna().any().any(): raise ValueError(f'{n}: blank dimension or Budget ID')
        for c in ['Cost Center ID','Account ID']: df[c]=df[c].str.zfill(2)
    if reg['Budget ID'].duplicated().any(): raise ValueError('Register contains duplicate Budget IDs')
    if not reg['Budget ID'].str.fullmatch(r'\d{2}-26-\d{2}-\d{4}').all(): raise ValueError('Budget IDs must follow CC-26-AA-0000')
    if not ((reg['Budget ID'].str[:2]==reg['Cost Center ID']) & (reg['Budget ID'].str[6:8]==reg['Account ID'])).all(): raise ValueError('Budget ID segments disagree with dimensions')
    if reg.groupby('Account ID')['Account Group ID'].nunique().max()!=1: raise ValueError('An account has multiple groups')
    if reg.groupby('Account Group ID')['Account Group'].nunique().max()!=1: raise ValueError('A group ID has multiple names')
    for df, cols in [(budget,['Budget USD','Budget Units','Unit Rate USD']),(actual,['Amount USD','Units','Unit Rate USD'])]:
        for c in cols:
            df[c]=pd.to_numeric(df[c],errors='raise')
            if not np.isfinite(df[c]).all(): raise ValueError(f'Invalid or missing numeric values in {c}')
    for df,col in [(budget,'Month'),(actual,'Posting Month'),(actual,'Service Month'),(actual,'Posting Date')]:
        df[col]=pd.to_datetime(df[col],errors='raise')
        if df[col].isna().any() or not df[col].dt.year.eq(2026).all(): raise ValueError(f'{col}: expected valid 2026 dates')
        if col!='Posting Date' and not df[col].dt.day.eq(1).all(): raise ValueError(f'{col}: expected first day of month')
    if not actual['Posting Date'].dt.to_period('M').eq(actual['Posting Month'].dt.to_period('M')).all(): raise ValueError('Posting Date disagrees with Posting Month')
    for name,df in [('Budget',budget),('Actuals',actual)]:
        check=df.merge(reg[DIM],on='Budget ID',how='left',suffixes=('','_register'),indicator=True,validate='many_to_one')
        if not check['_merge'].eq('both').all(): raise ValueError(f'{name}: unknown Budget IDs')
        for c in DIM[1:]:
            if not check[c].eq(check[c+'_register']).all(): raise ValueError(f'{name}: inconsistent {c}')
        if 'Currency' in df and not df['Currency'].eq('USD').all(): raise ValueError('Only USD is supported; convert currencies before analysis')
    if budget.duplicated(['Budget ID','Month']).any(): raise ValueError('Duplicate budget ID/month rows would double count plan')
    if actual['Transaction ID'].isna().any() or actual['Transaction ID'].duplicated().any(): raise ValueError('Missing or duplicate transaction IDs')
    if len(budget)!=len(reg)*12 or not budget.groupby('Budget ID')['Month'].nunique().reindex(reg['Budget ID'],fill_value=0).eq(12).all(): raise ValueError('Each registered ID requires 12 budget months, including zero budgets')
    for df,q,amount in [(budget,'Budget Units','Budget USD'),(actual,'Units','Amount USD')]:
        if ((df[q]*df['Unit Rate USD']-df[amount]).abs()>.011).any(): raise ValueError(f'{amount} does not equal units × rate')
    if (budget['Budget Units']<0).any() or (budget['Budget USD']<0).any(): raise ValueError('Negative budgets are not supported by this expense bridge')
    if ((budget['Budget Units']==0)&(budget['Budget USD']!=0)).any(): raise ValueError('Nonzero budget requires planned units')
    return reg,budget,actual

def analyze(reg,budget,actual):
    b=budget.copy();a=actual.copy()
    b['month']=b['Month'].dt.month
    for source,dest in [('Posting Month','post_month'),('Service Month','service_month')]: a[dest]=a[source].dt.month
    monthly=b[DIM+['month','Budget USD','Budget Units','Unit Rate USD','Planned Vendor']].rename(columns={'Budget USD':'budget','Budget Units':'budget_units','Unit Rate USD':'budget_rate','Planned Vendor':'planned_vendor'})
    keys=['Budget ID','month']
    posted=a.groupby(['Budget ID','post_month']).agg(actual=('Amount USD','sum'),lines=('Transaction ID','size')).reset_index().rename(columns={'post_month':'month'})
    service=a.groupby(['Budget ID','service_month']).agg(service_actual=('Amount USD','sum'),actual_units=('Units','sum')).reset_index().rename(columns={'service_month':'month'})
    monthly=monthly.merge(posted,on=keys,how='left',validate='one_to_one').merge(service,on=keys,how='left',validate='one_to_one')
    for c in ['actual','lines','service_actual','actual_units']:monthly[c]=monthly[c].fillna(0)
    planned=monthly['budget_units']!=0
    monthly['volume']=np.where(planned,(monthly['actual_units']-monthly['budget_units'])*monthly['budget_rate'],0)
    monthly['rate_mix']=np.where(planned,monthly['service_actual']-monthly['actual_units']*monthly['budget_rate'],0)
    monthly['unbudgeted']=np.where(~planned,monthly['service_actual'],0)
    monthly['timing']=monthly['actual']-monthly['service_actual']
    monthly['variance']=monthly['actual']-monthly['budget']
    residual=monthly['variance']-monthly[['volume','rate_mix','unbudgeted','timing']].sum(axis=1)
    if residual.abs().max()>.011:raise ValueError('Variance bridge does not reconcile')
    if abs(monthly['actual'].sum()-a['Amount USD'].sum())>.011:raise ValueError('Actuals rollup does not reconcile')
    if abs(monthly['budget'].sum()-b['Budget USD'].sum())>.011:raise ValueError('Budget rollup does not reconcile')
    monthly['lines']=monthly['lines'].astype(int)
    transactions=[]
    for r in a.to_dict('records'):
        transactions.append({'id':r['Budget ID'],'tx':r['Transaction ID'],'date':r['Posting Date'].strftime('%Y-%m-%d'),'post':r['post_month'],'service':r['service_month'],'vendor':r['Actual Vendor'],'type':r['Transaction Type'],'units':float(r['Units']),'rate':float(r['Unit Rate USD']),'amount':float(r['Amount USD']),'description':str(r['Description'])})
    return monthly,transactions

def load_forecasts(path,reg,actual):
    """Validate complete, frozen quarter-end snapshots separately from GL facts."""
    with pd.ExcelFile(path) as book:
        if 'Forecasts' not in book.sheet_names:
            return pd.DataFrame()
    f=pd.read_excel(path,sheet_name='Forecasts',dtype={c:str for c in ['Budget ID','Cost Center ID','Account ID','Account Group ID','Scenario ID']})
    required=DIM+['Scenario ID','Scenario','As Of Date','Actual Through Month','Month','Period Type','Forecast Units','Unit Rate USD','Forecast USD','Currency','Planned Vendor','Assumption']
    if set(required)-set(f):raise ValueError(f'Forecasts: missing columns {sorted(set(required)-set(f))}')
    if f[required].isna().any().any():raise ValueError('Forecasts contain missing required values')
    for c in ['Cost Center ID','Account ID']:f[c]=f[c].str.zfill(2)
    for c in ['Forecast Units','Unit Rate USD','Forecast USD','Actual Through Month']:
        f[c]=pd.to_numeric(f[c],errors='raise')
        if not np.isfinite(f[c]).all():raise ValueError(f'Forecasts: invalid {c}')
    f['Month']=pd.to_datetime(f['Month'],errors='raise');f['As Of Date']=pd.to_datetime(f['As Of Date'],errors='raise')
    if not f['Month'].dt.year.eq(2026).all() or not f['Month'].dt.day.eq(1).all():raise ValueError('Forecast months must be month-start dates in 2026')
    if not f['Currency'].eq('USD').all():raise ValueError('Forecasts must be USD')
    if set(f['Scenario ID'])!={'FQ1','FQ2','FQ3'}:raise ValueError('Expected forecast snapshots FQ1, FQ2, FQ3')
    if f.duplicated(['Scenario ID','Budget ID','Month']).any():raise ValueError('Duplicate forecast scenario/ID/month')
    mapped=f.merge(reg[DIM],on='Budget ID',suffixes=('','_reg'),how='left',validate='many_to_one',indicator=True)
    if not mapped['_merge'].eq('both').all():raise ValueError('Forecast contains unknown Budget IDs')
    for c in DIM[1:]:
        if not mapped[c].eq(mapped[c+'_reg']).all():raise ValueError(f'Forecasts: inconsistent {c}')
    actual_month=actual.groupby(['Budget ID','Posting Month']).agg(amount=('Amount USD','sum'),units=('Units','sum'))
    for q in [1,2,3]:
        cutoff=q*3;s=f[f['Scenario ID']==f'FQ{q}'];asof=pd.Timestamp(2026,cutoff,1)+pd.offsets.MonthEnd(0)
        if not s['Scenario'].eq(f'Q{q} forecast').all() or not s['As Of Date'].eq(asof).all() or not s['Actual Through Month'].eq(cutoff).all():raise ValueError('Inconsistent forecast snapshot metadata')
        if len(s)!=len(reg)*12 or not s.groupby('Budget ID')['Month'].nunique().reindex(reg['Budget ID'],fill_value=0).eq(12).all():raise ValueError('Forecast missing ID/month rows')
        closed=s['Month'].dt.month<=cutoff
        if not s['Period Type'].eq(np.where(closed,'Closed actual','Estimate')).all():raise ValueError('Forecast period type disagrees with cutoff')
        history=s[closed].set_index(['Budget ID','Month'])
        expected=actual_month.reindex(history.index).fillna(0)
        if ((history['Forecast USD']-expected['amount']).abs()>.011).any() or ((history['Forecast Units']-expected['units']).abs()>.0001).any():raise ValueError('Closed forecast months do not equal actual postings')
        future=s[~closed]
        if ((future['Forecast Units']*future['Unit Rate USD']-future['Forecast USD']).abs()>.011).any():raise ValueError('Forecast estimate amount disagrees with units and rate')
    return f

def write_report(path,out):
    reg,b,a=load_data(path);monthly,transactions=analyze(reg,b,a);out.mkdir(parents=True,exist_ok=True)
    forecasts=load_forecasts(path,reg,a)
    forecast_records=[];scenario_meta=[]
    if not forecasts.empty:
        forecasts['month']=forecasts['Month'].dt.month
        for q in [1,2,3]:
            sid=f'FQ{q}';sf=forecasts[forecasts['Scenario ID']==sid]
            monthly=monthly.merge(sf[['Budget ID','month','Forecast USD']].rename(columns={'Forecast USD':sid}),on=['Budget ID','month'],validate='one_to_one')
            scenario_meta.append({'id':sid,'label':f'Q{q} forecast','cutoff':q*3,'asof':sf['As Of Date'].iloc[0].strftime('%Y-%m-%d')})
        for r in forecasts.to_dict('records'):
            forecast_records.append({'scenario':r['Scenario ID'],'id':r['Budget ID'],'month':r['month'],'type':r['Period Type'],'amount':float(r['Forecast USD']),'units':float(r['Forecast Units']),'rate':float(r['Unit Rate USD']),'vendor':r['Planned Vendor'],'assumption':r['Assumption']})
        fcomparison=forecasts.merge(monthly[DIM+['month','actual','budget']],on=DIM+['month'],validate='many_to_one')
        fcomparison['Actual vs Forecast USD']=fcomparison['actual']-fcomparison['Forecast USD']
        fcomparison['Forecast vs Budget USD']=fcomparison['Forecast USD']-fcomparison['budget']
        fcomparison.to_csv(out/'forecast_comparisons_monthly.csv',index=False)
    monthly.to_csv(out/'monthly_budget_id_variances.csv',index=False)
    for name,keys in [('account_groups',['Account Group ID','Account Group']),('accounts',['Account ID','Account Name','Account Group']),('cost_centers',['Cost Center ID','Cost Center Name']),('budget_ids',DIM)]:
        df=monthly.groupby(keys,as_index=False)[METRICS].sum();df['variance_pct']=df['variance']/df['budget'].replace(0,np.nan);df.to_csv(out/f'{name}_annual.csv',index=False)
    payload={'source':path.name,'rows':json.loads(monthly.to_json(orient='records')),'transactions':transactions,'forecasts':forecast_records,'scenarios':scenario_meta,'counts':{'budget_ids':len(reg),'budget_rows':len(b),'actual_rows':len(a),'forecast_rows':len(forecasts)},'checks':{'source_totals_reconcile':True,'monthly_bridges_reconcile':True,'forecast_snapshots_validated':not forecasts.empty,'scenario_guide_used':False}}
    template=Path(__file__).with_name('report_template.html').read_text(encoding='utf-8')
    data=json.dumps(payload,ensure_ascii=False,allow_nan=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    report=out/'variance_report.html';report.write_text(template.replace('__DATA__',data),encoding='utf-8')
    (out/'validation.json').write_text(json.dumps(payload['checks'],indent=2),encoding='utf-8')
    print(f'Report: {report.resolve()}\nActual: ${a["Amount USD"].sum():,.2f}\nBudget: ${b["Budget USD"].sum():,.2f}\nVariance: ${a["Amount USD"].sum()-b["Budget USD"].sum():,.2f}')
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('workbook',nargs='?',type=Path,default=Path(__file__).with_name('Synthetic_FPA_2026_Grouped.xlsx'));parser.add_argument('--out',type=Path,default=Path(__file__).with_name('report'));parser.add_argument('--open',action='store_true',help='Open the generated offline report in your browser');args=parser.parse_args()
    try: report=write_report(args.workbook,args.out)
    except (ValueError,KeyError,FileNotFoundError,ImportError) as e:parser.exit(1,f'Cannot analyze workbook: {e}\n')
    if args.open:webbrowser.open(report.resolve().as_uri())
if __name__=='__main__':main()
