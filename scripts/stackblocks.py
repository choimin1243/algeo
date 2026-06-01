#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""쌓기나무 CLI — 터미널에서 3D 블록 쌓기 (AlgeoMath Kids 스타일)"""

import json, sys, os, re

if sys.platform == 'win32':
    os.system('')
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stdin.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ── 색상 ─────────────────────────────────────────────────
R    = '\033[0m'
BOLD = '\033[1m'
DIM  = '\033[2m'
RED, GRN, YLW = '\033[91m', '\033[92m', '\033[93m'
BLU, MAG, CYN = '\033[94m', '\033[95m', '\033[96m'
WHT            = '\033[97m'

HC = ['', GRN, CYN, YLW, MAG, RED]  # 높이 1~5 색상

def hc(h):
    return HC[min(h, 5)] if h > 0 else DIM

def vis(s):
    return len(re.sub(r'\033\[[0-9;]*m', '', s))

def rpad(s, w):
    return s + ' ' * max(0, w - vis(s))


# ── 그리드 ────────────────────────────────────────────────
class Grid:
    def __init__(self, W=5, D=5, H=5):
        self.W, self.D, self.H = W, D, H
        self.blocks = set()   # (x,y,z) 1-indexed
        self._hist  = []

    def _snap(self):
        self._hist.append(frozenset(self.blocks))
        if len(self._hist) > 50:
            self._hist.pop(0)

    def ok(self, x, y, z):
        return 1 <= x <= self.W and 1 <= y <= self.D and 1 <= z <= self.H

    def place(self, x, y, z):
        if not self.ok(x, y, z):
            return False, f"범위 초과 (x:1-{self.W}, y:1-{self.D}, z:1-{self.H})"
        if (x, y, z) in self.blocks:
            return False, f"({x},{y},{z}) 이미 블록 있음"
        self._snap(); self.blocks.add((x, y, z))
        return True, f"({x},{y},{z}) 배치"

    def remove(self, x, y, z):
        if (x, y, z) not in self.blocks:
            return False, f"({x},{y},{z}) 블록 없음"
        self._snap(); self.blocks.remove((x, y, z))
        return True, f"({x},{y},{z}) 제거"

    def stack(self, x, y, h):
        if not (1 <= x <= self.W and 1 <= y <= self.D):
            return False, f"범위 초과"
        if not (0 <= h <= self.H):
            return False, f"높이 범위 초과 (0-{self.H})"
        self._snap()
        for z in range(1, self.H + 1):
            self.blocks.discard((x, y, z))
        for z in range(1, h + 1):
            self.blocks.add((x, y, z))
        return True, f"({x},{y}) → {h}개 쌓기"

    def undo(self):
        if not self._hist:
            return False, "되돌릴 내용 없음"
        self.blocks = set(self._hist.pop())
        return True, "되돌리기 완료"

    def clear(self):
        self._snap(); self.blocks.clear()

    def count(self):
        return len(self.blocks)

    # 뷰 계산
    def hmap(self):
        m = [[0]*self.W for _ in range(self.D)]
        for x, y, z in self.blocks:
            if z > m[y-1][x-1]: m[y-1][x-1] = z
        return m

    def fsil(self):  # 정면 [z-1][x-1]
        s = [[False]*self.W for _ in range(self.H)]
        for x, y, z in self.blocks: s[z-1][x-1] = True
        return s

    def ssil(self):  # 우측면 [z-1][y-1]
        s = [[False]*self.D for _ in range(self.H)]
        for x, y, z in self.blocks: s[z-1][y-1] = True
        return s

    def layer(self, z):
        return [[(x+1, y+1, z) in self.blocks for x in range(self.W)]
                for y in range(self.D)]

    def save(self, fname):
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump({'W':self.W,'D':self.D,'H':self.H,
                       'blocks':[list(b) for b in self.blocks]}, f, indent=2)
        return True, f"'{fname}' 저장 완료"

    @classmethod
    def from_file(cls, fname):
        with open(fname, 'r', encoding='utf-8') as f:
            d = json.load(f)
        g = cls(d['W'], d['D'], d['H'])
        g.blocks = {tuple(p) for p in d['blocks']}
        return g, f"'{fname}' 불러오기 완료"


# ── 렌더링 헬퍼 ───────────────────────────────────────────
H_ = '─'; V_ = '│'
TL,TR,BL,BR = '┌','┐','└','┘'
TM,BM,LM,RM,MM = '┬','┴','├','┤','┼'

def hbar(n, l, m, r):
    return l + m.join([H_*3]*n) + r

def grid_view(title, tc, cols, rows, clabels, rlabels, cell_fn):
    out = [f"  {BOLD}{tc}{title}{R}"]
    out.append('      ' + ''.join(f'{str(c):^3}' for c in clabels))
    out.append('    ' + hbar(cols, TL, TM, TR))
    for ri in range(rows):
        row = f' {BOLD}{str(rlabels[ri]):>2}{R} '
        for ci in range(cols):
            ch, c = cell_fn(ri, ci)
            row += V_ + c + ch + R
        row += V_
        out.append(row)
        if ri < rows - 1:
            out.append('    ' + hbar(cols, LM, MM, RM))
    out.append('    ' + hbar(cols, BL, BM, BR))
    return out


# ── 각 뷰 ─────────────────────────────────────────────────
def view_top(g):
    m = g.hmap()
    def cell(ri, ci):
        h = m[ri][ci]
        return (f' {h} ', hc(h)+BOLD) if h else (' · ', DIM)
    return grid_view("위에서 본 모양", CYN, g.W, g.D,
                     range(1,g.W+1), range(1,g.D+1), cell)

def view_front(g):
    fv = g.fsil()
    def cell(ri, ci):
        z = g.H - ri
        return (' ■ ', GRN+BOLD) if fv[z-1][ci] else (' · ', DIM)
    return grid_view("앞에서 본 모양", GRN, g.W, g.H,
                     range(1,g.W+1), range(g.H,0,-1), cell)

def view_side(g):
    sv = g.ssil()
    def cell(ri, ci):
        z = g.H - ri
        return (' ■ ', YLW+BOLD) if sv[z-1][ci] else (' · ', DIM)
    return grid_view("오른쪽에서 본 모양", YLW, g.D, g.H,
                     range(1,g.D+1), range(g.H,0,-1), cell)

def view_layer(g, z):
    lm = g.layer(z)
    def cell(ri, ci):
        return (' ■ ', MAG+BOLD) if lm[ri][ci] else (' · ', DIM)
    return grid_view(f"{z}층 평면도", MAG, g.W, g.D,
                     range(1,g.W+1), range(1,g.D+1), cell)

def view_3d(g):
    """층별 비스듬한 3D 뷰 (높은 층 = 더 들여쓰기)"""
    out = [f"  {BOLD}{WHT}3D 뷰{R}  {DIM}(높은 층이 뒤에 위치){R}"]
    any_block = False
    for z in range(g.H, 0, -1):
        lm = g.layer(z)
        if not any(lm[y][x] for y in range(g.D) for x in range(g.W)):
            continue
        any_block = True
        ind = ' ' * (z - 1) * 2
        c = hc(z)
        out.append(f"{ind}  {BOLD}{c}── {z}층 ──{R}")
        for y in range(g.D):
            row = ind + '  '
            for x in range(g.W):
                row += (f'{c}{BOLD}■{R} ' if lm[y][x] else f'{DIM}·{R} ')
            out.append(row)
    if not any_block:
        out.append(f"  {DIM}(블록 없음){R}")
    return out

def view_all(g):
    """세 뷰를 나란히 출력"""
    top, front, side = view_top(g), view_front(g), view_side(g)
    tw = max(vis(l) for l in top)
    fw = max(vis(l) for l in front)
    n  = max(len(top), len(front), len(side))
    top   += [' '*tw] * (n - len(top))
    front += [' '*fw] * (n - len(front))
    side  += [''] * (n - len(side))
    return [rpad(t,tw) + '  ' + rpad(f,fw) + '  ' + s
            for t, f, s in zip(top, front, side)]


# ── REPL ──────────────────────────────────────────────────
HELP = f"""
{BOLD}{CYN}쌓기나무 CLI 명령어{R}

{BOLD}블록 조작{R}
  {GRN}놓기 x y z{R}      (place / p)  블록 1개 놓기
  {RED}빼기 x y z{R}      (remove / r) 블록 1개 빼기
  {YLW}쌓기 x y 높이{R}   (stack / s)  해당 열 높이까지 채우기

{BOLD}보기{R}
  {CYN}위{R}              (top / t)    위에서 본 모양 (높이 숫자)
  {GRN}앞{R}              (front / f)  앞에서 본 모양
  {YLW}옆{R}              (side / e)   오른쪽에서 본 모양
  {MAG}층 N{R}            (layer N)    N층 평면도
  보기             (view / v)   세 뷰 동시 표시
  {WHT}3D{R}                           층별 3D 뷰

{BOLD}기타{R}
  개수             (count / c)  블록 수
  초기화           (clear)      전체 삭제
  되돌리기         (undo / u)   실행 취소
  저장 [파일명]    (save)       JSON 저장
  불러오기 파일명  (load)       JSON 불러오기
  도움말           (help / h)   이 도움말
  종료             (quit / q)   종료

{BOLD}좌표{R}: x=가로(1=왼쪽), y=깊이(1=앞), z=높이(1=아래)
"""

def parse3(tokens, start=1):
    try:
        return [int(tokens[start+i]) for i in range(3)], None
    except (IndexError, ValueError):
        return None, "숫자 3개 필요"

def cmd(g, line):
    toks = line.strip().split()
    if not toks: return False
    t = toks[0].lower()

    if t in ('놓기','place','p'):
        args, err = parse3(toks)
        if err: print(f"  {RED}사용법: 놓기 x y z{R}"); return False
        ok, msg = g.place(*args)
        print(f"  {GRN if ok else RED}{'✓' if ok else '✗'} {msg}{R}")
        return ok

    if t in ('빼기','remove','r'):
        args, err = parse3(toks)
        if err: print(f"  {RED}사용법: 빼기 x y z{R}"); return False
        ok, msg = g.remove(*args)
        print(f"  {GRN if ok else RED}{'✓' if ok else '✗'} {msg}{R}")
        return ok

    if t in ('쌓기','stack','s'):
        args, err = parse3(toks)
        if err: print(f"  {RED}사용법: 쌓기 x y 높이{R}"); return False
        ok, msg = g.stack(*args)
        print(f"  {GRN if ok else RED}{'✓' if ok else '✗'} {msg}{R}")
        return ok

    if t in ('위','top','t'):
        print(); [print(l) for l in view_top(g)]; return False

    if t in ('앞','front','f'):
        print(); [print(l) for l in view_front(g)]; return False

    if t in ('옆','side','e'):
        print(); [print(l) for l in view_side(g)]; return False

    if t in ('층','layer','l'):
        if len(toks) < 2: print(f"  {RED}사용법: 층 N{R}"); return False
        try: z = int(toks[1])
        except ValueError: print(f"  {RED}숫자 필요{R}"); return False
        if not (1 <= z <= g.H): print(f"  {RED}층은 1-{g.H}{R}"); return False
        print(); [print(l) for l in view_layer(g, z)]; return False

    if t in ('보기','view','v'):
        print(); [print(l) for l in view_all(g)]; return False

    if t in ('3d',):
        print(); [print(l) for l in view_3d(g)]; return False

    if t in ('개수','count','c'):
        print(f"  {BOLD}{CYN}블록 수: {WHT}{g.count()}개{R}"); return False

    if t in ('초기화','clear'):
        g.clear(); print(f"  {YLW}초기화 완료{R}"); return False

    if t in ('되돌리기','undo','u'):
        ok, msg = g.undo()
        print(f"  {GRN if ok else RED}{'✓' if ok else '✗'} {msg}{R}")
        return ok

    if t in ('저장','save'):
        fname = (toks[1] if len(toks)>1 else 'stackblocks_save')
        if not fname.endswith('.json'): fname += '.json'
        try:
            ok, msg = g.save(fname); print(f"  {GRN}{msg}{R}")
        except Exception as e:
            print(f"  {RED}저장 실패: {e}{R}")
        return False

    if t in ('불러오기','load'):
        if len(toks) < 2: print(f"  {RED}사용법: 불러오기 파일명{R}"); return False
        fname = toks[1]
        if not fname.endswith('.json'): fname += '.json'
        try:
            ng, msg = Grid.from_file(fname)
            g.W, g.D, g.H = ng.W, ng.D, ng.H
            g.blocks = ng.blocks; g._hist.clear()
            print(f"  {GRN}{msg}{R}")
            return True
        except FileNotFoundError:
            print(f"  {RED}파일 없음: {fname}{R}")
        except Exception as e:
            print(f"  {RED}불러오기 실패: {e}{R}")
        return False

    if t in ('도움말','help','h','?'):
        print(HELP); return False

    if t in ('종료','quit','exit','q'):
        print(f"\n  {CYN}안녕히 가세요!{R}\n"); sys.exit(0)

    print(f"  {RED}알 수 없는 명령어: '{toks[0]}'  (도움말: h){R}")
    return False


BANNER = f"""
{BOLD}{CYN}╔══════════════════════════════════════════╗
║   쌓 기 나 무  CLI  v1.0                  ║
║   AlgeoMath Kids · 블록 쌓기 터미널 도구 ║
╚══════════════════════════════════════════╝{R}
  그리드 5×5×5  |  {DIM}도움말: h  |  종료: q{R}
"""

def main():
    g = Grid(5, 5, 5)
    print(BANNER)
    print()
    for l in view_all(g): print(l)
    print()

    while True:
        try:
            line = input(f"{BOLD}{BLU}쌓기나무>{R} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n  {CYN}종료합니다.{R}")
            break
        if not line: continue
        changed = cmd(g, line)
        if changed:
            print()
            for l in view_top(g): print(l)
        print()

if __name__ == '__main__':
    main()
