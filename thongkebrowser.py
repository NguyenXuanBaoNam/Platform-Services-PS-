import argparse #đọc tham số dòng lệnh
import sys
import re #regex để tách các trường nằm trong ngoặc kép
from collections import Counter #đếm tần suất
from urllib.request import urlopen #tải nội dung log từ 1 url
#thứ tự chuẩn khi sắp xếp bảng nếu các giá trị bằng nhau
BROWSER_ORDER = [
    "Chrome", "Edge", "Firefox", "Safari", "Opera",
    "Samsung Internet", "IE", "Chromium", "Brave", "Bots", "Other",
]
#danh sách từ khóa nhận diện bot/crawler
BOT_KEYWORDS = [
    "bot","spider","crawler","slurp","bingpreview","duckduckbot",
    "facebookexternalhit","petalbot","yandex","ahrefs","semrush",
    "curl","wget","python-requests","java","go-http-client",
    "headlesschrome","monitor","uptime","pingdom","datadog",
    "elb-healthchecker",
]
#phân loại trình duyệt từ user agent
def classify_browser(ua: str) -> str:
    ua_l = ua.lower()
    if any(k in ua_l for k in BOT_KEYWORDS):
        return "Bots"
    if " edg/" in ua_l or " edge/" in ua_l:
        return "Edge"
    if " opr/" in ua_l or " opera" in ua_l:
        return "Opera"
    if "samsungbrowser" in ua_l:
        return "Samsung Internet"
    if "brave" in ua_l:
        return "Brave"
    if "chrome/" in ua_l and "chromium" not in ua_l and " opr/" not in ua_l and " edg/" not in ua_l and "samsungbrowser" not in ua_l:
        return "Chrome"
    if "firefox/" in ua_l:
        return "Firefox"
    if "safari/" in ua_l and "version/" in ua_l and "chrome/" not in ua_l and "chromium" not in ua_l and " opr/" not in ua_l and " edg/" not in ua_l:
        return "Safari"
    if "msie" in ua_l or "trident/" in ua_l:
        return "IE"
    if "chromium/" in ua_l:
        return "Chromium"
    return "Other"
#tách user-agent từ một dòng log
def extract_user_agent(line: str) -> str | None:
    # Format có 3 trường trong dấu ngoặc kép: "$request" "$http_referer" "$http_user_agent"
    qs = re.findall(r'"([^"]*)"', line)#([^'"]) bất kì kí tự nào không phải dấu "
    if len(qs) >= 3:
        return qs[2] #>=3 phần tử mặc định là user agent
    return None
#đọc log từ file
def read_lines_from_path(path: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            yield line.rstrip("\n")
#đọc log từ raw url
def read_lines_from_url(url: str):
    with urlopen(url) as resp:
        for raw in resp.read().decode("utf-8", errors="ignore").splitlines():
            yield raw
#đếm và tính tổng
def compute_stats(lines, exclude_bots: bool):
    counts = Counter()
    total = 0
    for line in lines:
        ua = extract_user_agent(line)
        if not ua:
            continue
        b = classify_browser(ua)
        if exclude_bots and b == "Bots":
            continue
        counts[b] += 1
        total += 1
    return counts, total

def print_table(counts: Counter, total: int, title: str):
    if total == 0:
        print(f"{title}: (no data)")
        return
    print(title)
    print("-" * len(title))
    order_index = {name: i for i, name in enumerate(BROWSER_ORDER)}
    items = sorted(counts.items(), key=lambda kv: (-kv[1], order_index.get(kv[0], 999)))
    print(f"{'Browser':<20} {'Requests':>10} {'Share %':>9}")
    print(f"{'-'*20} {'-'*10:>10} {'-'*9:>9}")
    for name, c in items:
        pct = (c / total) * 100
        print(f"{name:<20} {c:>10} {pct:>8.1f}%")
    print(f"{'-'*20} {'-'*10:>10} {'-'*9:>9}")
    print(f"{'Total':<20} {total:>10} {100.0:>8.1f}%\n")
#in bảng kết quả
def main():
    #tạo parser, bắt buộc chọn 1 trong 2 --path hoặc --url
    parser = argparse.ArgumentParser(description="Compute browser share from Nginx access log (by User-Agent).")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--path", help="Path to local nginx access log file")
    g.add_argument("--url", help="URL to nginx access log file")
    parser.add_argument("--exclude-bots", action="store_true", help="Exclude bots/crawlers from the stats") #exclude-bots là flag, có thì true ko có thì false
    args = parser.parse_args()
#đọc lần 1 tính cả bot
    lines1 = read_lines_from_path(args.path) if args.path else read_lines_from_url(args.url)
    counts_inc, total_inc = compute_stats(lines1, exclude_bots=False)
#đọc lần 2 để loại bot
    lines2 = read_lines_from_path(args.path) if args.path else read_lines_from_url(args.url)
    counts_exc, total_exc = compute_stats(lines2, exclude_bots=True)

    if args.exclude_bots:
        print_table(counts_exc, total_exc, "Browser share (bots excluded)")
    else:
        print_table(counts_inc, total_inc, "Browser share (including bots)")
        print_table(counts_exc, total_exc, "Browser share (bots excluded)")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage examples:\n"
              "  python browser_share.py --url https://gist.github.com/anonymous/9f9bd99d2f32914d033a\n"
              "  python browser_share.py --path /var/log/nginx/access.log --exclude-bots\n")
    else:
        main()
