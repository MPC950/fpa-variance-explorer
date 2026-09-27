import unittest
from pathlib import Path
import tempfile
import pandas as pd
from analyze import load_data, analyze

class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path=Path(__file__).with_name('Synthetic_FPA_2026_Grouped.xlsx')
        cls.reg,cls.b,cls.a=load_data(cls.path)
        cls.m,cls.tx=analyze(cls.reg,cls.b,cls.a)
        cls.guide=pd.read_excel(cls.path,sheet_name='Scenario Guide',dtype={'Budget ID':str})
    def test_source_totals_and_bridges(self):
        self.assertAlmostEqual(self.m.actual.sum(),18912805.39,places=2)
        self.assertAlmostEqual(self.m.budget.sum(),20530230.61,places=2)
        self.assertLess((self.m.variance-self.m[['volume','rate_mix','unbudgeted','timing']].sum(axis=1)).abs().max(),.001)
        for start,end in [(1,1),(3,4),(7,9),(1,12)]:
            s=self.m[self.m.month.between(start,end)]
            self.assertAlmostEqual(s.actual.sum(),self.a.loc[self.a['Posting Month'].dt.month.between(start,end),'Amount USD'].sum(),places=2)
    def scenario(self,name):
        keys=self.guide.loc[self.guide['Planted Scenario'].eq(name),'Budget ID']
        return self.m[self.m['Budget ID'].isin(keys)]
    def test_rate_and_volume(self):
        r=self.scenario('Rate increase');self.assertGreater(r.rate_mix.sum(),0);self.assertAlmostEqual(r.volume.sum(),0,places=2)
        v=self.scenario('Volume overage');self.assertGreater(v.volume.sum(),0);self.assertAlmostEqual(v.rate_mix.sum(),0,places=2)
    def test_timing_and_accruals(self):
        t=self.scenario('Invoice timing');self.assertLess(t.loc[t.month.eq(3),'timing'].sum(),0);self.assertGreater(t.loc[t.month.eq(4),'timing'].sum(),0);self.assertAlmostEqual(t.variance.sum(),0,places=2)
        a=self.scenario('Accrual and reversal');self.assertAlmostEqual(a.variance.sum(),0,places=2)
    def test_zero_and_unbudgeted(self):
        z=self.scenario('Cancelled initiative');self.assertEqual(z.actual.sum(),0);self.assertGreater(z.budget.sum(),0)
        u=self.scenario('Unbudgeted activity');self.assertEqual(u.budget.sum(),0);self.assertAlmostEqual(u.unbudgeted.sum(),u.actual.sum(),places=2)
        m=self.scenario('Missing posting');self.assertEqual(m.loc[m.month.eq(9),'actual'].sum(),0)
    def test_vendor_mix(self):
        v=self.scenario('Vendor mix change');self.assertGreater(v.rate_mix.sum(),0);self.assertAlmostEqual(v.volume.sum(),0,places=2)
    def test_every_id_against_answer_key(self):
        annual=self.m.groupby('Budget ID')[['actual','budget']].sum()
        for _,r in self.guide.iterrows():
            self.assertAlmostEqual(annual.loc[r['Budget ID'],'actual'],r['Expected Actual USD'],places=2)
            self.assertAlmostEqual(annual.loc[r['Budget ID'],'budget'],r['Expected Budget USD'],places=2)
    def test_invalid_inputs_rejected(self):
        # Patch input reader to test validation without authoring temporary workbooks.
        from unittest.mock import patch
        for mutation in ['duplicate','unknown','group']:
            a=self.a.copy();b=self.b.copy()
            if mutation=='duplicate':a.loc[1,'Transaction ID']=a.loc[0,'Transaction ID']
            elif mutation=='unknown':a.loc[0,'Budget ID']='99-26-99-9999'
            else:b.loc[0,'Account Group']='Wrong group'
            frames={'Budget ID Register':self.reg.copy(),'Budget':b,'Actuals':a}
            with patch('analyze.pd.read_excel',side_effect=lambda *args,**kw:frames[kw['sheet_name']].copy()):
                with self.assertRaises(ValueError):load_data(self.path)

if __name__=='__main__':unittest.main()
