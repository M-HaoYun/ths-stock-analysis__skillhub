# -*- coding: utf-8 -*-
"""构建自检器：把「数据区替换 + 渲染产物」这一链路的坑变成可执行校验。

为什么要有它
------------
本项目一半的坑不是「接口限制」，而是**自己做数据版脚本时的手滑**，且多为**静默失败**
（不报错、数字看着正常）：数据区漏了 `NAME = ` 前缀、`DATE/WEEKDAY` 没换导致文件名与数据错配、
模板数据区里的变量没重新定义 → 跑到渲染段才 NameError、中文引号写成裸 `"` 导致 SyntaxError、
`re.sub` 替换串含反斜杠报 bad escape……靠记忆和事后 grep 一个个查，成本极高。
本脚本把这些判据固化下来，**构建完跑一次即可**，不必依赖记忆。

用法
----
    python check_build.py --builder build_xxx.py                    # 构建器静态检查
    python check_build.py --script  gen_xxx_0917.py --template gen_xxx.py
    python check_build.py --html    产物.html [--hist hist.json] [--expect-date 2026-09-17]
    python check_build.py --codes   codes.txt                       # CLI 参数清单文件 CRLF 检查
    python check_build.py --auto    <任意路径...>                    # 按扩展名自动分派
    python check_build.py --selftest                                # 自检（用故意写坏的样本证明每条检查有效）

退出码：0=全过 / 1=有 ❌ / 2=只有 ⚠️

校验项与对应坑
--------------
| 检查 | 内容 | 对应坑 |
|---|---|---|
| B1 | 构建器用 `re.sub(pat, "字符串")` 而非 lambda | 53 |
| B2 | 构建器里残留与本脚本 DATE 不一致的日期字面量 | 33 |
| B3 | 构建器 `TPL_PATH` 指向不存在的文件 | — |
| B4 | 构建器里出现被批量引号替换改坏的 `「, 」` 之类 | 59 |
| S1 | 生成脚本能否编译（裸 ASCII 双引号会 SyntaxError） | 58 |
| S2 | **未绑定名检测**（数据区漏变量/漏 `NAME = ` 前缀/f-string 引用构建器变量） | 42 / 44 / 52 / 54 |
| S3 | 数据区里出现转义的裸引号 `\\"`（编译能过但会渲染出裸引号） | 58 |
| S4 | 生成脚本 vs 模板的变量集合差异（少了=❌，多了=ℹ️ 常为拼写错） | 42 / 44 / 54 / 60 |
| S5 | `DATE` / `WEEKDAY` 是否仍是模板默认值 | 55 |
| H1 | `<title>` 与产物文件名同口径 | 55 |
| H2 | 占位符 `__X__` 残留 | — |
| H3 | 残留 markdown `**加粗**`（HTML 不解析，会原样显示星号） | 46 |
| H4 | `[MISSING]` 计数（超过 --allow-missing 才 ⚠️） | — |
| H5 | 模板旧特征值残留（--old 给关键词） | 27② / 13⑦ / 16⑦ |
| H6 | 走势图点数（速览卡应恒为 252） | 61 |
| C1 | HIST 只有 6 个字段、键名正确 | 56① |
| C2 | HIST 价格已 round(x,2)（未 round 的 17 位浮点会撑大产物） | 56② |
| C3 | HIST 日期升序/唯一/根数（<252 会触发模板 WARN） | 61 |
| K1 | 喂 CLI 的参数清单文件含 `\\r`（CRLF） | 28 |
"""
from __future__ import annotations

import argparse
import ast
import builtins
import io
import json
import os
import py_compile
import re
import sys
import tempfile

OK, WARN, FAIL, INFO = "OK", "WARN", "FAIL", "INFO"
_ICON = {OK: "✅", WARN: "⚠️ ", FAIL: "❌", INFO: "ℹ️ "}


class Report:
    def __init__(self, title: str):
        self.title = title
        self.items: list[tuple[str, str, str]] = []

    def add(self, level: str, tag: str, msg: str):
        self.items.append((level, tag, msg))

    def dump(self) -> int:
        n_fail = sum(1 for lv, _, _ in self.items if lv == FAIL)
        n_warn = sum(1 for lv, _, _ in self.items if lv == WARN)
        print(f"\n{'=' * 72}\n{self.title}\n{'=' * 72}")
        for lv, tag, msg in self.items:
            print(f"  {_ICON[lv]} [{tag}] {msg}")
        if not self.items:
            print("  （无可检查项）")
        print(f"\n  小结：❌ {n_fail} / ⚠️ {n_warn} / 共 {len(self.items)} 项")
        return 1 if n_fail else (2 if n_warn else 0)


# --------------------------------------------------------------------------- #
# AST 工具
# --------------------------------------------------------------------------- #
_BUILTINS = set(dir(builtins)) | {"__name__", "__file__", "__doc__", "self", "cls"}


def _coverage(needle: str, hay: str) -> float:
    """needle 的字符（多重集）有多大比例出现在 hay 里——用于判断 title 是否覆盖了文件名主体。"""
    if not needle:
        return 1.0
    from collections import Counter
    a, b = Counter(needle), Counter(hay)
    hit = sum(min(v, b.get(ch, 0)) for ch, v in a.items())
    return hit / sum(a.values())


def _target_names(node: ast.AST) -> set[str]:
    """递归收集赋值目标里的名字（含解包、for/with/推导式目标）。"""
    out: set[str] = set()
    if isinstance(node, ast.Name):
        out.add(node.id)
    elif isinstance(node, (ast.Tuple, ast.List)):
        for e in node.elts:
            out |= _target_names(e)
    elif isinstance(node, ast.Starred):
        out |= _target_names(node.value)
    return out


def scan_names(src: str) -> tuple[set[str], set[str]]:
    """返回 (被赋值的名字, 被读取的名字)。

    赋值侧覆盖：Assign / AnnAssign / AugAssign / For / With(as) / 推导式 /
    except as / global / 函数名 / 类名 / import / `globals()["X"] = ...`。
    读取侧覆盖所有 `ast.Name` 的 Load 上下文。
    """
    tree = ast.parse(src)
    assigned: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in tgts:
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) and t.value.id == "globals":
                    # globals()["X"] = ... 形式的动态注入
                    sl = t.slice
                    if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                        assigned.add(sl.value)
                    continue
                assigned |= _target_names(t)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            assigned |= _target_names(node.target)
        elif isinstance(node, ast.comprehension):
            assigned |= _target_names(node.target)
        elif isinstance(node, ast.withitem) and node.optional_vars is not None:
            assigned |= _target_names(node.optional_vars)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            assigned.add(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            assigned.add(node.name)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for a in list(node.args.args) + list(node.args.kwonlyargs) + list(node.args.posonlyargs):
                    assigned.add(a.arg)
                if node.args.vararg:
                    assigned.add(node.args.vararg.arg)
                if node.args.kwarg:
                    assigned.add(node.args.kwarg.arg)
        elif isinstance(node, ast.Lambda):
            for a in list(node.args.args) + list(node.args.kwonlyargs) + list(node.args.posonlyargs):
                assigned.add(a.arg)
        elif isinstance(node, ast.Import):
            for al in node.names:
                assigned.add((al.asname or al.name).split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for al in node.names:
                assigned.add(al.asname or al.name)
        elif isinstance(node, ast.Global) or isinstance(node, ast.Nonlocal):
            assigned |= set(node.names)
    used = {
        n.id for n in ast.walk(tree)
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
    }
    return assigned, used


# --------------------------------------------------------------------------- #
# 构建器检查
# --------------------------------------------------------------------------- #
_DATE8 = re.compile(r"\b(20\d{2})(0[1-9]|1[0-2])([0-2]\d)\b")
_DATE_DASH = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")


def check_builder(path: str) -> Report:
    src = open(path, encoding="utf-8", errors="replace").read()
    rep = Report(f"构建器检查：{os.path.basename(path)}")

    # 本脚本自己的日期基准（取第一个出现的日期字面量作为基准）
    dates = _DATE_DASH.findall(src) + [f"{a}-{b}-{c}" for a, b, c in _DATE8.findall(src)]
    base = dates[0] if dates else None

    # B1 re.sub 的替换串不是 lambda（坑 53）
    for m in re.finditer(r"\.subn?\(\s*([^,]+),\s*([^,)]+)", src):
        repl = m.group(2).strip()
        line = src[: m.start()].count("\n") + 1
        if not (repl.startswith("lambda") or repl.startswith("__") or repl.startswith("_repl")):
            if re.search(r'^["\']', repl) or re.search(r"^\w+\s*$", repl):
                rep.add(WARN, "B1", f"第 {line} 行 `re.sub(..., {repl[:28]}…)` 替换串不是 lambda → "
                                    f"内容含 `\\` 会报 bad escape（坑 53）。写法：`pat.sub(lambda _m, _t=txt: _t, src)`")
    # B2 残留其它日期（坑 33）
    if base:
        others = {d for d in dates if d != base}
        if others:
            rep.add(WARN, "B2", f"本脚本日期基准={base}，但还出现其它日期 {sorted(others)[:6]} → "
                                f"疑似复制旧脚本未替换全（坑 33）。改完必须 grep 全部 open()/json.dump 目标名")
    # B3 TPL_PATH 指向不存在的文件
    for m in re.finditer(r"TPL_PATH\s*=\s*r?[\"']([^\"']+)[\"']", src):
        tgt = m.group(1)
        if not os.path.exists(tgt):
            rep.add(FAIL, "B3", f"TPL_PATH 不存在：{tgt}（skill 目录可能已改名；"
                                f"建议改用 glob 自动定位，见 references/构建个人量化平台指南.md）")
    # B4 批量引号替换改坏的痕迹（坑 59）
    bad = re.findall(r"「\s*,\s*」|「\s*」|「\)|「\]", src)
    if bad:
        rep.add(FAIL, "B4", f"发现 {len(bad)} 处疑似被批量引号替换改坏的 `「, 」`/空引号（坑 59）——"
                            f"合法的元组分隔符 `\", \"` 曾被误换，逐处核对")
    if not rep.items:
        rep.add(OK, "B*", "未发现构建器层面的已知隐患")
    return rep


# --------------------------------------------------------------------------- #
# 生成脚本检查
# --------------------------------------------------------------------------- #
def check_script(path: str, template: str | None, expect_date: str | None) -> Report:
    src = open(path, encoding="utf-8", errors="replace").read()
    rep = Report(f"生成脚本检查：{os.path.basename(path)}")

    # S1 编译（坑 58 的裸引号会在这里暴露）
    try:
        compile(src, path, "exec")
    except SyntaxError as e:
        msg = f"{e.msg}（第 {e.lineno} 行）"
        rep.add(FAIL, "S1", f"无法编译 → 多半是数据区写了裸 ASCII 双引号（坑 58，中文强调改用「」）：{msg}")
        return rep
    except Exception as e:  # pragma: no cover
        rep.add(FAIL, "S1", f"编译异常：{e}")
        return rep

    # S2 未绑定名检测（坑 42/44/52/54）
    try:
        assigned, used = scan_names(src)
    except SyntaxError as e:
        rep.add(FAIL, "S2", f"AST 解析失败：{e}")
        return rep
    unbound = sorted(n for n in used - assigned - _BUILTINS if not n.startswith("__"))
    if unbound:
        rep.add(FAIL, "S2", "存在「被读取但从未赋值」的名字（跑了必 NameError，或数据区漏了 `NAME = ` 前缀）："
                            + ", ".join(unbound[:12]) + ("…" if len(unbound) > 12 else "")
                            + "　→ 坑 42/44/52/54 排查口诀：数据区变量必须带 `NAME = `，"
                              "且模板数据区原有的变量要全部重新定义")
    else:
        rep.add(OK, "S2", "无未绑定名（数据区变量齐全，含 `NAME = ` 前缀）")

    # S3 数据区转义裸引号（坑 58 隐蔽形态）
    trio = re.search(r"={2,}[^\n]*数据[^\n]*={2,}(.+?)(?:={2,}[^\n]*渲染[^\n]*={2,}|# -{2,} 渲染)", src, re.S)
    seg = trio.group(1) if trio else src
    n_esc = len(re.findall(r'\\"', seg))
    if n_esc:
        rep.add(WARN, "S3", f"数据区出现 {n_esc} 处 `\\\"`（会被还原成裸引号，坑 58 的隐蔽形态）——"
                            f"中文强调一律用「」，不要用英文双引号")

    # S5 DATE / WEEKDAY 是否仍是模板默认值（坑 55）
    def _const(name: str, s: str):
        m = re.search(rf'^{name}\s*=\s*[\'"]([^\'"]*)[\'"]', s, re.M)
        return m.group(1) if m else None

    if template and os.path.exists(template):
        tsrc = open(template, encoding="utf-8", errors="replace").read()
        t_date, g_date = _const("DATE", tsrc), _const("DATE", src)
        if t_date and g_date == t_date:
            rep.add(WARN, "S5", f"`DATE` 与模板默认值相同（{g_date}）→ 若这是新一天的数据版脚本说明忘了替换："
                                f"文件名会变成模板日期（坑 55）")
        elif expect_date and g_date and g_date.replace("-", "") != expect_date.replace("-", ""):
            rep.add(FAIL, "S5", f"`DATE`={g_date} 与期望 {expect_date} 不一致 → 产物文件名会错（坑 55）")
        # S4 变量集合比对（坑 42/44/54/60）
        t_assigned, _ = scan_names(tsrc)
        g_assigned, _ = scan_names(src)
        missing = sorted(t_assigned - g_assigned - _BUILTINS)
        extra = sorted(g_assigned - t_assigned - _BUILTINS)
        if missing:
            rep.add(FAIL, "S4", "模板里有、生成脚本里却没有的变量（渲染段会 NameError）："
                                + ", ".join(missing[:14]) + ("…" if len(missing) > 14 else "")
                                + "　→ 数据区是**整段替换**，模板数据区定义的变量必须自己重新定义（坑 42/44）")
        else:
            rep.add(OK, "S4", "生成脚本已覆盖模板的全部变量（数据区整段替换后无缺口）")
        if extra:
            rep.add(INFO, "S4", f"生成脚本多出的变量（{len(extra)} 个，通常是自己算的中间量；"
                                f"若有拼写错会同时出现在 missing 里）：{', '.join(extra[:12])}")
    else:
        if expect_date:
            g_date = _const("DATE", src)
            if g_date and g_date.replace("-", "") != expect_date.replace("-", ""):
                rep.add(FAIL, "S5", f"`DATE`={g_date} ≠ 期望 {expect_date}（坑 55）")
    return rep


# --------------------------------------------------------------------------- #
# 产物 HTML 检查
# --------------------------------------------------------------------------- #
def check_html(path: str, hist: str | None, expect_date: str | None,
               expect_points: int | None, allow_missing: int, old: list[str]) -> Report:
    html = open(path, encoding="utf-8", errors="replace").read()
    fname = os.path.basename(path)
    rep = Report(f"产物检查：{fname}")

    body = re.sub(r"<style.*?</style>|<script.*?</script>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", body)
    text = re.sub(r"\s+", " ", text)

    # H1 title 与文件名同口径（坑 55）
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    title = (m.group(1).strip() if m else "")
    stem = os.path.splitext(fname)[0]
    norm = lambda s: re.sub(r"[\s_\-·|/]+", "", s)  # noqa: E731
    if not title:
        rep.add(FAIL, "H1", "没有 <title>")
    else:
        dm = re.search(r"(\d{8})$", stem)
        core = stem[: dm.start()].rstrip("_-") if dm else stem
        core_norm, title_norm = norm(core), norm(title)
        cov = _coverage(core_norm, title_norm)
        if cov < 0.6:
            rep.add(WARN, "H1", f"title 疑似**缺主体名**：文件名芯=`{core}`，title=`{title}`"
                                f"（主体字符覆盖仅 {cov:.0%}）→ 应为 `{stem}` 的口径（坑 55）")
        elif dm and dm.group(1) not in title_norm and "速览卡" not in title:
            rep.add(WARN, "H1", f"title **缺日期**：文件名带 {dm.group(1)}，但 title=`{title}`（坑 55）"
                                f"；速览卡 title 用「名称 代码 · 速览卡」属既定风格，已豁免")
        else:
            rep.add(OK, "H1", f"title 与文件名同口径（{title}）")
    if expect_date:
        d8 = expect_date.replace("-", "")
        if d8 not in html and expect_date not in html:
            rep.add(WARN, "H1", f"产物里找不到期望日期 {expect_date}（DATE 可能未替换或数据未对齐，坑 55）")

    # H2 占位符残留
    ph = sorted(set(re.findall(r"__[A-Za-z][A-Za-z0-9_]{2,}__", html)))
    if ph:
        rep.add(FAIL, "H2", f"占位符未替换：{', '.join(ph[:10])}{'…' if len(ph) > 10 else ''}")
    else:
        rep.add(OK, "H2", "无占位符残留")

    # H3 markdown 星号（坑 46）
    nstar = html.count("**")
    if nstar:
        rep.add(FAIL, "H3", f"残留 markdown `**` {nstar} 处（HTML 不解析，页面会原样显示星号，坑 46）——改用 <b>")
    else:
        rep.add(OK, "H3", "无 `**` 残留")

    # H4 [MISSING]
    nmiss = len(re.findall(r"\[\s*MISSING\s*\]", text))
    if nmiss > allow_missing:
        rep.add(WARN, "H4", f"[MISSING] {nmiss} 处（上限 {allow_missing}）——确认每处都是真的取不到，"
                            f"而不是漏填")
    else:
        rep.add(OK, "H4", f"[MISSING] {nmiss} 处（≤{allow_missing}）")

    # H5 旧特征值残留
    for kw in old:
        if kw and kw in text:
            rep.add(FAIL, "H5", f"发现旧特征值残留：`{kw}`（换日期/换标的必须 grep 清理，坑 27②/13⑦/16⑦）")

    # H6 走势图点数（坑 61）
    mpts = re.search(r'<polyline points="([^"]+)" fill="none" stroke="#1f3a93" stroke-width="2"', html)
    if mpts:
        n = len(mpts.group(1).split())
        if expect_points and n != expect_points:
            rep.add(WARN, "H6", f"走势图 {n} 个点 ≠ 期望 {expect_points}（速览卡按 252 交易日窗口，坑 61）")
        else:
            rep.add(OK, "H6", f"走势图 {n} 个点")

    # C1-C3 HIST 文件（坑 56 / 61）
    if hist:
        rep2 = check_hist(hist)
        rep.items.extend(rep2.items)
    return rep


def check_hist(path: str) -> Report:
    rep = Report(f"HIST 检查：{os.path.basename(path)}")
    try:
        env = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        rep.add(FAIL, "C0", f"读取失败：{e}")
        return rep
    bars = env["data"].get("item") if isinstance(env.get("data"), dict) else env.get("data")
    if not isinstance(bars, list) or not bars:
        rep.add(FAIL, "C0", "找不到 K 线数组（应走 data 或 data.item）")
        return rep
    keys = set().union(*[set(b.keys()) for b in bars[:50]])
    remote = {"date_ms", "close_price", "high_price", "low_price", "open_price", "volume"}
    if remote <= keys:
        datek, pricek = "date_ms", "close_price"
        rep.add(INFO, "C1", "远端/ETF 结构（data.item[] + *_price）")
    else:
        want = {"date", "open", "high", "low", "close", "volume"}
        extra = sorted(keys - want)
        if extra:
            rep.add(WARN, "C1", f"字段超出 6 个（多出 {extra}）→ 多余字段会进 JSON 甚至 SVG（坑 56①）")
        else:
            rep.add(OK, "C1", "字段恰为 6 个（date/open/high/low/close/volume）")
        datek, pricek = "date", "close"
    # C2 价格是否 round(2)（查全部价格字段，坑 56②）
    if remote <= keys:
        pkeys = ["open_price", "high_price", "low_price", "close_price"]
    else:
        pkeys = ["open", "high", "low", "close"]
    bad, tot = 0, 0
    for b in bars[:400]:
        for k in pkeys:
            v = b.get(k)
            if isinstance(v, float):
                tot += 1
                if len(str(v).split(".")[-1]) > 2:
                    bad += 1
    if bad:
        rep.add(WARN, "C2", f"{bad}/{tot} 个价格小数位 >2（未 round(x,2) → 撑大文本与坐标，坑 56②）")
    else:
        rep.add(OK, "C2", f"价格均已 round(x,2)（查了 {tot} 个值）")
    # C3 日期与根数
    ds = [str(b.get(datek)) for b in bars]
    if len(bars) < 252:
        rep.add(WARN, "C3", f"仅 {len(bars)} 根 < 252 → 速览卡会打 [WARN] 且「近1年涨幅」退化为区间值（坑 61）")
    else:
        rep.add(OK, "C3", f"{len(bars)} 根（≥252，够近一年窗口）")
    return rep


def check_codes(path: str) -> Report:
    rep = Report(f"参数清单 CRLF 检查：{os.path.basename(path)}")
    raw = open(path, "rb").read()
    n = raw.count(b"\r\n")
    if n:
        rep.add(FAIL, "K1", f"含 {n} 处 CRLF → 逐行喂 CLI 时每行会带尾 \\r，报 Invalid string"
                            f"（坑 28）。修复：`sed -i 's/\\r$//'` 或写文件时 newline='\\n'")
    else:
        rep.add(OK, "K1", "纯 LF，无尾 \\r")
    return rep


# --------------------------------------------------------------------------- #
# 自检：用故意写坏的样本证明每条检查确实有效
# --------------------------------------------------------------------------- #
_BAD_SCRIPT = '''# -*- coding: utf-8 -*-
DATE = "2026-09-17"
WEEKDAY = "周四"
CFG = {"name": "测试"}
DIVS = [(2024, 0.5)]

def render():
    return f"{CFG['name']} {DIVS} {BT_SCOPE}"

print(render())
'''

_BAD_SCRIPT_QUOTE = '''# -*- coding: utf-8 -*-
DATE = "2026-09-17"
NOTE = "他问"有没有增长"，而不是"为什么""


def render():
    return NOTE
'''

_BAD_BUILDER = '''# -*- coding: utf-8 -*-
import re
DATE = "2026-09-17"
TPL_PATH = r"C:\\\\nope\\\\gen_x.py"
src = open(TPL_PATH).read()
src = re.sub(r"^DATE = .*$", 'DATE = "2026-09-16"', src, count=1)
NOTE = "「, 」坏了"
'''


def selftest() -> int:
    tmp = tempfile.mkdtemp(prefix="checkbuild_selftest_")
    fails = []
    print("=" * 72)
    print("自检：故意写坏的样本，检查器必须逐条报出来")
    print("=" * 72)

    def expect(name: str, rep: Report, tag: str, want: str):
        got = [lv for lv, tg, _ in rep.items if tg == tag]
        ok = want in got
        print(f"  {'✅' if ok else '❌'} {name}: 期望 {tag}={want}，实际 {tag}={got}")
        if not ok:
            fails.append(name)

    p1 = os.path.join(tmp, "gen_bad.py")
    open(p1, "w", encoding="utf-8").write(_BAD_SCRIPT)
    expect("未绑定名(BT_SCOPE)", check_script(p1, None, None), "S2", FAIL)

    p2 = os.path.join(tmp, "gen_bad_quote.py")
    open(p2, "w", encoding="utf-8").write(_BAD_SCRIPT_QUOTE)
    expect("裸引号 SyntaxError", check_script(p2, None, None), "S1", FAIL)

    p3 = os.path.join(tmp, "build_bad.py")
    open(p3, "w", encoding="utf-8").write(_BAD_BUILDER)
    r3 = check_builder(p3)
    expect("re.sub 非 lambda", r3, "B1", WARN)
    expect("残留旧日期", r3, "B2", WARN)
    expect("TPL_PATH 不存在", r3, "B3", FAIL)
    expect("引号批量替换坏掉", r3, "B4", FAIL)

    p4 = os.path.join(tmp, "codes.txt")
    open(p4, "wb").write(b"881101.TI\r\n881102.TI\r\n")
    expect("CRLF", check_codes(p4), "K1", FAIL)

    p5 = os.path.join(tmp, "hist.json")
    json.dump({"data": [{"date": "2026-09-01", "open": 1.234567, "high": 2.0,
                         "low": 1.0, "close": 1.5, "volume": 100, "ticker": "x"}]},
              open(p5, "w", encoding="utf-8"))
    r5 = check_hist(p5)
    expect("HIST 多余字段", r5, "C1", WARN)
    expect("HIST 未 round", r5, "C2", WARN)

    print(f"\n  自检结果：{'全部通过 ✅' if not fails else '失败项 ' + str(fails)}")
    return 0 if not fails else 1


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="构建自检器（把坑变成可执行校验）")
    ap.add_argument("--builder", help="构建器脚本 build_*.py")
    ap.add_argument("--script", help="生成的数据版脚本 gen_*_MMDD.py")
    ap.add_argument("--template", help="对应的 skill 模板（用于变量集合比对）")
    ap.add_argument("--html", help="产出的 HTML")
    ap.add_argument("--hist", help="HIST JSON（校验字段/精度/根数）")
    ap.add_argument("--codes", help="喂 CLI 的参数清单文本（CRLF 检查）")
    ap.add_argument("--auto", nargs="*", help="按扩展名自动分派")
    ap.add_argument("--expect-date", help="期望日期 YYYY-MM-DD（校验 DATE 与产物）")
    ap.add_argument("--expect-points", type=int, help="走势图期望点数（速览卡=252）")
    ap.add_argument("--allow-missing", type=int, default=0, help="[MISSING] 允许上限，超出才 ⚠️")
    ap.add_argument("--old", default="", help="旧特征值关键词，逗号分隔（残留即 ❌）")
    ap.add_argument("--selftest", action="store_true", help="用故意写坏的样本自检")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    reps: list[Report] = []
    old = [s.strip() for s in a.old.split(",") if s.strip()]
    if a.builder:
        reps.append(check_builder(a.builder))
    if a.script:
        reps.append(check_script(a.script, a.template, a.expect_date))
    if a.html:
        reps.append(check_html(a.html, a.hist, a.expect_date, a.expect_points, a.allow_missing, old))
    elif a.hist:
        reps.append(check_hist(a.hist))
    if a.codes:
        reps.append(check_codes(a.codes))
    for p in (a.auto or []):
        ext = os.path.splitext(p)[1].lower()
        if ext == ".py":
            reps.append(check_builder(p) if os.path.basename(p).startswith("build_")
                        else check_script(p, a.template, a.expect_date))
        elif ext in (".html", ".htm"):
            reps.append(check_html(p, a.hist, a.expect_date, a.expect_points, a.allow_missing, old))
        elif ext == ".json":
            reps.append(check_hist(p))
        elif ext in (".txt", ".csv"):
            reps.append(check_codes(p))
    if not reps:
        ap.print_help()
        return 0

    worst = 0
    for r in reps:
        worst = max(worst, r.dump())
    print(f"\n{'✅ 全部通过' if worst == 0 else ('❌ 存在必须修的问题' if worst == 1 else '⚠️ 仅告警')}"
          f"　（退出码 {worst}）")
    return worst


if __name__ == "__main__":
    sys.exit(main())
