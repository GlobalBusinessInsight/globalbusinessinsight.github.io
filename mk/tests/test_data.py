"""Check meaningful data invariants without network requests."""
import json, math, unittest
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]

class HistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.data = json.loads((ROOT / 'data/history.json').read_text())
    def test_complete_finite_ordered_history(self):
        self.assertEqual(set(self.data['series']), {'NASDAQ','SP500','QQQ','FEDFUNDS','GS2','GS10','PAYEMS','GDP','GDPC1'})
        for k,s in self.data['series'].items():
            rows=s['observations']; dates=[r['date'] for r in rows]
            self.assertEqual(dates, sorted(set(dates)), k)
            self.assertGreaterEqual(len(rows), 60 if k in ('GDP','GDPC1') else 200, k)
            self.assertTrue(all(math.isfinite(r['value']) for r in rows), k)
            self.assertLessEqual(dates[-1], date.today().isoformat(), k)
            self.assertTrue(s['fetchedAt'])
    def test_monthly_market_uniqueness_and_coverage(self):
        for k in ('NASDAQ','SP500','QQQ'):
            rows=self.data['series'][k]['observations']
            months=[r['date'][:7] for r in rows]
            self.assertEqual(len(months), len(set(months)), k)
            self.assertGreaterEqual(len(months),240,k)
            self.assertTrue(all(r['value']>0 for r in rows))
    def test_offline_bundle_matches_json(self):
        bundle=(ROOT / 'data/history.js').read_text()
        self.assertEqual(json.loads(bundle.removeprefix('window.MARKET_DATA=').rstrip(';\n')),self.data)


class FailureRetentionTests(unittest.TestCase):
    def test_failed_fetch_preserves_valid_history(self):
        import importlib.util, tempfile
        from unittest.mock import patch
        spec=importlib.util.spec_from_file_location('updater', ROOT/'scripts/update_data.py')
        updater=importlib.util.module_from_spec(spec);spec.loader.exec_module(updater)
        previous=json.loads((ROOT/'data/history.json').read_text())
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder);(target/'data').mkdir()
            (target/'data/history.json').write_text(json.dumps(previous))
            with patch.object(updater,'ROOT',target),patch.object(updater,'fred',side_effect=OSError('offline')),patch.object(updater,'market',side_effect=OSError('offline')),patch('builtins.print'):
                updater.main()
            current=json.loads((target/'data/history.json').read_text())
            for key in previous['series']:
                self.assertEqual(current['series'][key]['observations'],previous['series'][key]['observations'])
                self.assertEqual(current['series'][key]['fetchedAt'],previous['series'][key]['fetchedAt'])
                self.assertEqual(current['series'][key]['status'],'stale')

class QuoteTimeTests(unittest.TestCase):
    def test_current_quote_rejects_future_and_previous_month(self):
        import importlib.util
        from datetime import datetime, timezone
        spec=importlib.util.spec_from_file_location('updater_quote', ROOT/'scripts/update_data.py')
        updater=importlib.util.module_from_spec(spec);spec.loader.exec_module(updater)
        now=datetime(2026,10,2,18,tzinfo=timezone.utc)
        def quote(at): return updater.current_quote({'regularMarketPrice':123.45,'regularMarketTime':at.timestamp()},now)
        self.assertIsNone(quote(datetime(2026,9,30,20,tzinfo=timezone.utc)))
        self.assertIsNone(quote(datetime(2026,10,2,19,tzinfo=timezone.utc)))
        current=quote(datetime(2026,10,2,17,tzinfo=timezone.utc))
        self.assertEqual(current['date'],'2026-10-02')
        self.assertTrue(current['provisional'])
        self.assertEqual(current['asOf'],'2026-10-02T13:00:00-04:00')

if __name__=='__main__': unittest.main()
