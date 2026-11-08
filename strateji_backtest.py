#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
strateji_backtest.py — Ücretsiz OKX geçmiş mum verisinde koşullu scalp strateji keşfi.
Kural: hiçbir strateji her zaman çalışmaz; yalnızca belli rejimde çalışır.
Her stratejiyi rejime göre (trend/range + volatilite) segmentleyip expectancy ölçer.
Para gerektirmez: public REST API, anahtar yok. Sonuç JSON + konsol özeti.
"""
import json, os, sys, time, urllib.request, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "backtest_veri")
os.makedirs(CACHE, exist_ok=True)

INST = sys.argv[1] if len(sys.argv) > 1 else "ETH-USDT-SWAP"
BAR = sys.argv[2] if len(sys.argv) > 2 else "5m"
TARGET = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
START = sys.argv[4] if len(sys.argv) > 4 else None  # YYYY-MM-DD, ortak dönem karşılaştırması için
END = sys.argv[5] if len(sys.argv) > 5 else None    # YYYY-MM-DD (hariç)

def _epoch(d):
    return int(time.mktime(time.strptime(d, "%Y-%m-%d"))) * 1000

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def load_candles(inst, bar, target):
    path = os.path.join(CACHE, f"{inst}_{bar}.json")
    cached = []
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                cached = json.load(f)
        except (OSError, ValueError):
            cached = []
    # OKX newest-first; page back with 'after'
    out = list(cached)
    seen = {c[0] for c in out}
    after = min(seen) if seen else None
    base = "https://www.okx.com/api/v5/market/history-candles"
    tries = 0
    while len(out) < target and tries < 60:
        tries += 1
        url = f"{base}?instId={inst}&bar={bar}&limit=100"
        if after:
            url += f"&after={after}"
        try:
            d = fetch(url).get("data", [])
        except Exception as e:
            print("fetch err:", e); time.sleep(1); continue
        if not d:
            break
        new = [c for c in d if c[0] not in seen]
        if not new:
            break
        for c in new:
            seen.add(c[0]); out.append(c)
        after = min(int(c[0]) for c in d)
        time.sleep(0.12)
    # newest-first -> oldest-first
    out.sort(key=lambda c: int(c[0]))
    # keep confirmed candles only (last field '1')
    out = [c for c in out if str(c[8]) == "1"] if out and len(out[0]) > 8 else out
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f)
    return out

def num(c):
    return dict(ts=int(c[0]), o=float(c[1]), h=float(c[2]), l=float(c[3]),
                c=float(c[4]), v=float(c[5]))

def ema(vals, n):
    if not vals: return []
    k = 2/(n+1); out = [vals[0]]
    for x in vals[1:]:
        out.append(x*k + out[-1]*(1-k))
    return out

def rsi(closes, n=14):
    if len(closes) <= n: return [50.0]*len(closes)
    gains=[]; losses=[]
    out=[50.0]*len(closes)
    ag=al=0.0
    for i in range(1,len(closes)):
        ch=closes[i]-closes[i-1]
        g=max(ch,0); l=max(-ch,0)
        if i<=n:
            ag+=g/n; al+=l/n
            if i==n:
                out[i]=100-100/(1+(ag/al if al else 1e9))
        else:
            ag=(ag*(n-1)+g)/n; al=(al*(n-1)+l)/n
            out[i]=100-100/(1+(ag/al if al else 1e9))
    return out

def atr(candles, n=14):
    out=[0.0]*len(candles)
    trs=[]
    for i in range(len(candles)):
        if i==0: tr=candles[i]['h']-candles[i]['l']
        else:
            pc=candles[i-1]['c']
            tr=max(candles[i]['h']-candles[i]['l'], abs(candles[i]['h']-pc), abs(candles[i]['l']-pc))
        trs.append(tr)
        if i<n:
            out[i]=statistics.mean(trs[:i+1]) if trs[:i+1] else tr
        else:
            out[i]=(out[i-1]*(n-1)+tr)/n
    return out

def regime(closes, atrs, i, look=50):
    """Trend yönü + volatilite rejimi. Basit lineer eğim / ATR normalize."""
    if i < look:
        a=atrs[i] or 1e-9
        return ("range", a/closes[i]*100)
    seg = closes[i-look:i+1]
    n=len(seg); xs=list(range(n))
    mx=statistics.mean(xs); my=statistics.mean(seg)
    denom=sum((x-mx)**2 for x in xs) or 1
    slope=sum((xs[j]-mx)*(seg[j]-my) for j in range(n))/denom
    a=atrs[i] or 1e-9
    strength=slope*look/a   # toplam hareket / ATR
    if strength > 1.2: trend="up"
    elif strength < -1.2: trend="down"
    else: trend="range"
    volpct=a/closes[i]*100
    return (trend, volpct)

def simulate(candles, entry_i, side, tp_mult, sl_mult, atrs, max_hold=12):
    """entry next bar open. Conservative: same-bar TP+SL -> SL first. Time stop."""
    if entry_i+1 >= len(candles): return None
    e = candles[entry_i+1]['o']
    a = atrs[entry_i] or e*0.002
    tp = e + side*tp_mult*a
    sl = e - side*sl_mult*a
    risk = abs(e-sl) or 1e-9
    for j in range(entry_i+1, min(entry_i+1+max_hold, len(candles))):
        b=candles[j]
        hit_sl = (b['l']<=sl) if side>0 else (b['h']>=sl)
        hit_tp = (b['h']>=tp) if side>0 else (b['l']<=tp)
        if hit_sl and hit_tp:
            return -1.0, j-entry_i   # conservative SL first
        if hit_sl:
            return -1.0, j-entry_i
        if hit_tp:
            return (tp-e)*side/risk, j-entry_i
    # time stop at close
    exitp=candles[min(entry_i+max_hold, len(candles)-1)]['c']
    return (exitp-e)*side/risk, max_hold

def signals(candles, closes, rsi_v, atrs, emas, emal, bb):
    """Her mum için strateji sinyalleri (entry o mumun kapanışında, next open'da gir)."""
    N=20
    sigs={k:[] for k in ["sweep_long","sweep_short","breakout_long","breakout_short","rsi_long","rsi_short","bb_long","bb_short"]}
    for i in range(N+2, len(candles)):
        lows=[candles[j]['l'] for j in range(i-N,i)]
        highs=[candles[j]['h'] for j in range(i-N,i)]
        c=candles[i]
        # sweep: new extreme low/high then close back inside (reversal fitili)
        if c['l'] < min(lows) and c['c'] > min(lows) and c['c']>c['o']:
            sigs["sweep_long"].append(i)
        if c['h'] > max(highs) and c['c'] < max(highs) and c['c']<c['o']:
            sigs["sweep_short"].append(i)
        # breakout: close beyond N-bar extreme
        if c['c'] > max(highs):
            sigs["breakout_long"].append(i)
        if c['c'] < min(lows):
            sigs["breakout_short"].append(i)
        # rsi mean reversion
        if rsi_v[i] < 30 and rsi_v[i-1] >= 30:
            sigs["rsi_long"].append(i)
        if rsi_v[i] > 70 and rsi_v[i-1] <= 70:
            sigs["rsi_short"].append(i)
        # bollinger fade
        if bb[i] and c['c'] < bb[i][0]:
            sigs["bb_long"].append(i)
        if bb[i] and c['c'] > bb[i][1]:
            sigs["bb_short"].append(i)
    return sigs

def bollinger(closes, n=20, k=2):
    out=[None]*len(closes)
    for i in range(n,len(closes)):
        seg=closes[i-n:i+1]; m=statistics.mean(seg)
        sd=statistics.pstdev(seg)
        out[i]=(m-k*sd, m+k*sd, m)
    return out

def main():
    raw=load_candles(INST,BAR,TARGET)
    if len(raw)<200:
        print("Yetersiz veri:",len(raw)); return
    candles=[num(c) for c in raw]
    if START:
        candles=[c for c in candles if c['ts']>=_epoch(START)]
    if END:
        candles=[c for c in candles if c['ts']<_epoch(END)]
    if len(candles)<200:
        print("Filtre sonrası yetersiz veri:",len(candles)); return
    closes=[c['c'] for c in candles]
    atrs=atr(candles)
    rsi_v=rsi(closes)
    emas=ema(closes,20); emal=ema(closes,50)
    bb=bollinger(closes)
    sigs=signals(candles,closes,rsi_v,atrs,emas,emal,bb)
    volmed=statistics.median([atrs[i]/closes[i]*100 for i in range(50,len(closes))])

    results={}
    TP,SL=1.5,1.0
    for name, idxs in sigs.items():
        side = 1 if name.endswith("long") else -1
        buckets={}
        for i in idxs:
            trend,volpct=regime(closes,atrs,i)
            vol = "highvol" if volpct>volmed else "lowvol"
            for key in [trend, vol, "ALL"]:
                r=simulate(candles,i,side,TP,SL,atrs)
                if r is None: continue
                R,hold=r
                b=buckets.setdefault(key,[])
                b.append((R,hold))
        results[name]={}
        for key,b in buckets.items():
            if not b: continue
            wins=[x for x,_ in b if x>0]; losses=[x for x,_ in b if x<=0]
            totalR=sum(x for x,_ in b)
            wr=len(wins)/len(b)*100
            aw=statistics.mean(wins) if wins else 0
            al=statistics.mean(losses) if losses else 0
            pf=(sum(wins)/abs(sum(losses))) if losses and sum(losses)!=0 else (99 if wins else 0)
            results[name][key]=dict(n=len(b),wr=round(wr,1),expR=round(totalR/len(b),3),
                                    totalR=round(totalR,2),pf=round(pf,2),
                                    avgW=round(aw,2),avgL=round(al,2),
                                    avghold=round(statistics.mean(h for _,h in b),1))
    out=dict(inst=INST,bar=BAR,candles=len(candles),
             first=time.strftime("%Y-%m-%d",time.localtime(candles[0]['ts']/1000)),
             last=time.strftime("%Y-%m-%d",time.localtime(candles[-1]['ts']/1000)),
             tp_mult=TP,sl_mult=SL,volmed=round(volmed,3),results=results)
    suffix = (f"_{START}" if START else "") + (f"_{END}" if END else "")
    op=os.path.join(CACHE,f"sonuc_{INST}_{BAR}{suffix}.json")
    with open(op,"w",encoding="utf-8") as f: json.dump(out,f,ensure_ascii=False,indent=2)

    print(f"\n=== {INST} {BAR} | {len(candles)} mum | {out['first']} .. {out['last']} | TP {TP}ATR / SL {SL}ATR ===")
    print(f"volatilite medyan ATR% = {volmed:.3f}")
    for name in results:
        a=results[name].get("ALL")
        if not a: continue
        print(f"\n{name}: ALL n={a['n']} wr={a['wr']}% expR={a['expR']} totalR={a['totalR']} pf={a['pf']}")
        # en iyi rejimler
        rows=[(k,v) for k,v in results[name].items() if k!="ALL" and v['n']>=8]
        rows.sort(key=lambda kv: kv[1]['expR'], reverse=True)
        for k,v in rows[:4]:
            print(f"   {k:9s} n={v['n']:3d} wr={v['wr']:5.1f}% expR={v['expR']:+.3f} totalR={v['totalR']:+7.2f} pf={v['pf']:.2f}")
    print("\nJSON:",op)

if __name__=="__main__":
    main()