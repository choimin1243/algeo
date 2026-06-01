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
2. 이미지나 예시 그림이 있으면 방향과 모양을 먼저 추론합니다:
   - 보이는 시점(정면/오른쪽/위쪽 단서), 바닥 배치, 층별 개수, 각 위치의 높이를 함께 읽습니다.
   - 층별 개수만으로 한 줄 배치를 만들지 말고, 그림의 좌우/앞뒤 가지 방향을 보존하는 높이 지도(height map)를 만듭니다.
   - 떠 있는 블록이 없도록 모든 높은 칸은 아래층부터 채웁니다.
   - 생성 전 `높이 지도`, `층별 개수`, `총 블록 수`가 요청/이미지와 맞는지 검산합니다.
3. 아래 Python 스크립트를 사용합니다:
   - 자동 주입용 임시 Python 스크립트는 cmd/콘솔 창이 보이지 않도록 `pythonw.exe` 또는 `Start-Process -WindowStyle Hidden`으로 실행합니다.
   - AlgeoMath 3D 브라우저 창은 사용자가 확인할 수 있게 띄웁니다.

**터미널 CLI (대화형):**
```
C:\Users\choi2\.claude\scripts\stackblocks.py
```

**브라우저 주입 (AlgeoMath 3D 직접 반영):**
아래 패턴으로 직접 실행합니다 (inject_blocks.py 내장 로직 사용)

4. 사용자 요청에 따라 적절한 방식으로 실행합니다

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

## 이미지 기반 쌓기나무 추론

이미지로 쌓기나무를 요청하면 다음 순서로 배치합니다:

1. 그림에서 보이는 앞쪽, 오른쪽, 왼쪽 방향을 먼저 정합니다.
2. 바닥에 닿아 있는 블록 수와 위치를 읽어 1층 평면도를 만듭니다.
3. 각 바닥 칸 위에 몇 층까지 올라가는지 읽어 height map을 만듭니다.
4. 층별 개수를 계산해 이미지의 표기와 맞는지 검산합니다.
5. AlgeoMath 좌표로 변환합니다: `x=가로`, `y=깊이`, `z=높이`.

예: 그림이 `3층(1개), 2층(3개), 1층(5개)`를 보이고 가운데 기둥에서 좌우/앞쪽으로 퍼지는 모양이면, 단순 직선 `1,2,3,2,1`만 고집하지 말고 이미지 방향에 맞는 십자/가지형 height map을 우선합니다. 단, 사용자가 특정 방향을 말하면 그 방향을 따른다.

검산 규칙:

- `1층 개수`는 높이 1 이상인 칸의 수입니다.
- `2층 개수`는 높이 2 이상인 칸의 수입니다.
- `3층 개수`는 높이 3 이상인 칸의 수입니다.
- 총 블록 수는 height map의 모든 높이 합입니다.

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
