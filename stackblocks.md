# /stackblocks — 쌓기나무 CLI (AlgeoMath Kids 3D)

AlgeoMath Kids 3D (https://www.algeomath.kr/kids/algeomath/poly/make) 에 쌓기나무 블록을 쌓습니다.

## 사용법

```
/stackblocks <명령> [인수...]
```

인수 없이 호출하면 현재 상태를 보여줍니다.

---

## 스킬 동작 절차

이 스킬이 호출되면:

1. 사용자의 자연어 요청을 파악합니다
2. 아래 Python 스크립트를 사용합니다:
   - 자동 주입용 임시 Python 스크립트는 cmd/콘솔 창이 보이지 않도록 `pythonw.exe` 또는 `Start-Process -WindowStyle Hidden`으로 실행합니다.
   - AlgeoMath 3D 브라우저 창은 사용자가 확인할 수 있게 띄웁니다.

**터미널 CLI (대화형):**
```
C:\Users\choi2\.claude\scripts\stackblocks.py
```

**브라우저 주입 (AlgeoMath 3D 직접 반영):**
아래 패턴으로 직접 실행합니다 (inject_blocks.py 내장 로직 사용)

3. 사용자 요청에 따라 적절한 방식으로 실행합니다

---

## 블록 배치 방식

### 방식 1 — 터미널 CLI (stackblocks.py)
브라우저 없이 터미널에서 쌓기나무를 조작합니다.

```powershell
PYTHONUTF8=1 python "C:\Users\choi2\.claude\scripts\stackblocks.py"
```

터미널 내 명령어:

| 명령어 | 단축키 | 설명 |
|--|--|--|
| `놓기 x y z` | `p x y z` | 블록 1개 놓기 |
| `빼기 x y z` | `r x y z` | 블록 1개 빼기 |
| `쌓기 x y 높이` | `s x y h` | 열 전체를 h 높이까지 채우기 |
| `보기` | `v` | 위·앞·옆 3뷰 동시 표시 |
| `위` / `앞` / `옆` | `t`/`f`/`e` | 개별 뷰 |
| `층 N` | `l N` | N층 평면도 |
| `3d` | | 층별 3D 뷰 |
| `개수` | `c` | 블록 수 |
| `초기화` | | 전체 삭제 |
| `되돌리기` | `u` | 실행 취소 |
| `저장 [파일명]` | | JSON 저장 |
| `불러오기 파일명` | | JSON 불러오기 |

좌표: x=가로(1=왼쪽), y=깊이(1=앞), z=높이(1=아래), 5×5×5 그리드

### 방식 2 — AlgeoMath 3D 브라우저 직접 주입
Playwright로 브라우저를 열고 블록을 사이트에 직접 반영합니다.

아래 Python 코드 패턴을 사용합니다:

```python
import sys, json, time
sys.path.insert(0, r'C:\Users\choi2')
from playwright.sync_api import sync_playwright

layout = [
    # (col, row, layer) — 0-indexed
    (0,0,1),(1,0,1),(2,0,1),   # 예시: 1층 3개
    (0,0,2),(1,0,2),            # 예시: 2층 2개
    (0,0,3),                    # 예시: 3층 1개
]
COLORS = {1:0x81C784, 2:0xFF8F00, 3:0xE53935}  # 층별 색상

p = sync_playwright().start()
browser = p.chromium.launch(headless=False, args=['--start-maximized'])
page = browser.new_page()
page.set_viewport_size({'width':1400,'height':900})
page.goto('https://www.algeomath.kr/kids/algeomath/poly/make')
time.sleep(5)
frame = page.frames[1]
base = json.loads(frame.evaluate('() => JSON.stringify(window.AlgeomathPoly.api.save())'))
base['scene']['objectDatas'] = [
    {'id':100+i,'typeName':'STACK_CUBE','name':'stackCube',
     'is2DObject':False,'color':COLORS.get(layer,0xFFFFFF),
     'measurementType':None,'visible':True,
     'position':{'x':col+0.5,'y':-(row+0.5),'z':layer-0.5},
     'rotation':{'_x':0,'_y':0,'_z':0,'_order':'XYZ'},
     'scale':{'x':1,'y':1,'z':1}}
    for i,(col,row,layer) in enumerate(layout)
]
frame.evaluate('(d) => window.AlgeomathPoly.api.load(d)', base)
time.sleep(1)
browser.close(); p.stop()
```

---

## 요청 해석 기준

사용자가 자연어로 요청하면 아래와 같이 해석합니다:

| 사용자 요청 예시 | 처리 방식 |
|--|--|
| "3층 피라미드 쌓아줘" | 방식2: 3층 계단 피라미드 layout 생성 후 브라우저 주입 |
| "위에서 본 모양 보여줘" | 방식1: `보기` 또는 `위` 명령 실행 |
| "(2,3)에 2층으로 쌓기" | 방식2: `쌓기 2 3 2` 해당 블록 주입 |
| "5×5 바닥 깔아줘" | 방식2: 5×5 단층 layout 생성 후 주입 |
| "앞에서 본 모양과 같고 위에서 본 모양이 다른 2가지" | 방식2: 조건을 만족하는 배치 계산 후 주입 |
| "가능한 모든 경우의 수" | 방식2: 경우의 수 열거 후 격자 배치 주입 |
| "맨 위 블록 삭제" | 방식2: 기존 씬 읽기 → 최고 z 제거 → 재주입 |

---

## 좌표계

```
AlgeoMath 3D 내부 좌표:
  position.x = col + 0.5
  position.y = -(row + 0.5)
  position.z = layer - 0.5

예) col=2, row=1, layer=3 → position (2.5, -1.5, 2.5)
```

---

## 검증 방법

주입 후 `window.AlgeomathPoly.api.save()` 를 호출해 블록 수와 좌표를 확인합니다:

```python
saved = json.loads(frame.evaluate('() => JSON.stringify(window.AlgeomathPoly.api.save())'))
blocks = saved['scene']['objectDatas']
print(f'블록 수: {len(blocks)}')
for b in blocks:
    print(b['position'])
```
