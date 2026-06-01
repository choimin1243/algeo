# /algeo2d — 2D 도형 CLI (AlgeoMath Kids 2D)

AlgeoMath Kids 2D (https://www.algeomath.kr/kids/algeomath/app/make) 에 2D 도형을 추가합니다.

## 사용법

```
/algeo2d <도형> [좌표...] [색상]
```

인수 없이 호출하면 현재 캔버스 상태를 보고합니다.

---

## 스킬 동작 절차

이 스킬이 호출되면:

1. 사용자의 자연어 요청을 파악합니다
2. 아래 Python 모듈을 사용합니다:

**대화형 CLI:**
```
C:\Users\choi2\.claude\scripts\algeo2d.py
```

**Python 모듈 직접 사용 (권장):**
```python
import sys; sys.path.insert(0, r'C:\Users\choi2\.claude\scripts')
from algeo2d import Scene, inject, get_scene
from playwright.sync_api import sync_playwright
import time
```

3. Playwright로 브라우저를 열고 도형을 AlgeoMath 2D에 직접 주입합니다

---

## 지원 도형

| 도형 | 메서드 | 인수 |
|--|--|--|
| 점 | `sc.add_free_point(x, y, color)` | x, y 좌표 |
| 선분 | `sc.add_segment(x1,y1, x2,y2, color)` | 두 끝점 좌표 |
| 삼각형 | `sc.add_polygon([(x1,y1),(x2,y2),(x3,y3)], color)` | 꼭짓점 3개 |
| 사각형 | `sc.add_polygon([(x1,y1),...,(x4,y4)], color)` | 꼭짓점 4개 |
| 임의 다각형 | `sc.add_polygon([(x,y),...], color)` | 꼭짓점 N개 |
| 원 | `sc.add_circle(cx, cy, r, color)` | 중심 + 반지름 |

색상 옵션: `'blue'`, `'red'`, `'green'`, `'orange'`, `'purple'`, `'cyan'`
또는 hex: `'#e53935'`, CSS: `'rgb(50,100,220)'`

---

## 브라우저 주입 패턴

```python
import sys, time
sys.path.insert(0, r'C:\Users\choi2\.claude\scripts')
from algeo2d import Scene, inject, get_scene
from playwright.sync_api import sync_playwright

p = sync_playwright().start()
browser = p.chromium.launch(headless=False, args=['--start-maximized'])
page = browser.new_page()
page.set_viewport_size({'width':1400,'height':900})
page.goto('https://www.algeomath.kr/kids/algeomath/app/make')
time.sleep(8)
frame = next(f for f in page.frames if 'tools/app' in f.url)

sc = get_scene(frame)

# 도형 추가
sc.add_free_point(2, 3)                              # 점
sc.add_segment(-3, 0, 3, 0, color='#ff8e00')         # 선분
sc.add_polygon([(-2,0),(0,3),(2,0)], color='#43a047') # 삼각형
sc.add_circle(0, 0, 2, color='#e53935')               # 원

inject(frame, sc)
time.sleep(1)
# 필요시: page.screenshot(path='C:/Users/choi2/result.png')
browser.close()
p.stop()
```

---

## 좌표계

```
AlgeoMath 2D 수학 좌표계:
  원점(0,0) = 캔버스 중앙
  x: 오른쪽 양수, 왼쪽 음수
  y: 위쪽 양수, 아래쪽 음수
  기본 표시 범위: x[-5, 5], y[-5, 5]
  단위: 1 = 격자 1칸
```

---

## 요청 해석 기준

| 사용자 요청 예시 | 처리 방식 |
|--|--|
| "원점에 점 찍어줘" | `add_free_point(0, 0)` |
| "반지름 3인 원" | `add_circle(0, 0, 3)` |
| "삼각형 그려줘 (0,3) (-3,0) (3,0)" | `add_polygon([(0,3),(-3,0),(3,0)])` |
| "가로 4 세로 2 직사각형" | `add_polygon([(-2,1),(2,1),(2,-1),(-2,-1)])` |
| "x=2 세로선" | `add_segment(2,-5, 2,5)` |
| "초기화" | 씬 읽기 → AxisSegment만 남기고 reload |
| "도형 몇 개야?" | `get_scene(frame)` 후 objectCapsules 집계 |

---

## 내부 데이터 구조

```
objectCapsules 타입:
  GenericPoint   — 자유점 (positionX, positionY)
  NameText       — 점 이름 레이블
  GenericSegment — 독립 선분 (point1, point2 ID 참조)
  AuxiliarySegment — 다각형의 변 (owner=폴리곤ID)
  GenericPolygon — 다각형 (points[], segments[])
  AxisSegment    — 좌표축 (삭제 불가)
```

---

## 검증 방법

주입 후 씬을 다시 읽어 도형 수와 위치를 확인합니다:

```python
sc2 = get_scene(frame)
caps = sc2.data['objectCapsules']
print(f'총 객체: {len(caps)}')
for o in caps:
    tn = o['typeName']
    if tn == 'GenericPoint':
        print(f'  점: ({o["content"]["positionX"]}, {o["content"]["positionY"]})')
    elif tn == 'GenericPolygon':
        print(f'  다각형: {len(o["content"]["points"])-1}각형')
    elif tn == 'GenericSegment':
        print(f'  선분: pt{o["content"]["point1"]}→pt{o["content"]["point2"]}')
```

---

## 저장 포맷

AlgeoMath 2D는 LZString 압축 JSON을 사용합니다:
- `algeoApp.save()` → `"v1_" + LZString.compressToEncodedURIComponent(json)`
- `algeoApp.load(compressed)` → 씬 전체 교체
