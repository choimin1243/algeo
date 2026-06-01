# -*- coding: utf-8 -*-
"""
algeo2d.py — AlgeoMath Kids 2D 도형 추가 CLI
사용법: python algeo2d.py
"""
import sys, os, time, json, uuid, re
os.system('')
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from playwright.sync_api import sync_playwright
import ctypes, ctypes.wintypes

# ── 색상 상수 ──────────────────────────────────────────────
R    = '\033[0m'; BOLD = '\033[1m'; DIM = '\033[2m'
RED  = '\033[91m'; GRN = '\033[92m'; YLW = '\033[93m'
BLU  = '\033[94m'; MAG = '\033[95m'; CYN = '\033[96m'; WHT = '\033[97m'

SHAPE_COLORS = {
    'blue':   'rgb(50, 100, 220)',
    'red':    '#e53935',
    'green':  '#43a047',
    'orange': '#ff8e00',
    'purple': '#7b1fa2',
    'cyan':   '#00acc1',
    'black':  '#000000',
}
DEFAULT_PT  = 'rgb(50, 100, 220)'
DEFAULT_SEG = '#ff8e00'
DEFAULT_PLY = '#43a047'


# ── 씬 조작 헬퍼 ──────────────────────────────────────────
class Scene:
    """objectCapsules 빌더"""

    BASE_CONTENT = dict(
        dependers=[], dependerAlgebraicFunctionObject=[],
        visible=True, valid=True, lineWidth=2, globalAlpha=1,
        layerOrder=2, gradationState=False, gradationType='clear',
        gradationFirstColor='#db3743', gradationSecondColor='#43a047',
        gradationThirdColor='#0067ce',
        gradationFirstColorRate=0.3, gradationSecondColorRate=0.6,
        gradationThirdColorRate=1, gradationGlobalAlpha=0.5,
        isMovePosition=False, bindGroup=False, bindNumber=0,
    )

    def __init__(self, base_data: dict):
        self.data = json.loads(json.dumps(base_data))  # deep copy
        existing_ids = [o['id'] for o in self.data.get('objectCapsules', [])]
        self._next = max(existing_ids, default=0) + 1

    def _alloc(self):
        i = self._next
        self._next += 1
        return i

    def _content(self, extra: dict, color: str):
        c = dict(self.BASE_CONTENT)
        c['color'] = color
        c.update(extra)
        return c

    def add_free_point(self, x, y, color=DEFAULT_PT, show_label=False):
        """자유점(GenericPoint) + NameText 추가 → point id 반환"""
        pt_id = self._alloc()
        nm_id = self._alloc()

        pt_content = self._content(dict(
            name='가', layerOrder=3, isMovePosition=True,
            positionX=x, positionY=y, style=1, size=0, tabState=0,
            trailOn=False,
            nameText=nm_id,
            nameDisplacement={'x': 15, 'y': -15},
            mode=0, expr1=None, expr2=None,
            moveable=True, isReferencePoint=False,
            sliderList=[], dependFunctionName=[],
        ), color)

        nm_content = self._content(dict(
            name=str(uuid.uuid4()), layerOrder=4,
            centerX=x + 0.2, centerY=y + 0.2,
            versionNum=1, text='',
            fontName='NanumSquareR', underlineColor='#00ff0000',
            underlineState=0, bold='', italic='',
            fontSize=17, isLatex=False, latex='',
            moveable=True, owner=pt_id,
            offsetPivot={'x': 0.2, 'y': 0.2},
        ), '#000000')

        self.data['objectCapsules'].append(
            {'typeName': 'GenericPoint', 'id': pt_id, 'isTopLevel': True,  'content': pt_content})
        self.data['objectCapsules'].append(
            {'typeName': 'NameText',     'id': nm_id, 'isTopLevel': False, 'content': nm_content})
        return pt_id

    def _set_depender(self, pt_id, dep_id):
        for obj in self.data['objectCapsules']:
            if obj['id'] == pt_id:
                obj['content']['dependers'].append(dep_id)

    def add_segment(self, x1, y1, x2, y2, color=DEFAULT_SEG):
        """선분 추가"""
        p1 = self.add_free_point(x1, y1)
        p2 = self.add_free_point(x2, y2)
        seg_id = self._alloc()
        self._set_depender(p1, seg_id)
        self._set_depender(p2, seg_id)

        self.data['objectCapsules'].append({'typeName': 'GenericSegment',
            'id': seg_id, 'isTopLevel': True,
            'content': self._content(dict(
                name=f'선분_{seg_id}', lineDash=[], trailOn=False,
                point1=p1, point2=p2, fixed=False,
            ), color)})
        return seg_id

    def add_polygon(self, pts, color=DEFAULT_PLY):
        """다각형 추가 — pts: [(x,y), ...]"""
        pt_ids = [self.add_free_point(x, y) for x, y in pts]
        n = len(pts)

        # 폴리곤 ID 먼저 확보 (AuxiliarySegment의 owner로 사용)
        poly_id = self._alloc()

        # AuxiliarySegment 으로 변(edge) 생성
        seg_ids = []
        for i in range(n):
            p1, p2 = pt_ids[i], pt_ids[(i+1) % n]
            seg_id = self._alloc()
            self._set_depender(p1, seg_id)
            self._set_depender(p2, seg_id)
            self.data['objectCapsules'].append({'typeName': 'AuxiliarySegment',
                'id': seg_id, 'isTopLevel': False,
                'content': self._content(dict(
                    name=f'변_{seg_id}',
                    owner=poly_id,      # 소유 폴리곤 ID
                    movable=True,
                    segmentIndex=i,     # 변 순서
                    point1=p1, point2=p2,
                    lineDash=[], trailOn=False,
                ), color)})
            seg_ids.append(seg_id)

        for pid in pt_ids: self._set_depender(pid, poly_id)
        for sid in seg_ids: self._set_depender(sid, poly_id)

        self.data['objectCapsules'].append({'typeName': 'GenericPolygon',
            'id': poly_id, 'isTopLevel': True,
            'content': self._content(dict(
                name=f'다각형_{poly_id}',
                points=pt_ids + [pt_ids[0]],   # 닫힌 경로 (마지막 = 첫번째)
                segments=seg_ids,               # AuxiliarySegment IDs
                trailOn=False,
                fillColor=color,
                fillAlpha=0.25,
                lineDash=[],
                hasPattern=False, pattern=0,
                patternLineDash=[], patternStripeAlpha=0.5,
                patternStripeColor=color, patternStripeWidth=5,
                patternStripeInterval=10,
            ), color)})
        return poly_id

    def add_circle(self, cx, cy, r, color='#e53935'):
        """원 추가 (32-각형 근사)"""
        import math
        n = 32
        pts = [(cx + r*math.cos(2*math.pi*i/n),
                cy + r*math.sin(2*math.pi*i/n)) for i in range(n)]
        return self.add_polygon(pts, color=color)

    def to_json_str(self):
        return json.dumps(self.data, ensure_ascii=False)


# ── 브라우저 주입 ──────────────────────────────────────────
def inject(frame, scene: Scene):
    """씬을 LZString으로 압축해서 algeoApp.load()에 전달"""
    json_str = scene.to_json_str()
    frame.evaluate(f'''() => {{
        const raw = {json_repr(json_str)};
        const compressed = "v1_" + LZString.compressToEncodedURIComponent(raw);
        window.algeoApp.load(compressed);
    }}''')


def json_repr(s):
    """Python 문자열을 JS 리터럴로 안전하게 변환"""
    return json.dumps(s)


def get_scene(frame) -> Scene:
    """현재 브라우저의 씬 데이터 읽기"""
    decoded = frame.evaluate('''() => {
        const s = window.algeoApp.save();
        if (!s) return null;
        let d = s;
        if (d.startsWith("v1_")) d = d.slice(3);
        return LZString.decompressFromEncodedURIComponent(d);
    }''')
    if not decoded:
        return None
    return Scene(json.loads(decoded))


def bring_to_front():
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    def _cb(hwnd, _):
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, 256)
        if 'algeomath' in buf.value.lower():
            ctypes.windll.user32.ShowWindow(hwnd, 3)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        return True
    ctypes.windll.user32.EnumWindows(WNDENUMPROC(_cb), 0)


# ── 명령어 파서 ───────────────────────────────────────────
HELP = f"""
{BOLD}{CYN}AlgeoMath 2D 도형 추가 CLI{R}

{BOLD}도형 명령어{R}  (좌표: 수학 좌표계 — 예: 점 2 3)
  {GRN}점 x y{R}                        자유점
  {GRN}선분 x1 y1 x2 y2{R}              선분
  {GRN}삼각형 x1 y1 x2 y2 x3 y3{R}      삼각형
  {GRN}사각형 x1 y1 x2 y2 x3 y3 x4 y4{R} 사각형(임의)
  {GRN}다각형 x1 y1 x2 y2 ...{R}         다각형 (짝수 개 좌표)
  {GRN}원 cx cy r{R}                    원

{BOLD}기타{R}
  초기화   — 모든 도형 삭제 (축만 남김)
  스크린샷  — 현재 화면 캡처
  도움말   — 이 도움말
  종료     — 종료

{BOLD}색상{R} (선택, 명령어 끝에 추가)
  blue  red  green  orange  purple  cyan
  예: 원 0 0 2 red
"""


def parse_floats(tokens):
    result = []
    color = None
    for t in tokens:
        if t in SHAPE_COLORS:
            color = SHAPE_COLORS[t]
        else:
            try:
                result.append(float(t))
            except ValueError:
                pass
    return result, color


def run(frame, line: str):
    toks = line.strip().split()
    if not toks:
        return
    cmd = toks[0].lower()

    if cmd in ('도움말', 'help', 'h', '?'):
        print(HELP)
        return

    if cmd in ('초기화', 'clear', 'reset'):
        sc = get_scene(frame)
        if sc:
            sc.data['objectCapsules'] = [
                o for o in sc.data['objectCapsules']
                if o['typeName'] == 'AxisSegment'
            ]
            inject(frame, sc)
            print(f'  {GRN}초기화 완료{R}')
        return

    if cmd in ('스크린샷', 'shot', 'ss'):
        return  # main()에서 처리

    if cmd in ('종료', 'quit', 'exit', 'q'):
        print(f'\n  {CYN}종료합니다.{R}')
        sys.exit(0)

    # ── 도형 명령어 ──
    vals, color = parse_floats(toks[1:])

    sc = get_scene(frame)
    if sc is None:
        print(f'  {RED}씬 읽기 실패{R}')
        return

    try:
        if cmd in ('점', 'point', 'p'):
            if len(vals) < 2:
                print(f'  {RED}사용법: 점 x y{R}'); return
            sc.add_free_point(vals[0], vals[1], color=color or DEFAULT_PT)
            print(f'  {GRN}점 ({vals[0]}, {vals[1]}) 추가{R}')

        elif cmd in ('선분', 'segment', 'seg', 's'):
            if len(vals) < 4:
                print(f'  {RED}사용법: 선분 x1 y1 x2 y2{R}'); return
            sc.add_segment(*vals[:4], color=color or DEFAULT_SEG)
            print(f'  {GRN}선분 ({vals[0]},{vals[1]})→({vals[2]},{vals[3]}) 추가{R}')

        elif cmd in ('삼각형', 'triangle', 'tri', 't'):
            if len(vals) < 6:
                print(f'  {RED}사용법: 삼각형 x1 y1 x2 y2 x3 y3{R}'); return
            pts = [(vals[i], vals[i+1]) for i in range(0, 6, 2)]
            sc.add_polygon(pts, color=color or DEFAULT_PLY)
            print(f'  {GRN}삼각형 추가{R}')

        elif cmd in ('사각형', 'rect', 'r'):
            if len(vals) >= 8:
                pts = [(vals[i], vals[i+1]) for i in range(0, 8, 2)]
            elif len(vals) == 4:
                x, y, w, h = vals
                pts = [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
            else:
                print(f'  {RED}사용법: 사각형 x1 y1 x2 y2 x3 y3 x4 y4{R}'); return
            sc.add_polygon(pts, color=color or DEFAULT_PLY)
            print(f'  {GRN}사각형 추가{R}')

        elif cmd in ('다각형', 'polygon', 'poly'):
            if len(vals) < 6 or len(vals) % 2 != 0:
                print(f'  {RED}사용법: 다각형 x1 y1 x2 y2 ... (3개 이상 꼭짓점){R}'); return
            pts = [(vals[i], vals[i+1]) for i in range(0, len(vals), 2)]
            sc.add_polygon(pts, color=color or DEFAULT_PLY)
            print(f'  {GRN}{len(pts)}각형 추가{R}')

        elif cmd in ('원', 'circle', 'c'):
            if len(vals) < 3:
                print(f'  {RED}사용법: 원 cx cy r{R}'); return
            sc.add_circle(vals[0], vals[1], vals[2], color=color or '#e53935')
            print(f'  {GRN}원 중심({vals[0]},{vals[1]}) 반지름{vals[2]} 추가{R}')

        else:
            print(f'  {RED}알 수 없는 명령어: {toks[0]}  (도움말: h){R}')
            return

        inject(frame, sc)

    except Exception as e:
        print(f'  {RED}오류: {e}{R}')


# ── 메인 ─────────────────────────────────────────────────
BANNER = f"""
{BOLD}{BLU}=== AlgeoMath 2D  도형 추가 CLI  v1.0 ==={R}
  도움말: h  |  종료: q
"""

def main():
    pw  = sync_playwright().start()
    browser = pw.chromium.launch(headless=False, args=['--start-maximized'])
    page = browser.new_page()
    page.set_viewport_size({'width': 1400, 'height': 900})
    page.goto('https://www.algeomath.kr/kids/algeomath/app/make')
    print('로딩 중...')
    time.sleep(8)

    frame = next((f for f in page.frames if 'tools/app' in f.url), None)
    if not frame:
        print(f'{RED}앱 프레임을 찾을 수 없습니다.{R}')
        browser.close(); pw.stop(); return

    # 창 앞으로
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    def _cb(hwnd, _):
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, 256)
        if 'algeomath' in buf.value.lower():
            ctypes.windll.user32.ShowWindow(hwnd, 3)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        return True
    ctypes.windll.user32.EnumWindows(WNDENUMPROC(_cb), 0)

    print(BANNER)

    # 스크린샷용 page 전달 클로저
    _page = page

    while True:
        try:
            line = input(f'{BOLD}{BLU}algeo2d>{R} ').strip()
        except (EOFError, KeyboardInterrupt):
            print(f'\n  {CYN}종료합니다.{R}')
            break
        if not line:
            continue
        # 스크린샷 명령어에만 _page 필요
        if line.strip().split()[0].lower() in ('스크린샷', 'shot', 'ss'):
            _page.screenshot(path='C:/Users/choi2/algeo2d_shot.png')
            print(f'  {GRN}algeo2d_shot.png 저장됨{R}')
        else:
            run(frame, line)
        print()

    browser.close()
    pw.stop()


if __name__ == '__main__':
    main()
