import unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from analyze import load_data,load_forecasts

class ForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path=Path(__file__).with_name('Synthetic_FPA_2026_Grouped.xlsx')
        cls.reg,cls.b,cls.a=load_data(cls.path)
        cls.f=load_forecasts(cls.path,cls.reg,cls.a)
    def test_complete_snapshots(self):
        self.assertEqual(len(self.f),9360)
        self.assertEqual(self.f.groupby('Scenario ID').size().tolist(),[3120,3120,3120])
        totals=self.f.groupby('Scenario ID')['Forecast USD'].sum()
        self.assertEqual(totals.round(2).tolist(),[18717568.54,18651004.25,18555097.51])
        for q in [1,2,3]:
            f=self.f[self.f['Scenario ID']==f'FQ{q}']
            closed=f[f['Period Type']=='Closed actual']['Forecast USD'].sum()
            self.assertAlmostEqual(closed,self.a.loc[self.a['Posting Month'].dt.month<=q*3,'Amount USD'].sum(),places=2)
    def test_invalid_forecasts_stop_analysis(self):
        for case in ['duplicate','closed_amount','missing_month','dimension']:
            f=self.f.copy()
            if case=='duplicate':f=pd.concat([f,f.iloc[[0]]],ignore_index=True)
            elif case=='closed_amount':f.loc[0,'Forecast USD']+=10
            elif case=='missing_month':f=f.iloc[1:]
            else:f.loc[0,'Account Group']='Invalid'
            with patch('analyze.pd.read_excel',return_value=f):
                with self.assertRaises(ValueError):load_forecasts(self.path,self.reg,self.a)
    def test_all_forecast_comparisons_reconcile(self):
        actual=self.a.groupby(['Budget ID','Posting Month'])['Amount USD'].sum()
        budget=self.b.set_index(['Budget ID','Month'])['Budget USD']
        for _,sf in self.f.groupby('Scenario ID'):
            sf=sf.set_index(['Budget ID','Month']);a=actual.reindex(sf.index).fillna(0);b=budget.reindex(sf.index);f=sf['Forecast USD']
            self.assertLess(((a-f)-((a-b)-(f-b))).abs().max(),.001)
    def test_q1_does_not_use_later_actuals(self):
        from generate_forecasts import generate
        changed=self.a.copy()
        future=changed['Posting Month'].dt.month>3
        changed.loc[future,'Amount USD']*=2
        changed.loc[future,'Units']*=2
        with patch('generate_forecasts.load_data',return_value=(self.reg,self.b,self.a)):
            original=[r for r in generate(self.path) if r['Scenario ID']=='FQ1']
        with patch('generate_forecasts.load_data',return_value=(self.reg,self.b,changed)):
            adjusted=[r for r in generate(self.path) if r['Scenario ID']=='FQ1']
        self.assertEqual(original,adjusted)

if __name__=='__main__':unittest.main()
