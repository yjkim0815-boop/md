#!/usr/bin/env python3
"""팀 워크로그 수집 도구.

  python wl.py day  <응답파일> <YYYY-MM-DD>      # ★ 하루치 응답 병합 (정본 경로)
  python wl.py seal <월요일> [상태]              # 7일 수집 확인 후 주차 확정
  python wl.py overflow <json...>                # /issue/{key}/worklog 응답 병합
  python wl.py summary                           # SUMMARY.md 재생성
  python wl.py viewer                            # viewer/data.js 생성 (호출 0)
  python wl.py status                            # 진척 현황 (호출 0)
  python wl.py week <응답파일> <월요일> [상태]   # (구) 주 단위 일괄 — 타임아웃 위험

기존 data/*.json 을 항상 베이스로 읽으므로 **증분 병합**이다.
임시 파일이 사라져도 md 안의 데이터만 있으면 이어서 작업할 수 있다.
규칙 정본은 ../INDEX.md.
"""
import sys, os, json, collections, datetime

# Windows 콘솔 기본 인코딩(cp949)에서는 이모지·일부 기호 출력이 UnicodeEncodeError 로 죽는다.
# 실제로 2026-08-07 오버플로 안내(🔴) 출력에서 터졌다 — 저장은 끝난 뒤라 유실은 없었지만
# 트레이스백이 남고 남은 안내가 잘린다. 표준출력을 UTF-8 로 바꾸고, 그래도 못 그리는 문자는
# 대체 문자로 흘려보낸다(도구가 출력 때문에 멈추면 안 된다).
for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DOW = ["월", "화", "수", "목", "금", "토", "일"]
TODAY = datetime.date.today().isoformat()

BY_ID = {m["accountId"]: m
         for m in json.load(open(os.path.join(ROOT, "roster.json"), encoding="utf-8"))["members"]}


def jload(p):
    """BOM 유무 무관 로드 (PowerShell Out-File 은 BOM 을 붙인다)."""
    return json.load(open(p, encoding="utf-8-sig"))


def text_of(cm):
    out = []
    def w(n):
        if isinstance(n, dict):
            if n.get("type") == "text":
                out.append(n.get("text", ""))
            for v in n.values():
                w(v)
        elif isinstance(n, list):
            for v in n:
                w(v)
    w(cm)
    return " ".join(out).strip()


def monday_of(d):
    return (d - datetime.timedelta(days=d.weekday())).isoformat()


def load_weeks():
    weeks, meta = collections.defaultdict(dict), {}
    if not os.path.isdir(DATA):
        return weeks, meta
    for fn in sorted(os.listdir(DATA)):
        d = jload(os.path.join(DATA, fn))
        meta[d["week"]] = {"status": d["status"], "note": d.get("note", ""),
                           "collectedDays": set(d.get("collectedDays", []))}
        for e in d["entries"]:
            weeks[d["week"]][e["worklogId"]] = e
    return weeks, meta


def rec_of(w, key, summary, project):
    """워크로그 1건 → 정규화 레코드. 로스터 외 작성자면 None."""
    a = w.get("author") or {}
    aid = a.get("accountId")
    if aid not in BY_ID:                       # 정합성 ① 작성자 재필터
        return None
    st = (w.get("started") or "")[:10]
    if not st:
        return None
    dt = datetime.date.fromisoformat(st)
    sec = w.get("timeSpentSeconds") or 0
    started = w.get("started") or ""
    return {"worklogId": str(w.get("id")), "date": st, "dow": DOW[dt.weekday()],
            "startedAt": started[:19] if started else None,   # 2026-06-01T09:00:00
            "timeOfDay": started[11:16] if started else None,  # 09:00
            "createdAt": (w.get("created") or "")[:19] or None,
            "author": BY_ID[aid]["name"], "accountId": aid,
            "authorEmail": BY_ID[aid]["email"],
            "seconds": sec, "hours": round(sec / 3600, 2),
            "issueKey": key, "project": project, "summary": summary,
            "comment": text_of(w.get("comment") or {})}


def save(weeks, meta):
    os.makedirs(DATA, exist_ok=True)
    for mon, recs in weeks.items():
        d0 = datetime.date.fromisoformat(mon)
        rows = sorted(recs.values(), key=lambda r: (r["date"], r["author"], r["issueKey"]))
        m = meta.get(mon, {"status": "부분", "note": "오버플로 이슈 유입분만 — search 미실행"})
        obj = {"week": mon,
               "range": [mon, (d0 + datetime.timedelta(days=6)).isoformat()],
               "status": m["status"], "collected": TODAY,
               "collectedDays": sorted(m.get("collectedDays", [])),
               "count": len(rows),
               "hours": round(sum(r["seconds"] for r in rows) / 3600, 2),
               "note": m.get("note", ""), "entries": rows}
        with open(os.path.join(DATA, mon + ".json"), "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)   # 정합성 ④
    sync_manifest()


def sync_manifest():
    """data 정본을 현황판용 manifest 집계에 즉시 반영한다."""
    path = os.path.join(ROOT, "manifest.json")
    if not os.path.exists(path):
        return

    manifest = jload(path)
    weeks = manifest.setdefault("weeks", {})
    for fn in os.listdir(DATA):
        d = jload(os.path.join(DATA, fn))
        week = weeks.setdefault(d["week"], {})
        week.update({"status": d["status"], "count": d["count"],
                     "hours": d["hours"], "roster": len(BY_ID),
                     "collected": d["collected"], "collectedDays": d["collectedDays"]})

    months = manifest.setdefault("months", {})
    grouped = collections.defaultdict(list)
    for week, value in weeks.items():
        grouped[week[:7]].append((week, value))
    for month, items in grouped.items():
        old = months.get(month, {})
        months[month] = {"status": old.get("status", "대기"),
                         "weeks": [week for week, _ in sorted(items)],
                         "weekCount": len(items),
                         "count": sum(item.get("count", 0) for _, item in items),
                         "hours": round(sum(item.get("hours", 0) for _, item in items), 2),
                         "confirmedAt": old.get("confirmedAt")}

    manifest["updated"] = TODAY
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def ingest(nodes, lo, hi):
    """응답 노드에서 로스터·기간 필터를 적용해 (레코드목록, 잘린이슈목록) 반환."""
    recs, truncated = [], []
    for n in nodes:
        f = n.get("fields", n)
        k, su = n.get("key"), (f.get("summary") or "")
        pr = (f.get("project") or {}).get("key")
        wl = f.get("worklog") or {}
        if not isinstance(wl, dict):
            continue
        got, tot = wl.get("worklogs", []), wl.get("total")
        if tot is not None and tot > len(got):
            truncated.append((k, tot, su))
        for w in got:
            r = rec_of(w, k, su, pr)
            if r:
                recs.append(r)
    return recs, truncated


def report_overflow(truncated):
    cpath = os.path.join(ROOT, "issue-cache.json")
    cache = jload(cpath) if os.path.exists(cpath) else {}
    need = []
    for k, tot, su in truncated:
        c = cache.get(k)
        if c is None:
            need.append((k, tot, su, "신규"))
        elif c["total"] != tot:
            need.append((k, tot, su, "변경 %s→%s" % (c["total"], tot)))
    print("\n오버플로 %d개 · 캐시 보유 %d개" % (len(truncated), len(cache)))
    if need:
        print("  🔴 추가 호출 %d회 필요:" % len(need))
        for k, tot, su, why in need:
            print("     %-12s total=%-4s [%s] %s" % (k, tot, why, su[:36]))
        print("\n  " + " ".join(k for k, _, _, _ in need))
    else:
        print("  ✅ 전부 캐시 적중 — 추가 호출 0회")


def cmd_day(resp, day):
    """하루치 응답을 병합한다. 주차 상태는 건드리지 않고 collectedDays 만 채운다."""
    weeks, meta = load_weeks()
    before = sum(len(v) for v in weeks.values())
    dt = datetime.date.fromisoformat(day)
    mon = monday_of(dt)

    d = jload(resp)
    recs, truncated = ingest(d["issues"]["nodes"], dt, dt)
    inday = 0
    for r in recs:                       # 기간 밖(오버플로 유입)도 각자 주차로 보낸다
        weeks[monday_of(datetime.date.fromisoformat(r["date"]))][r["worklogId"]] = r
        if r["date"] == day:
            inday += 1

    m = meta.setdefault(mon, {"status": "수집중", "note": "일별 수집 진행 중"})
    days = set(m.get("collectedDays", []))
    days.add(day)
    m["collectedDays"] = days
    if m["status"] == "부분":
        m["status"] = "수집중"
    save(weeks, meta)

    tgt = [r for r in weeks[mon].values() if r["date"] == day]
    print("%s (%s) · 이슈 %d개" % (day, DOW[dt.weekday()], len(d["issues"]["nodes"])))
    print("  당일 팀 엔트리: %d건 / %.1f h"
          % (len(tgt), sum(r["seconds"] for r in tgt) / 3600))
    by = collections.Counter()
    for r in tgt:
        by[r["author"]] += r["seconds"]
    for a, s in by.most_common():
        print("     %-5s %5.1f h" % (a, s / 3600))
    print("  전체: %d건 → %d건" % (before, sum(len(v) for v in weeks.values())))
    have = sorted(days)
    need7 = [(dt - datetime.timedelta(days=dt.weekday()) + datetime.timedelta(days=i)).isoformat()
             for i in range(7)]
    miss = [x for x in need7 if x not in days]
    print("  주차 %s 수집일: %d/7  %s" % (mon, len(have), "완료 → seal 가능" if not miss else "미수집 " + ", ".join(miss)))
    report_overflow(truncated)


def cmd_seal(monday, status="확정"):
    """7일치가 모두 모였는지 확인하고 주차 상태를 확정한다."""
    weeks, meta = load_weeks()
    if monday not in weeks:
        print("🔴 %s 주차 데이터가 없다." % monday)
        return
    d0 = datetime.date.fromisoformat(monday)
    need7 = [(d0 + datetime.timedelta(days=i)).isoformat() for i in range(7)]
    days = set(meta[monday].get("collectedDays", []))
    miss = [x for x in need7 if x not in days]
    if miss:
        print("🔴 미수집 %d일 남음: %s" % (len(miss), ", ".join(miss)))
        print("   그래도 확정하려면: wl.py seal %s %s --force" % (monday, status))
        return
    meta[monday]["status"] = status
    meta[monday]["note"] = ""
    save(weeks, meta)
    v = weeks[monday]
    print("✅ %s → %s · %d건 / %.1f h"
          % (monday, status, len(v), sum(r["seconds"] for r in v.values()) / 3600))


def cmd_week(resp, monday, status="확정"):
    weeks, meta = load_weeks()
    before_n = sum(len(v) for v in weeks.values())
    before_w = set(weeks)

    d = jload(resp)
    nodes = d["issues"]["nodes"]
    page = d["issues"].get("pageInfo", {})
    d0 = datetime.date.fromisoformat(monday)
    d6 = d0 + datetime.timedelta(days=6)

    truncated, added, spill_n = [], 0, 0
    for n in nodes:
        f = n.get("fields", n)
        k, su = n.get("key"), (f.get("summary") or "")
        pr = (f.get("project") or {}).get("key")
        wl = f.get("worklog") or {}
        if not isinstance(wl, dict):
            continue
        got = wl.get("worklogs", [])
        tot = wl.get("total")
        if tot is not None and tot > len(got):
            truncated.append((k, tot, su))
        for w in got:
            r = rec_of(w, k, su, pr)
            if not r:
                continue
            mon = monday_of(datetime.date.fromisoformat(r["date"]))
            weeks[mon][r["worklogId"]] = r
            added += 1
            if not (d0 <= datetime.date.fromisoformat(r["date"]) <= d6):
                spill_n += 1

    meta[monday] = {"status": status, "note": ""}
    save(weeks, meta)

    print("주차 %s (%s~%s) · 이슈 %d개 · hasNextPage=%s"
          % (monday, monday, d6, len(nodes), page.get("hasNextPage")))
    tgt = weeks[monday]
    print("  대상 주차: %d건 / %.1f h  → 상태 %s"
          % (len(tgt), sum(r["seconds"] for r in tgt.values()) / 3600, status))
    by = collections.Counter()
    for r in tgt.values():
        by[r["author"]] += r["seconds"]
    for a, s in by.most_common():
        print("     %-5s %5.1f h" % (a, s / 3600))
    print("  기간밖(타 주차 분배): %d건 · 신규 주차 %d개"
          % (spill_n, len(set(weeks) - before_w)))
    print("  전체: %d건 → %d건" % (before_n, sum(len(v) for v in weeks.values())))

    cpath = os.path.join(ROOT, "issue-cache.json")
    cache = jload(cpath) if os.path.exists(cpath) else {}
    need = []
    for k, tot, su in truncated:
        c = cache.get(k)
        if c is None:
            need.append((k, tot, su, "신규"))
        elif c["total"] != tot:
            need.append((k, tot, su, "변경 %s→%s" % (c["total"], tot)))
    print("\n오버플로 %d개 · 캐시 보유 %d개" % (len(truncated), len(cache)))
    if need:
        print("  🔴 추가 호출 %d회 필요:" % len(need))
        for k, tot, su, why in need:
            print("     %-12s total=%-4s [%s] %s" % (k, tot, why, su[:36]))
        print("\n  " + " ".join(k for k, _, _, _ in need))
    else:
        print("  ✅ 전부 캐시 적중 — 추가 호출 0회")


def cmd_overflow(paths):
    weeks, meta = load_weeks()
    before = sum(len(v) for v in weeks.values())
    cpath = os.path.join(ROOT, "issue-cache.json")
    cache = jload(cpath) if os.path.exists(cpath) else {}

    # 이슈 메타는 기존 레코드에서 회수 (응답에는 summary 가 없다)
    imeta = {}
    for v in weeks.values():
        for r in v.values():
            imeta[r["issueKey"]] = (r["summary"], r["project"])

    for p in paths:
        key = os.path.splitext(os.path.basename(p))[0]
        d = jload(p)
        su, pr = imeta.get(key, ("", "WORK"))
        cache[key] = {"total": d.get("total"), "lastFetched": TODAY}
        n = 0
        for w in d.get("worklogs", []):
            r = rec_of(w, key, su, pr)
            if not r:
                continue
            weeks[monday_of(datetime.date.fromisoformat(r["date"]))][r["worklogId"]] = r
            n += 1
        print("  %-12s total=%-4s 팀 엔트리 %d건" % (key, d.get("total"), n))

    save(weeks, meta)
    json.dump(cache, open(cpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("전체: %d건 → %d건 · 캐시 %d개"
          % (before, sum(len(v) for v in weeks.values()), len(cache)))


def cmd_status(today=None):
    """채팅방에 그대로 붙일 현황판.

    열 구성은 2026-08-05 확정 — **주차(월) · 주차 · 주간 · 월간 · 건수 · 시간 · 인원 · 비고**.
    `시각%`·`기준(로스터)`·`로우` 는 뺐다. 로스터 17명·로우 보관이 이제 전제라
    매 행에 다시 표시할 정보가 아니다(예외 상황만 비고에 적는다).
    """
    R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mf = json.load(open(os.path.join(R, "manifest.json"), encoding="utf-8"))
    WI = {"확정": "✅", "부분": "🟡", "진행": "🔵", "수집중": "🔵"}
    MI = {"확정": "✅", "대기": "⏳"}

    def isolabel(s):
        d = datetime.date.fromisoformat(s)
        y, w, _ = d.isocalendar()
        return "W%02d" % w if y == 2026 else "%d-W%02d" % (y, w)

    # 🔴 표시 대상 = **확정 + 진행 주차만** (2026-08-06 사용자 확정)
    # 수집·저장은 전부 유지하되(부분 주차 포함), 현황판에는 확정/진행만 올린다.
    # 부분 주차는 오버플로 버킷이 과거·미래로 1~2건씩 흩뿌린 결과라 진척을 오독하게 만든다.
    SHOW = ("확정", "진행")
    shown, hidden = [], []
    for w in sorted(mf["weeks"]):
        d = json.load(open(os.path.join(R, "data", w + ".json"), encoding="utf-8"))
        cd = len(d.get("collectedDays", []))
        (shown if d["status"] in SHOW else hidden).append((w, d, cd))

    print("%-12s %-9s %-7s %-7s %6s %9s %5s %6s  %s"
          % ("주차(월)", "주차", "주간", "월간", "건수", "시간", "인원", "수집", "비고"))
    print("-" * 82)
    for w, d, cd in shown:
        v = mf["weeks"][w]
        ms = mf["months"][w[:7]]["status"]
        ppl = len({e["author"] for e in d["entries"]})
        note = "🔒 보류" if v.get("manualOverride") else ""
        print("%-12s %-9s %s%-5s %s%-5s %5d %8.1fh %4d %5s  %s"
              % (w, isolabel(w), WI[v["status"]], v["status"],
                 MI[ms], ms, v["count"], v["hours"], ppl, "%d/7" % cd, note))
    print("-" * 82)
    if hidden:
        hc = sum(d["count"] for _, d, _ in hidden)
        hh = sum(d["hours"] for _, d, _ in hidden)
        print("⚪ 미표시(부분) %d주 · %d건 · %.1fh — 데이터는 보관 중. 수집·확정되면 표에 올라온다"
              % (len(hidden), hc, hh))
    # 이하 집계는 **표시 대상(shown) 기준**이다. 유입·미래 주차를 섞으면 수치가 부풀려진다.
    keys = [w for w, _, _ in shown]
    c = collections.Counter(mf["weeks"][w]["status"] for w in keys)
    print("주간: " + " · ".join("%s%s %d주" % (WI[k], k, n) for k, n in c.most_common()))

    print("\n=== 월간 ===")
    mo = collections.defaultdict(lambda: [0, 0, 0.0])
    for w, d, _ in shown:
        m = w[:7]
        mo[m][0] += 1
        mo[m][1] += d["count"]
        mo[m][2] += d["hours"]
    for m in sorted(mo):
        wc, cc, hh = mo[m]
        ms = mf["months"].get(m, {}).get("status", "대기")
        print("  %-9s %s%-4s %2d주 %5d건 %9.1fh" % (m, MI[ms], ms, wc, cc, hh))

    tot = sum(d["count"] for _, d, _ in shown)
    hrs = sum(d["hours"] for _, d, _ in shown)
    conf = [w for w in keys if mf["weeks"][w]["status"] == "확정"]
    print("\n수집 %d주 · %d건 · %.1fh" % (len(shown), tot, hrs))
    print("확정 %d주 · %d건 · %.1fh"
          % (len(conf), sum(mf["weeks"][w]["count"] for w in conf),
             sum(mf["weeks"][w]["hours"] for w in conf)))

    # 팀별 집계 — 로스터는 3개 팀에 걸쳐 있다(2026-08-06 Jira 그룹 조회로 확인)
    roster = json.load(open(os.path.join(R, "roster.json"), encoding="utf-8"))
    TEAM = {m["name"]: (m.get("team") or "미상") for m in roster["members"]}
    agg = collections.defaultdict(lambda: [0, 0.0, set()])
    for _, d, _ in shown:
        for e in d["entries"]:
            t2 = TEAM.get(e["author"], "미상")
            agg[t2][0] += 1
            agg[t2][1] += e["hours"]
            agg[t2][2].add(e["author"])
    if agg:
        print("\n=== 팀별 ===")
        head = collections.Counter(TEAM.values())
        for t2, (c2, h2, who) in sorted(agg.items(), key=lambda x: -x[1][1]):
            print("  %-12s %4d건 %9.1fh · 기록 %2d명 / 로스터 %d명"
                  % (t2, c2, h2, len(who), head.get(t2, 0)))

    t = datetime.date.fromisoformat(today) if today else datetime.date.today()
    nowmon = t - datetime.timedelta(days=t.weekday())
    line = (nowmon - datetime.timedelta(weeks=2)).isoformat()
    cand = [w for w, v in mf["weeks"].items() if v["status"] != "확정" and w <= line]
    if cand:
        print("다음 대상: %s (%s)" % (max(cand), isolabel(max(cand))))
    print("누적 호출 %d회 / %d회차"
          % (sum(r["calls"]["total"] for r in mf["runs"]), len(mf["runs"])))


def cmd_summary():
    weeks, meta = load_weeks()
    rows = [r for v in weeks.values() for r in v.values()]
    per, pc = collections.defaultdict(float), collections.Counter()
    proj, iss, isum, dow = collections.defaultdict(float), collections.defaultdict(float), {}, collections.defaultdict(float)
    for r in rows:
        per[r["author"]] += r["seconds"]; pc[r["author"]] += 1
        proj[r["project"] or "-"] += r["seconds"]
        iss[r["issueKey"]] += r["seconds"]; isum[r["issueKey"]] = r["summary"]
        dow[r["dow"]] += r["seconds"]
    L = []
    A = L.append
    A("---"); A("문서유형: SUMMARY"); A("프로젝트: 공통(개인 영역)")
    A("작성일: 2026-08-04"); A("최종수정: %s" % TODAY); A("작성자: dominic"); A("상태: 진행중")
    A("요약: 모바일개발팀 워크로그 누적 집계 — 수집된 주차 전체 롤업. tools/wl.py 가 자동 생성")
    A("---"); A("")
    A("# 📈 팀 워크로그 누적 집계"); A("")
    A("> 🤖 **`tools/wl.py summary` 가 생성한다. 직접 고치지 않는다.**")
    A("> 원본 [data/](./data) · 진척 [manifest.json](./manifest.json) · 규칙 [INDEX.md](./INDEX.md)")
    A("> ⚠️ **🟡 부분 주차는 과소 집계다.** 오버플로 유입분만 있고 search 미실행이라 확정 주차와 나란히 비교하면 안 된다.")
    A("")
    A("## 총계"); A(""); A("| 항목 | 값 |"); A("|---|---:|")
    A("| 엔트리 | **%d건** |" % len(rows))
    A("| 시간 | **%.1f h** (%.1f MD) |" % (sum(per.values())/3600, sum(per.values())/3600/8))
    A("| 주차 | %d개 |" % len(weeks)); A("| 인원 | %d명 |" % len(per)); A("")
    A("## 주차별"); A(""); A("| 주차(월) | 상태 | 엔트리 | 시간 |"); A("|---|---|---:|---:|")
    for w in sorted(weeks, reverse=True):
        st = meta[w]["status"]
        ic = {"확정": "✅", "현행화중": "🔄", "부분": "🟡"}.get(st, "")
        s = sum(r["seconds"] for r in weeks[w].values()) / 3600
        A("| %s | %s %s | %d | %.1f h |" % (w, ic, st, len(weeks[w]), s))
    A("")
    A("## 인원별 (전 주차 누적)"); A("")
    A("| 팀원 | 시간 | 엔트리 | 평균/건 |"); A("|---|---:|---:|---:|")
    for a, s in sorted(per.items(), key=lambda x: -x[1]):
        A("| %s | **%.1f h** | %d | %.1f h |" % (a, s/3600, pc[a], s/3600/pc[a]))
    A("")
    A("## 요일별"); A(""); A("| 요일 | 시간 |"); A("|---|---:|")
    for d_ in DOW:
        if d_ in dow:
            A("| %s | %.1f h |" % (d_, dow[d_]/3600))
    wk = sum(dow.get(x, 0) for x in ("토", "일")) / 3600
    A("")
    if wk > 0:
        A("> 🔴 **주말 %.1f h** 가 기록돼 있다. 월~금만 수집했다면 통째로 누락됐을 데이터다." % wk)
    else:
        A("> ℹ️ **현재까지 수집분에 주말 기록은 없다(0 h).** 주말 수집은 유지한다 — 추가 비용이 0이고, 한 건이라도 생기면 그 자체가 신호다.")
    A("")
    A("## 프로젝트별"); A(""); A("| 프로젝트 | 시간 |"); A("|---|---:|")
    for p, s in sorted(proj.items(), key=lambda x: -x[1]):
        A("| `%s` | %.1f h |" % (p, s/3600))
    A("")
    A("## 상위 이슈 15"); A(""); A("| 이슈 | 시간 | 제목 |"); A("|---|---:|---|")
    for k, s in sorted(iss.items(), key=lambda x: -x[1])[:15]:
        A("| `%s` | %.1f h | %s |" % (k, s/3600, isum[k][:52]))
    A(""); A("## 참고")
    A("- [INDEX.md](./INDEX.md) · [roster.json](./roster.json) · [manifest.json](./manifest.json)")
    A("- [KB 루트 README](../../README.md)")
    open(os.path.join(ROOT, "SUMMARY.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("SUMMARY.md 재생성 — %d건 / %.1f h / 주차 %d개"
          % (len(rows), sum(per.values())/3600, len(weeks)))


def cmd_viewer():
    """viewer/data.js 생성 — file:// 로 열리므로 fetch 가 아니라 JS 변수로 심는다."""
    weeks, meta = load_weeks()
    ros = json.load(open(os.path.join(ROOT, "roster.json"), encoding="utf-8"))
    mfp = os.path.join(ROOT, "manifest.json")
    mf = jload(mfp) if os.path.exists(mfp) else {"weeks": {}}

    # 🔴 캘린더에는 **확정 + 진행 주차만** 내보낸다 (2026-08-06 사용자 확정).
    # data/*.json 에는 부분 주차도 그대로 보관한다 — 여기서 걸러내기만 한다.
    SHOW = ("확정", "진행")
    keep = [mon for mon in weeks if meta[mon]["status"] in SHOW]
    skipped = len(weeks) - len(keep)

    rows = []
    for mon in sorted(keep):
        for e in sorted(weeks[mon].values(), key=lambda r: (r["date"], r.get("timeOfDay") or "~", r["author"])):
            rows.append([mon, e["date"], e["dow"], e.get("timeOfDay"), e["seconds"] // 60,
                         e["author"], e["issueKey"], e["project"] or "",
                         e["summary"] or "", e["comment"] or ""])
    wk = []
    for mon in sorted(keep, reverse=True):
        m = mf.get("weeks", {}).get(mon, {})
        vals = weeks[mon].values()
        timed = sum(1 for r in vals if r.get("timeOfDay"))
        wk.append({"week": mon, "status": meta[mon]["status"],
                   "count": len(vals),
                   "hours": round(sum(r["seconds"] for r in vals) / 3600, 2),
                   "roster": m.get("roster"),
                   "timed": timed})
    out = {"generated": TODAY,
           "fields": ["week", "date", "dow", "time", "min", "author", "issue", "project", "summary", "comment"],
           "roster": [{"name": m["name"], "email": m["email"],
                    "team": m.get("team") or "미상",
                    "roles": m.get("roles", [])} for m in ros["members"]],
           "weeks": wk, "entries": rows}
    vdir = os.path.join(ROOT, "viewer")
    os.makedirs(vdir, exist_ok=True)
    p = os.path.join(vdir, "data.js")
    with open(p, "w", encoding="utf-8") as f:
        f.write("window.WL = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print("viewer/data.js 생성 — %d건 / 주차 %d개 / %.0f KB"
          % (len(rows), len(wk), os.path.getsize(p) / 1024))
    if rows:
        print("  시각 보유 %d건 (%.1f%%)"
              % (sum(w["timed"] for w in wk), sum(w["timed"] for w in wk) / len(rows) * 100))
    if skipped:
        print("  ⚪ 부분 주차 %d개 제외 (data/ 에는 보관)" % skipped)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    c = sys.argv[1]
    if c == "day":
        cmd_day(sys.argv[2], sys.argv[3])
    elif c == "seal":
        cmd_seal(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "확정")
    elif c == "week":
        cmd_week(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "확정")
    elif c == "overflow":
        cmd_overflow(sys.argv[2:])
    elif c == "viewer":
        cmd_viewer()
    elif c == "summary":
        cmd_summary()
    elif c == "status":
        cmd_status(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print(__doc__); sys.exit(1)
