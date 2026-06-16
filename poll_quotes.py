#!/usr/bin/env python3
"""Fetch delayed stock quotes for the local (8-county) public companies.

Yahoo Finance's quote endpoints do NOT send CORS headers, so the browser can't
call them directly. We fetch server-side here (on a GitHub Actions schedule) and
write quotes.json, which the Busy Biz homepage reads same-origin for its ticker.

Quotes are delayed, not real-time — the homepage labels them as such and shows a
"updated Nm ago" chip built from this file's generated_at.

Input:  local_tickers.json  ([{ticker, name}], core-region companies)
Output: quotes.json         ({generated_at, quotes:[{ticker,name,price,change,change_pct,prev_close,currency,market_time}]})
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TICKERS = HERE / "local_tickers.json"
OUT = HERE / "quotes.json"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def _get(url):
    """Fetch JSON. curl-cffi (TLS fingerprint) first for cloud runners, urllib fallback."""
    try:
        from curl_cffi import requests as creq
        r = creq.get(url, impersonate="chrome", timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def fetch_quote(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    m = _get(url)["chart"]["result"][0]["meta"]
    price = m.get("regularMarketPrice")
    prev = m.get("chartPreviousClose") or m.get("previousClose")
    if price is None or prev is None:
        return None
    change = round(price - prev, 2)
    pct = round((change / prev) * 100, 2) if prev else 0.0
    return {
        "ticker": ticker,
        "price": round(price, 2),
        "change": change,
        "change_pct": pct,
        "prev_close": round(prev, 2),
        "currency": m.get("currency", "USD"),
        "market_time": m.get("regularMarketTime"),
    }


def main():
    tickers = json.loads(TICKERS.read_text())
    names = {t["ticker"]: t["name"] for t in tickers}
    quotes, failed = [], []
    for t in tickers:
        sym = t["ticker"]
        try:
            q = fetch_quote(sym)
            if q:
                q["name"] = names.get(sym, sym)
                quotes.append(q)
            else:
                failed.append(sym)
        except Exception:
            failed.append(sym)
        time.sleep(0.15)  # be polite
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "quotes": quotes,
    }
    OUT.write_text(json.dumps(payload, indent=1))
    print(f"Wrote {OUT}: {len(quotes)} quotes, {len(failed)} failed"
          + (f" ({', '.join(failed[:8])}{'…' if len(failed) > 8 else ''})" if failed else ""))


if __name__ == "__main__":
    main()
