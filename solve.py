from typing import List, Tuple, Optional

UNKN, EMPTY, FILL = -1, 0, 1  # -/0/1


def gen_patterns(length: int, clues: List[int]) -> List[List[int]]:
    if not clues:
        return [[EMPTY] * length]
    res = []
    total_blocks = sum(clues)
    min_len = total_blocks + (len(clues) - 1)
    if min_len > length:
        return []  # 不可能
    max_lead = length - min_len
    first, rest = clues[0], clues[1:]

    def place_with_lead(lead: int):
        prefix = [EMPTY] * lead + [FILL] * first
        if not rest:
            res.append(prefix + [EMPTY] * (length - len(prefix)))
            return
        remain = length - len(prefix) - 1
        if remain < 0:
            return
        for suffix in gen_patterns(remain, rest):
            res.append(prefix + [EMPTY] + suffix)

    for lead in range(max_lead + 1):
        place_with_lead(lead)
    return res


def line_consistent(patterns: List[List[int]], current: List[int]) -> List[List[int]]:
    ok = []
    for p in patterns:
        good = True
        for a, b in zip(p, current):
            if b != UNKN and a != b:
                good = False
                break
        if good:
            ok.append(p)
    return ok


def deduce_from_patterns(patterns: List[List[int]]) -> Optional[List[int]]:
    if not patterns:
        return None
    w = len(patterns[0])
    out = []
    for i in range(w):
        vals = {p[i] for p in patterns}
        out.append(vals.pop() if len(vals) == 1 else UNKN)
    return out


def apply_updates(line: List[int], deduced: List[int]) -> bool:
    changed = False
    for i, v in enumerate(deduced):
        if v != UNKN and line[i] != v:
            line[i] = v
            changed = True
    return changed


def transpose(grid: List[List[int]]) -> List[List[int]]:
    return [list(col) for col in zip(*grid)]


def pretty_io(grid: List[List[int]]) -> str:
    mapc = {UNKN: "-", EMPTY: "0", FILL: "1"}
    return "\n".join("".join(mapc[c] for c in row) for row in grid)


def solve_nonogram_partial(rows: List[List[int]], cols: List[List[int]]) -> List[List[int]]:
    """
    始终返回结果：
    - 确定: 1
    - 否定: 0
    - 未定: -1（打印时为 '-'）
    即使矛盾或未能完全解出，也返回当前已知的部分解。
    """
    h, w = len(rows), len(cols)
    grid = [[UNKN] * w for _ in range(h)]

    row_all = [gen_patterns(w, clue) for clue in rows]
    col_all = [gen_patterns(h, clue) for clue in cols]

    # 若起始存在明显不可能的行/列，也继续，但记录为无解方向
    row_ok = [list(pats) for pats in row_all]
    col_ok = [list(pats) for pats in col_all]

    def propagate() -> bool:
        # 返回 True 表示未发现矛盾；False 表示出现矛盾
        changed_any = True
        while changed_any:
            changed_any = False
            # 行传播
            for r in range(h):
                row_ok[r] = line_consistent(row_ok[r], grid[r])
                if not row_ok[r]:
                    return False  # 矛盾
                ded = deduce_from_patterns(row_ok[r])
                if ded is None:
                    return False
                if apply_updates(grid[r], ded):
                    changed_any = True
            # 列传播
            t = transpose(grid)
            for c in range(w):
                col_ok[c] = line_consistent(col_ok[c], t[c])
                if not col_ok[c]:
                    return False  # 矛盾
                ded = deduce_from_patterns(col_ok[c])
                if ded is None:
                    return False
                if apply_updates(t[c], ded):
                    changed_any = True
            grid[:] = transpose(t)
        return True

    def is_complete() -> bool:
        return all(all(cell != UNKN for cell in row) for row in grid)

    def choose_cell() -> Optional[Tuple[int, int]]:
        best = None
        best_score = float("inf")
        for r in range(h):
            for c in range(w):
                if grid[r][c] == UNKN:
                    score = len(row_ok[r]) + len(col_ok[c])
                    if score < best_score:
                        best_score = score
                        best = (r, c)
        return best

    def cell_bias(r: int, c: int) -> float:
        # 使用模式统计该格为 1 的倾向
        rcnt = len(row_ok[r]) or 1
        ones_r = sum(p[c] == FILL for p in row_ok[r]) / rcnt
        t = transpose(grid)
        ccnt = len(col_ok[c]) or 1
        ones_c = sum(p[r] == FILL for p in col_ok[c]) / ccnt
        return (ones_r + ones_c) / 2.0

    def snapshot():
        return [row[:] for row in grid], [list(p) for p in row_ok], [list(p) for p in col_ok]

    def restore(snap):
        nonlocal grid, row_ok, col_ok
        g, ro, co = snap
        grid = [row[:] for row in g]
        row_ok = [list(p) for p in ro]
        col_ok = [list(p) for p in co]

    best_partial = None  # 记录搜索过程中“最完整”的部分解

    def completeness_score(g) -> int:
        # 已确定格子数量
        return sum(1 for r in g for v in r if v != UNKN)

    def record_partial():
        nonlocal best_partial
        if best_partial is None or completeness_score(grid) > completeness_score(best_partial):
            best_partial = [row[:] for row in grid]

    def dfs() -> bool:
        # 尝试推进；若矛盾则记录当前部分解并回溯
        ok = propagate()
        record_partial()
        if not ok:
            return False
        if is_complete():
            return True
        pos = choose_cell()
        if pos is None:
            return True  # 理论上已 complete
        r, c = pos
        prob = cell_bias(r, c)
        try_vals = [FILL, EMPTY] if prob >= 0.5 else [EMPTY, FILL]
        for v in try_vals:
            snap = snapshot()
            grid[r][c] = v
            if dfs():
                return True
            restore(snap)
        # 两个分支都失败，记录当前部分解并返回失败
        record_partial()
        return False

    solved = dfs()
    if solved:
        return grid
    # 未完全解出或矛盾：返回最佳部分解（未定为 -1）
    return best_partial if best_partial is not None else grid
