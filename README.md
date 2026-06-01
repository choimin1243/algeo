# AlgeoMath Claude Code Skills

Claude Code에서 AlgeoMath Kids 수학 도구를 직접 제어하는 스킬 모음입니다.

## 스킬 목록

| 스킬 | 파일 | 설명 |
|--|--|--|
| `/stackblocks` | `stackblocks.md` | AlgeoMath Kids 3D — 쌓기나무 블록 쌓기 |
| `/algeo2d` | `algeo2d.md` | AlgeoMath Kids 2D — 도형 추가 |

## 설치 방법

1. 이 저장소를 클론합니다:
```bash
git clone https://github.com/choimin1243/algeomath-skills.git
```

2. `.md` 파일을 Claude Code 커맨드 폴더에 복사합니다:
```powershell
# Windows
copy stackblocks.md "$env:USERPROFILE\.claude\commands\stackblocks.md"
copy algeo2d.md "$env:USERPROFILE\.claude\commands\algeo2d.md"
```

3. Python 스크립트를 scripts 폴더에 복사합니다:
```powershell
copy scripts\stackblocks.py "$env:USERPROFILE\.claude\scripts\stackblocks.py"
copy scripts\algeo2d.py "$env:USERPROFILE\.claude\scripts\algeo2d.py"
```

4. 의존성 설치:
```bash
pip install playwright
playwright install chromium
```

## 사용법

### /stackblocks — 쌓기나무 (3D)

```
/stackblocks 3층 피라미드 만들어줘
/stackblocks 위에서 본 모양과 앞에서 본 모양이 같고 옆이 다른 경우의 수
/stackblocks 4x4x4 큐브 쌓아줘
```

AlgeoMath Kids 3D (https://www.algeomath.kr/kids/algeomath/poly/make) 에 직접 반영됩니다.

### /algeo2d — 2D 도형

```
/algeo2d 반지름 2 원 그려줘
/algeo2d 삼각형 꼭짓점 (0,3) (-3,0) (3,0) 초록색으로
/algeo2d 직사각형 가로 4 세로 2
```

AlgeoMath Kids 2D (https://www.algeomath.kr/kids/algeomath/app/make) 에 직접 반영됩니다.

## 구조

```
algebra/
├── README.md
├── stackblocks.md     ← /stackblocks 스킬 정의
├── algeo2d.md         ← /algeo2d 스킬 정의
└── scripts/
    ├── stackblocks.py ← 쌓기나무 터미널 CLI + 브라우저 주입 모듈
    └── algeo2d.py     ← 2D 도형 터미널 CLI + 브라우저 주입 모듈
```

## 요구사항

- Python 3.8+
- playwright (`pip install playwright && playwright install chromium`)
- Windows 10/11
