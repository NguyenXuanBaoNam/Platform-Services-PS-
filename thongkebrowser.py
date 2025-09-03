import argparse, re
from collections import Counter
from urllib.request import urlopen
from user_agents import parse



def phan_loai_browser(ua: str) -> str:
    user_agent = parse(ua)
    return user_agent.browser.family


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
    if total == 0:
        print("(no data)")
        return
    # sắp xếp: giảm dần theo count, nếu bằng nhau thì theo tên
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    print(f"{'Browser':<30} {'Requests':>10} {'Share %':>9}")
    print(f"{'-'*20} {'-'*10:>10} {'-'*9:>9}")
    for name, cnt in items:
        pct = cnt * 100 / total
        print(f"{name:<30} {cnt:>10} {pct:>8.1f}%")
    print(f"{'-'*30} {'-'*10:>10} {'-'*9:>9}")
    print(f"{'Total':<30} {total:>10} {100.0:>8.1f}%\n")


def main():
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--path")
    g.add_argument("--url")
    args = parser.parse_args()
    lines = doc_tu_path(args.path) if args.path else doc_tu_url(args.url)
    counts, total = dem_tinhtong(lines)
    in_bang(counts, total)

main()
