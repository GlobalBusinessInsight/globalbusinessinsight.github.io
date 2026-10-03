#!/usr/bin/env python3
"""Fetch public observations; retain validated history on source failure. No database/dependencies."""
import csv, io, json, math, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
START = '2005-01-01'
FRED = ['FEDFUNDS', 'PAYEMS', 'GDPC1', 'GDP', 'GS2', 'GS10']
MARKETS = {'SP500': '^GSPC', 'NASDAQ': '^IXIC', 'QQQ': 'QQQ'}

def get(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=40) as r:
                return r.read().decode('utf-8-sig')
        except Exception:
            if attempt == 2: raise
            time.sleep(2 ** attempt)

def finite(value):
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (ValueError, TypeError): return None

def fred(key):
    api_key = os.getenv('FRED_API_KEY')
    if api_key:
        url = 'https://api.stlouisfed.org/fred/series/observations?' + urlencode({'series_id': key, 'api_key': api_key, 'file_type': 'json', 'observation_start': START})
        rows = [(x['date'], x['value']) for x in json.loads(get(url))['observations']]
    else:
        url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?' + urlencode({'id': key, 'cosd': START})
        rows = [(x['observation_date'], x[key]) for x in csv.DictReader(io.StringIO(get(url)))]
    data = [{'date': d, 'value': finite(v)} for d, v in rows if finite(v) is not None]
    if len(data) < (60 if key in ('GDP', 'GDPC1') else 200): raise ValueError('History too short')
    return {'observations': data, 'source': 'FRED', 'url': f'https://fred.stlouisfed.org/series/{key}', 'frequency': 'quarterly' if key in ('GDP', 'GDPC1') else 'monthly'}

def current_quote(meta, now):
    value, stamp = finite(meta.get('regularMarketPrice')), finite(meta.get('regularMarketTime'))
    if value is None or value <= 0 or stamp is None or stamp > now.timestamp(): return None
    at = datetime.fromtimestamp(stamp, ZoneInfo('America/New_York'))
    if at.strftime('%Y-%m') != now.astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m'): return None
    return {'date': at.date().isoformat(), 'value': round(value, 6), 'asOf': at.isoformat(), 'provisional': True}


def market(key):
    params = urlencode({'period1': 1104537600, 'period2': int(time.time()), 'interval': '1d'})
    error = None
    for host in ('query1', 'query2'):
        try:
            raw = json.loads(get(f'https://{host}.finance.yahoo.com/v8/finance/chart/{quote(MARKETS[key], safe="")}?{params}'))
            result = raw['chart']['result'][0]
            today = datetime.now(ZoneInfo('America/New_York')).date().isoformat()
            monthly = {}
            for stamp, value in zip(result['timestamp'], result['indicators']['quote'][0]['close']):
                d = datetime.fromtimestamp(stamp, ZoneInfo('America/New_York')).date().isoformat()
                v = finite(value)
                # Exclude today's possibly unfinished daily candle, even after close.
                if v is not None and v > 0 and START <= d < today:
                    monthly[d[:7]] = {'date': d, 'value': round(v, 6)}
            latest = current_quote(result.get('meta', {}), datetime.now(timezone.utc))
            if latest and latest['date'] >= monthly.get(latest['date'][:7], {}).get('date', ''):
                monthly[latest['date'][:7]] = {k: latest[k] for k in ('date', 'value', 'asOf', 'provisional')}
            observations = [monthly[m] for m in sorted(monthly)]
            if len(observations) < 200: raise ValueError('History too short')
            return {'observations': observations, 'source': 'Yahoo Finance', 'url': f'https://finance.yahoo.com/quote/{quote(MARKETS[key], safe="")}/history/', 'frequency': 'month-end close', 'symbol': MARKETS[key], 'latestQuote': latest}
        except Exception as exc: error = exc
    raise error

def main():
    path = ROOT / 'data' / 'history.json'
    old = json.loads(path.read_text()) if path.exists() else {'series': {}}
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    result = {'schemaVersion': 1, 'checkedAt': now, 'series': dict(old['series'])}
    failures = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(fred if k in FRED else market, k): k for k in FRED + list(MARKETS)}
        for job in as_completed(jobs):
            k = jobs[job]
            try:
                series = job.result()
                obs = series['observations']
                if any(x['date'] > now[:10] for x in obs): raise ValueError('Future observation')
                previous = old['series'].get(k)
                if previous and obs[-1]['date'] < previous['observations'][-1]['date']:
                    raise ValueError('Source regressed; retaining previous snapshot')
                # Preserve older history if providers impose a moving retention window.
                combined = {x['date']: x for x in previous['observations']} if previous else {}
                if k in MARKETS:
                    new_months = {x['date'][:7] for x in obs}
                    combined = {d: x for d, x in combined.items() if d[:7] not in new_months}
                combined.update({x['date']: x for x in obs})
                series['observations'] = [combined[d] for d in sorted(combined)]
                series.update(fetchedAt=now, status='ok', error=None)
                result['series'][k] = series
                print(f'{k}: {len(series["observations"])} observations through {obs[-1]["date"]}')
            except Exception as exc:
                # Never log URLs: optional API credentials may be in them.
                failures.append(k)
                print(f'{k}: fetch failed ({type(exc).__name__}); keeping prior data', file=sys.stderr)
                if k in result['series']:
                    result['series'][k] = {**result['series'][k], 'status': 'stale', 'error': '本次抓取失败，保留上次有效数据'}
    if len(result['series']) != len(FRED) + len(MARKETS):
        raise RuntimeError('Initial download incomplete; no incomplete file was written')
    result['failedSeries'] = failures
    result['dataUpdatedAt'] = max(s['fetchedAt'] for s in result['series'].values())
    path.parent.mkdir(exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':'), allow_nan=False))
    temporary.replace(path)
    # Local-file fallback also lets the dashboard open by double-clicking index.html.
    (ROOT / 'data' / 'history.js').write_text('window.MARKET_DATA=' + json.dumps(result, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + ';\n')
    if failures:
        print('::warning::Some sources failed; previous observations retained: ' + ', '.join(failures))
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as out: out.write(f'degraded={str(bool(failures)).lower()}\n')

if __name__ == '__main__': main()
