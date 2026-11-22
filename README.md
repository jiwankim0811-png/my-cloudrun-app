# BFS vs DFS Maze Escape Benchmark (GraphLab)

Stitch 연동 프로젝트: `projects/17197904467986631939` (BFS vs DFS Maze Visualizer)

너비 우선 탐색(BFS, FIFO Queue)과 깊이 우선 탐색(DFS, LIFO Stack)의 작동 원리와 탐색 경로 차이를 실시간으로 시각화하고 성능을 비교하는 풀스택 벤치마크 웹 애플리케이션입니다.

## 1. 아키텍처 구성

- **서버 (`server/`)**: FastAPI 기반 Python 3.11 백엔드
  - `algorithms.py`: BFS 최단 경로 보장 탐색 및 DFS 백트랙 탐색, 단계별 히스토그램 데이터 생성, 시간 복잡도 $O(V+E)$ 메타데이터 산출
  - `main.py`: REST API 엔드포인트 (`/health`, `/presets`, `/solve`)
- **클라이언트 (`gas/`, `client/`)**: Stitch `Algorithmic Lens` 다크 테마 웹앱
  - Google Apps Script 웹앱 호스팅 (`Code.gs`)
  - Tailwind CSS, Space Grotesk, JetBrains Mono 기반 반응형 듀얼 아레나 (`index.html`)

## 2. 로컬 실행 방법

```bash
cd server
pip install -r requirements.txt
python main.py
```
- 서버 주소: `http://localhost:8080`
- API 문서(Swagger): `http://localhost:8080/docs`

## 3. Docker 및 Cloud Run 배포

```bash
docker build -t my-cloudrun-app .
docker run -p 8080:8080 -e PORT=8080 my-cloudrun-app
```
