#!/usr/bin/env python3
"""남아 있는 원본 응답에서 startedAt / timeOfDay / createdAt 을 회수해 채운다.

  python backfill.py <원본이 있는 폴더> [...]

`data/*.json` 의 기존 엔트리는 유지하고 **비어 있는 시각 필드만** 채운다.
API 호출 0회. 원본이 없어 못 채운 건은 `null` 로 남고 화면에서 '시간 미지정'으로 분리된다.
"""
import sys, os, json, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def jload(p):
    try:
        return json.load(open(p, encoding="utf-8-sig"))
    except Exception:
        return None


def harvest(paths):
    """원본 트리를 훑어 worklogId → (started, created) 맵을 만든다."""
    found = {}

    def walk(o):
        if isinstance(o, dict):
            if "id" in o and "started" in o and "timeSpentSeconds" in o:
                found[str(o["id"])] = (o.get("started"), o.get("created"))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    n = 0
    for base in paths:
        pats = [base] if os.path.isfile(base) else [
            os.path.join(base, "*.json"), os.path.join(base, "*.txt"),
            os.path.join(base, "**", "*.json"), os.path.join(base, "**", "*.txt")]
        for pat in pats:
            for f in glob.glob(pat, recursive=True):
                d = jload(f)
                if d:
                    n += 1
                    walk(d)
    print("원본 %d개 스캔 · worklogId %d건 회수" % (n, len(found)))
    return found


def main(paths):
    found = harvest(paths)
    filled = already = miss = 0
    byweek = collections.Counter()
    for fn in sorted(os.listdir(DATA)):
        p = os.path.join(DATA, fn)
        d = jload(p)
        dirty = False
        for e in d["entries"]:
            if e.get("startedAt"):
                already += 1
                continue
            m = found.get(e["worklogId"])
            if not m or not m[0]:
                e.setdefault("startedAt", None)
                e.setdefault("timeOfDay", None)
                e.setdefault("createdAt", None)
                miss += 1
                byweek[d["week"]] += 1
                dirty = True
                continue
            st, cr = m
            e["startedAt"] = st[:19]
            e["timeOfDay"] = st[11:16]
            e["createdAt"] = (cr or "")[:19] or None
            filled += 1
            dirty = True
        if dirty:
            # 키 순서를 고정해 diff 를 읽기 쉽게 유지한다
            order = ["worklogId", "date", "dow", "startedAt", "timeOfDay", "createdAt",
                     "author", "accountId", "authorEmail", "seconds", "hours",
                     "issueKey", "project", "summary", "comment"]
            d["entries"] = [{k: e.get(k) for k in order} for e in d["entries"]]
            json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    tot = filled + already + miss
    print("\n채움 %d · 기존보유 %d · 미회수 %d / 전체 %d (%.1f%% 확보)"
          % (filled, already, miss, tot, (filled + already) / tot * 100))
    if byweek:
        print("\n미회수 주차:")
        for w, c in byweek.most_common():
            print("   %s  %d건" % (w, c))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
