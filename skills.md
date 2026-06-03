# AlgeoMath Skills

AlgeoMath 작업을 빠르게 라우팅하기 위한 안내서입니다.

## Routing

- 3D 쌓기나무, 블록 개수, 층 수, 높이맵, 위/앞/옆 모양이 함께 나오는 문제는 `/stackblocks`를 사용합니다.
- 2D 도형, 점, 선분, 삼각형, 원, 좌표평면 문제는 `/algeo2d`를 사용합니다.
- 사용자가 "도형"이라고만 말해도, 높이와 층이 있으면 기본적으로 3D로 판단합니다.

## Shape Inference

- 이미지가 있으면 먼저 `앞`, `뒤`, `왼쪽`, `오른쪽`, `위` 방향을 정합니다.
- 쌓기나무는 `x=좌우`, `y=앞뒤`, `z=아래→위` 기준으로 생각합니다.
- 층 수는 검증 정보일 뿐이므로, 바닥 배치와 높이를 함께 확인합니다.
- 정답이 하나가 아니면, 대표적인 배열 경우를 모두 제시합니다.
- 시작점에서 떠 있는 블록은 만들지 않습니다.

## Execution

- AlgeoMath 브라우저에서 직접 배치할 때는 `C:\Users\choi2\.codex\skills\algeomath-skills\scripts\stackblocks_harness.py`를 우선 사용합니다.
- 가능하면 `--blocks '[[x,y,z], ...]'` 형식으로 정확하게 넣습니다.
- 높이맵이 편할 때만 `--height-map '[[x,y,h], ...]'`를 사용합니다.
- Windows에서 보조 스크립트를 실행할 때는 창이 보이지 않도록 실행합니다.

## Installed Commands

- `/stackblocks`: AlgeoMath Kids 3D 쌓기나무 만들기
- `/algeo2d`: AlgeoMath Kids 2D 도형 만들기

## Local Files

- Commands: `C:\Users\choi2\.claude\commands`
- Scripts: `C:\Users\choi2\.claude\scripts`
