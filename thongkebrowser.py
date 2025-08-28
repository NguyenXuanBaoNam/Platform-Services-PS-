import argparse, re
from collections import Counter
from urllib.request import urlopen

BROWSER_SORT = ["Chrome","Edge","Firefox","Safari","Opera","Samsung Internet","IE","Chromium","Brave","Bots","Other"]

def phan_loai_browser(ua: str) -> str:
    s = ua.lower()
    if " edg/" in s or " edge/" in s: return "Edge"
    if " opr/" in s or " opera" in s: return "Opera"
    if "samsungbrowser" in s: return "Samsung Internet"
    if "brave" in s: return "Brave"
    if ("chrome/" in s and "chromium" not in s and " opr/" not in s and " edg/" not in s and "samsungbrowser" not in s): return "Chrome"
    if "firefox/" in s: return "Firefox"
    if ("safari/" in s and "version/" in s and "chrome/" not in s and "chromium" not in s and " opr/" not in s and " edg/" not in s): return "Safari"
    if "msie" in s or "trident/" in s: return "IE"
    if "chromium/" in s: return "Chromium"
    return "Other"

def tach_ua(line: str):
    qs = re.findall(r'"([^"]*)"', line)
    return qs[2] if len(qs) >= 3 else None

def doc_tu_url(url: str):
    with urlopen(url) as resp:
        for raw in resp.read().decode("utf-8", errors="ignore").splitlines():
            yield raw

def doc_tu_path(path: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f: yield line.rstrip("\n")

def dem_tinhtong(lines):
    c, tot = Counter(), 0
    for line in lines:
        ua = tach_ua(line)
        if not ua: continue
        c[phan_loai_browser(ua)] += 1
        tot += 1
    return c, tot

def in_bang(counts: Counter, total: int):
    if total == 0: print(f"(no data)"); return
    order = {n:i for i,n in enumerate(BROWSER_SORT)}
    items = sorted(counts.items(), key=lambda kv: (-kv[1], order.get(kv[0], 999)))
    print(f"{'Browser':<20} {'Requests':>10} {'Share %':>9}")
    print(f"{'-'*20} {'-'*10:>10} {'-'*9:>9}")
    for name, cnt in items:
        pct = cnt*100/total
        print(f"{name:<20} {cnt:>10} {pct:>8.1f}%")
    print(f"{'-'*20} {'-'*10:>10} {'-'*9:>9}")
    print(f"{'Total':<20} {total:>10} {100.0:>8.1f}%\n")

def main():
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--path")
    g.add_argument("--url")
    args = parser.parse_args()
    lines = doc_tu_path(args.path) if args.path else doc_tu_url(args.url)
    counts, total = dem_tinhtong(lines)
    in_bang(counts, total)

if __name__ == "__main__":
    main()
