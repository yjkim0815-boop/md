#!/usr/bin/env python3
"""로우 응답(원본 API 결과) 보관 · 30일 보존 후 삭제.

  python rawstore.py put   <주차월요일> <파일...>   # raw/<주차>/ 로 평문 보관
  python rawstore.py putov <파일...>                # raw/_overflow/ 로 평문 보관
  python rawstore.py ls    [주차]                   # 보관 현황 (보관일·잔여일 포함)
  python rawstore.py prune [--dry-run] [--today YYYY-MM-DD]
                                                    # 보관 7일 경과분 삭제

⚠️ **압축하지 않는다 (2026-08-05 사용자 확정).** 평문 `.json` 그대로 둔다.
git 이 커밋 시 zlib 으로 자동 압축하므로 저장소 크기·clone 전송량은 압축해도 거의 같다.

🗑️ **보존 기간 30일 (2026-08-07 사용자 확정).**
보관일로부터 **30일이 지나면 삭제**한다. 판정 시점은 **워크로그 수집이 완료된 직후**다
(수집 루틴 마지막 단계에서 `prune` 을 부른다). 별도 스케줄러를 두지 않는다.

보관일은 파일 mtime 이 아니라 `raw/_meta.json` 에 **명시 기록**한다.
파일을 옮기면 mtime 이 초기화돼 보존 기간 계산이 틀어지기 때문이다.

로우는 한 번 받으면 변하지 않는다. 7일 안에는 스키마가 바뀌어도 API 재호출 없이
data/*.json 을 다시 만들 수 있다. 그 이후는 `data/*.json` 이 유일한 사본이다.

📌 로우 보유 여부는 **주차 확정 조건이 아니다.** 확정은 ①W_now-2 이하 ②roster 17
③collectedDays 7/7 의 3조건으로만 판정한다. 7일이 지나 로우가 지워져도 확정은 유지된다.
"""
import sys, os, glob, shutil, json, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
META = os.path.join(RAW, "_meta.json")
KEEP_DAYS = 30


def human(n):
    return "%.1f KB" % (n / 1024) if n < 1048576 else "%.2f MB" % (n / 1048576)


def load_meta():
    if os.path.exists(META):
        return json.load(open(META, encoding="utf-8"))
    return {}


def save_meta(m):
    os.makedirs(RAW, exist_ok=True)
    json.dump(m, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def today_str(arg=None):
    return arg or datetime.date.today().isoformat()


def put(bucket, files, today=None):
    """bucket = 주차월요일 또는 '_overflow'."""
    dest = os.path.join(RAW, bucket)
    os.makedirs(dest, exist_ok=True)
    tot = n = 0
    for f in files:
        if not os.path.isfile(f):
            continue
        shutil.copyfile(f, os.path.join(dest, os.path.basename(f)))
        sz = os.path.getsize(os.path.join(dest, os.path.basename(f)))
        tot += sz
        n += 1
        print("  %-28s %10s" % (os.path.basename(f), human(sz)))
    if n:
        m = load_meta()
        m[bucket] = today_str(today)          # 보관일 기록(갱신 시 연장)
        save_meta(m)
        print("  합계 %s · 보관일 %s" % (human(tot), m[bucket]))


def cmd_ls(week=None, today=None):
    if not os.path.isdir(RAW):
        print("raw/ 없음")
        return
    m = load_meta()
    td = datetime.date.fromisoformat(today_str(today))
    tot = n = 0
    for d in sorted(os.listdir(RAW)):
        p = os.path.join(RAW, d)
        if not os.path.isdir(p) or (week and d != week):
            continue
        fs = sorted(glob.glob(os.path.join(p, "*.json")))
        sz = sum(os.path.getsize(x) for x in fs)
        tot += sz
        n += len(fs)
        kept = m.get(d)
        if kept:
            age = (td - datetime.date.fromisoformat(kept)).days
            left = KEEP_DAYS - age
            mark = "🗑️ 삭제대상" if left <= 0 else "D-%d" % left
        else:
            age, mark = "?", "보관일 미기록"
        print("  %-13s %2d개 %11s  보관 %-10s %s" % (d, len(fs), human(sz), kept or "-", mark))
    print("  ─ 총 %d개 · %s  (보존 %d일)" % (n, human(tot), KEEP_DAYS))


def cmd_prune(dry=False, today=None):
    """보관 7일 경과분 삭제. 수집 완료 직후 호출한다."""
    if not os.path.isdir(RAW):
        print("  raw/ 없음")
        return
    m = load_meta()
    td = datetime.date.fromisoformat(today_str(today))
    gone = kept = 0
    freed = 0
    for d in sorted(os.listdir(RAW)):
        p = os.path.join(RAW, d)
        if not os.path.isdir(p):
            continue
        stamp = m.get(d)
        if not stamp:                          # 보관일 미기록 → 오늘로 스탬프하고 보존
            m[d] = td.isoformat()
            print("  %-13s 보관일 미기록 → %s 로 기록(보존)" % (d, m[d]))
            kept += 1
            continue
        age = (td - datetime.date.fromisoformat(stamp)).days
        if age >= KEEP_DAYS:
            sz = sum(os.path.getsize(x) for x in glob.glob(os.path.join(p, "*")))
            print("  🗑️ %-13s 보관 %s (%d일 경과) · %s %s"
                  % (d, stamp, age, human(sz), "(dry-run)" if dry else "삭제"))
            if not dry:
                shutil.rmtree(p)
                m.pop(d, None)
            gone += 1
            freed += sz
        else:
            kept += 1
    if not dry:
        save_meta(m)
    print("  ─ 삭제 %d · 보존 %d · 확보 %s%s"
          % (gone, kept, human(freed), " (dry-run — 실제 삭제 안 함)" if dry else ""))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    args = sys.argv[1:]
    today = None
    if "--today" in args:
        i = args.index("--today")
        today = args[i + 1]
        del args[i:i + 2]
    dry = "--dry-run" in args
    if dry:
        args.remove("--dry-run")
    c = args[0]
    if c == "put":
        put(args[1], args[2:], today)
    elif c == "putov":
        put("_overflow", args[1:], today)
    elif c == "ls":
        cmd_ls(args[1] if len(args) > 1 else None, today)
    elif c == "prune":
        cmd_prune(dry, today)
    else:
        print(__doc__)
        sys.exit(1)
