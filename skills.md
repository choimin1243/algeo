# AlgeoMath Skills

AlgeoMath 작업을 할 때는 먼저 만들 대상이 3D 쌓기나무인지, 2D 도형인지 구분한다.

## Routing

- 쌓기나무, 입체 블록, 큐브 쌓기, 위/앞/오른쪽에서 본 모양처럼 3D 구조가 필요한 요청은 `/stackblocks`를 사용한다.
- 삼각형, 사각형, 원, 다각형, 선분, 점, 좌표평면 위 도형처럼 쌓기나무가 아닌 나머지 도형 요청은 `/algeo2d`를 사용한다.
- 사용자가 "도형"이라고만 말하면 기본적으로 2D로 판단하되, 높이, 층, 큐브, 블록, 입체, 쌓기 같은 단서가 있으면 3D로 판단한다.

## Shape Inference

- 이미지나 예시 그림이 있으면 텍스트 설명보다 이미지의 방향과 모양을 우선한다.
- 쌓기나무 이미지는 먼저 보이는 시점(정면, 오른쪽, 위쪽 단서), 바닥 배치, 층별 개수, 각 위치의 높이를 함께 추론한다.
- "1층 5개, 2층 3개, 3층 1개"처럼 층별 개수가 보이면 단순히 한 줄로 쌓지 말고, 이미지의 좌우/앞뒤 가지 모양을 반영한 높이 지도(height map)를 만든다.
- 방향이 애매하면 사용자가 보는 그림의 왼쪽/오른쪽/앞쪽 모양을 보존하는 배치를 우선하고, 떠 있는 블록이 없도록 아래층부터 채운다.
- 생성 전에 예상 배치를 `높이 지도`, `층별 개수`, `총 블록 수`로 검산한다.

## Execution

- AlgeoMath 브라우저 창은 사용자가 확인할 수 있게 띄운다.
- Windows에서 보조 Python 스크립트를 실행할 때는 cmd/콘솔 창이 보이지 않도록 `pythonw.exe` 또는 `Start-Process -WindowStyle Hidden`을 사용한다.
- 자동 주입용 임시 스크립트는 `%TEMP%`에 만들고, 필요한 로그는 파일로 남긴다.
- 이전 요청에서 실행 중인 AlgeoMath 임시 Python 프로세스가 있으면 새 작업 전에 정리한다.

## Installed Commands

- `/stackblocks`: AlgeoMath Kids 3D 쌓기나무 만들기
- `/algeo2d`: AlgeoMath Kids 2D 도형 만들기

## Local Files

- Commands: `C:\Users\choi2\.claude\commands`
- Scripts: `C:\Users\choi2\.claude\scripts`
