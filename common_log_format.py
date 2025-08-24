#!/usr/bin/env python3
import sys#đọc từ stdin, ghi stdout
import re#tách trường

# Regex bắt log theo CLF hoặc Combined
# Ví dụ:
# 118.70.74.157 - - [28/Sep/2015:11:32:04 +0700] "GET /..." 200 12086 "ref" "ua"
LOG_RE_CLF = re.compile(
    r'^(\S+)\s+'             # 1: host #neo đầu cuối, bắt toàn bộ dòng, phát hiện rác thừa cuối dòng
    r'(\S+)\s+'              # 2: ident #bắt từ ko có khoảng trắng cho các trường ko dc chứa space: host, ident, authuser, status, bytes
    r'(\S+)\s+'              # 3: authuser # có ít nhất 1 khoảng trắng ngăn cách các trường
    r'\[([^\]]+)\]\s+'       # 4: time #thời gian nằm trong []. Dùng [^]]+ để ko vượt qua dấu ], kết thúc an toàn hơn so với .*
    r'"([^"]*)"\s+'          # 5: request #phần request nằm trong dấu "...", cho phép có khoảng trắng bên trong; ko cho phép dấu " ở giữa
    r'(\d{3})\s+'            # 6: status (3 chữ số) ràng buộc status phải có 3 chữ số hợp lệ
    r'(\S+)'                 # 7: bytes cho phép số hoặc -(1 số cài đătj sẽ dùng - khi không biết kích thước
    r'(?:\s+"[^"]*"\s+"[^"]*")?'  # optional: "referer" "user-agent" ? → tùy chọn: nếu là CLF thuần (không có ref/UA) vẫn match; nếu là Combined thì match luôn cả "referer" và "user-agent" ở cuối.
    r'\s*$' # \s* có thể có hoặc không có khoảng trắng ở cuối, $ là neo cuối dòng trong regex
)

def convert_line(line: str) -> str | None:
    """
    Parse một dòng log CLF/Combined, trả về đúng định dạng CLF (7 trường).
    """
    m = LOG_RE_CLF.match(line)#ktra xem dòng có phải là CLF không
    if not m:
        return None #nếu ko để main in cảnh báo và bỏ qua

    host, ident, authuser, time_str, request, status, bytes_ = m.groups() #nếu đúng thì trả về đúng 7 nhóm tương ứng CLF

    # Nếu thiếu thì thay bằng '-'
    host = host or '-'
    ident = ident or '-'
    authuser = authuser or '-'
    request = request or '-'
    status = status or '-'
    bytes_ = bytes_ or '-'

    return f'{host} {ident} {authuser} [{time_str}] "{request}" {status} {bytes_}'

def main():
    for raw in sys.stdin: #duyệt dòng từ stdin
        line = raw.rstrip('\n') #raw là dòng gốc đọc đc, kết thúc bằng \n(xuống dòng), rstrip('\n'): gỡ kí tự xuống dòng ở cuối
        if not line.strip():#bỏ qua các dòng trống/chỉ toàn khoảng trắng, vì đấy ko phải log hợp lệ
            continue
        out = convert_line(line)#nếu trả về none, in cảnh báo sang stderr, ko làm bẩn stdout
        if out is None:
            # Cảnh báo sang stderr nếu không parse được
            print(f'# cannot-parse: {line}', file=sys.stderr)
            continue
        print(out)

if __name__ == '__main__':
    main()
