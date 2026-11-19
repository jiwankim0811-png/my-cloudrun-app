"""
Google Cloud Run 배포용 BFS vs DFS 미로 탐색 시각화 백엔드 서버 (main.py)
Stitch 연동 프로젝트: projects/17197904467986631939 (BFS vs DFS Maze Visualizer)
"""

import os
import sys
from typing import Optional, List, Dict, Any

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from algorithms import (
        DEFAULT_MAZES,
        solve_maze_bfs,
        solve_maze_dfs,
        compare_maze_algorithms
    )
except ImportError:
    from .algorithms import (
        DEFAULT_MAZES,
        solve_maze_bfs,
        solve_maze_dfs,
        compare_maze_algorithms
    )


app = FastAPI(
    title="BFS vs DFS Maze Escape Benchmark API",
    description="너비 우선 탐색(Queue)과 깊이 우선 탐색(Stack) 미로 탈출 시뮬레이션 및 단계별 히스토그램 스냅샷 API",
    version="1.0.0"
)

# CORS 설정: GAS 및 웹 브라우저 통신 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MazeSolveRequest(BaseModel):
    preset: Optional[str] = Field(
        "classic",
        description="미로 프리셋 이름 ('classic', 'dense', 'bottleneck')",
        examples=["classic"]
    )
    custom_grid: Optional[List[List[int]]] = Field(
        None,
        description="사용자 정의 2D 미로 그리드 (0: 통로, 1: 벽)"
    )
    start: Optional[List[int]] = Field(
        [0, 0],
        description="시작점 좌표 [row, col]",
        examples=[[0, 0]]
    )
    goal: Optional[List[int]] = Field(
        [9, 9],
        description="도착점 좌표 [row, col]",
        examples=[[9, 9]]
    )


@app.get("/")
def read_root():
    """API 상태 확인 및 프로젝트 정보 반환"""
    return {
        "status": "online",
        "service": "BFS vs DFS Maze Escape Benchmark API",
        "version": "1.0.0",
        "stitch_project_id": "projects/17197904467986631939",
        "endpoints": {
            "health": "/health",
            "presets": "/presets",
            "solve": "POST /solve"
        }
    }


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """배포 자동 검증용 헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "algorithms": ["BFS", "DFS"],
        "data_structures": ["FIFO Queue", "LIFO Stack"]
    }


@app.get("/presets")
def get_presets():
    """기본 제공되는 미로 토폴로지 프리셋 반환"""
    return {
        "presets": DEFAULT_MAZES,
        "metadata": {
            "classic": "10x10 Sample Labyrinth",
            "dense": "10x10 Dense Obstacles",
            "bottleneck": "10x10 Bottleneck Spiral"
        }
    }


@app.post("/solve")
def solve_maze(payload: MazeSolveRequest):
    """
    미로 그리드에 대해 BFS와 DFS를 동시에 수행하고,
    각 단계별 히스토그램 스냅샷, 시간 복잡도 메타데이터 및 비교 리포트를 반환합니다.
    """
    # 1. 미로 그리드 결정
    if payload.custom_grid:
        grid = payload.custom_grid
    else:
        preset_name = payload.preset or "classic"
        if preset_name not in DEFAULT_MAZES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"알 수 없는 프리셋입니다: '{preset_name}'. 사용 가능한 프리셋: {list(DEFAULT_MAZES.keys())}"
            )
        grid = DEFAULT_MAZES[preset_name]

    # 2. 좌표 유효성 검증
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    if rows == 0 or cols == 0:
        raise HTTPException(status_code=400, detail="유효하지 않은 미로 크기입니다.")

    start_r, start_c = payload.start[0], payload.start[1]
    goal_r, goal_c = payload.goal[0], payload.goal[1]

    if not (0 <= start_r < rows and 0 <= start_c < cols):
        raise HTTPException(status_code=400, detail="시작점 좌표가 미로 범위를 벗어났습니다.")
    if not (0 <= goal_r < rows and 0 <= goal_c < cols):
        raise HTTPException(status_code=400, detail="도착점 좌표가 미로 범위를 벗어났습니다.")
    if grid[start_r][start_c] == 1:
        raise HTTPException(status_code=400, detail="시작점이 벽(1)에 위치할 수 없습니다.")
    if grid[goal_r][goal_c] == 1:
        raise HTTPException(status_code=400, detail="도착점이 벽(1)에 위치할 수 없습니다.")

    # 3. 알고리즘 실행 및 비교 결과 산출
    try:
        report = compare_maze_algorithms(
            grid=grid,
            start=(start_r, start_c),
            goal=(goal_r, goal_c)
        )
        report["preset_name"] = payload.preset
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"알고리즘 연산 중 오류가 발생했습니다: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
