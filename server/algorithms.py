"""
BFS vs DFS 미로 탐색 백엔드 알고리즘 모듈 (algorithms.py)
Stitch 연동 프로젝트: projects/17197904467986631939 (BFS vs DFS Maze Visualizer)

구현 기능:
1. 너비 우선 탐색 (BFS, Breadth-First Search) 미로 탐색 (FIFO Queue 기반)
2. 깊이 우선 탐색 (DFS, Depth-First Search) 미로 탐색 (LIFO Stack 기반)
3. 단계별(Step-by-step) 탐색 상태, 큐/스택 내용, 히스토그램 데이터 배열 생성
4. 각 스텝별 소요 시간 및 시간/공간 복잡도(Time & Space Complexity) 진행 메타데이터 산출
5. BFS vs DFS 종합 비교 분석 및 승자 판정
"""

import time
from collections import deque
from typing import List, Dict, Any, Tuple, Optional, Set


# 기본 미로 토폴로지 프리셋 (0: 통로, 1: 벽)
DEFAULT_MAZES: Dict[str, List[List[int]]] = {
    "classic": [
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 1, 0, 1, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
        [1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 1, 1, 1, 0]
    ],
    "dense": [
        [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 1, 0, 1, 0, 1, 1, 1, 0],
        [0, 0, 1, 0, 1, 0, 0, 0, 1, 0],
        [0, 1, 1, 0, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0, 0, 1, 0]
    ],
    "bottleneck": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 1, 1, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 1, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]
}

# 이동 방향: 상, 우, 하, 좌
DIRECTIONS = [
    (-1, 0, "UP"),
    (0, 1, "RIGHT"),
    (1, 0, "DOWN"),
    (0, -1, "LEFT")
]


def count_passable_cells(grid: List[List[int]]) -> int:
    """이동 가능한 통로(0) 셀의 총 개수를 계산합니다."""
    return sum(row.count(0) for row in grid)


def solve_maze_bfs(
    grid: List[List[int]],
    start: Tuple[int, int] = (0, 0),
    goal: Tuple[int, int] = (9, 9)
) -> Dict[str, Any]:
    """
    너비 우선 탐색 (BFS)을 수행하고 각 단계별 스냅샷, 히스토그램 및 메타데이터를 반환합니다.
    자료구조: FIFO Queue (collections.deque)
    특징: 최단 경로(Shortest Path) 보장, 레벨 단위 방사형 탐색
    """
    rows = len(grid)
    cols = len(grid[0])
    total_passable = count_passable_cells(grid)

    queue = deque()
    # (row, col, path, level)
    queue.append((start[0], start[1], [list(start)], 0))
    visited: Set[Tuple[int, int]] = {start}

    snapshots: List[Dict[str, Any]] = []
    step = 0
    max_queue_size = 1
    total_edges_explored = 0
    found_path: Optional[List[List[int]]] = None

    # 단계별 히스토그램 누적기: 거리별(레벨별) 방문 노드 수
    level_distribution: Dict[int, int] = {0: 1}
    direction_counts: Dict[str, int] = {"UP": 0, "RIGHT": 0, "DOWN": 0, "LEFT": 0}

    overall_start_time = time.perf_counter()

    while queue:
        step += 1
        step_start_time = time.perf_counter()

        r, c, path, level = queue.popleft()
        current_node = [r, c]

        # 도착점 도달 확인
        if (r, c) == goal:
            found_path = path
            step_elapsed_us = (time.perf_counter() - step_start_time) * 1_000_000
            total_elapsed_ms = (time.perf_counter() - overall_start_time) * 1000

            snapshots.append({
                "step": step,
                "action": "GOAL_REACHED",
                "current_node": current_node,
                "level": level,
                "queue": [list(item[:2]) for item in queue],
                "queue_size": len(queue),
                "visited_count": len(visited),
                "current_path": path,
                "histogram": {
                    "level_distribution": dict(sorted(level_distribution.items())),
                    "queue_size_trend": len(queue),
                    "direction_counts": dict(direction_counts),
                    "explore_ratio": round((len(visited) / total_passable) * 100, 1)
                },
                "metadata": {
                    "step_elapsed_us": round(step_elapsed_us, 2),
                    "total_elapsed_ms": round(total_elapsed_ms, 2),
                    "time_complexity_ops": len(visited) + total_edges_explored,
                    "time_complexity_formula": "O(V + E)",
                    "space_complexity_memory": len(queue),
                    "space_complexity_formula": "O(V)",
                    "status_note": f"목표점 도착 완료! 최단 경로 길이: {len(path)} 보폭"
                }
            })
            break

        # 4방향 인접 노드 확장 (Wavefront Expansion)
        expanded_nodes = []
        for dr, dc, dname in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                total_edges_explored += 1
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    next_level = level + 1
                    level_distribution[next_level] = level_distribution.get(next_level, 0) + 1
                    direction_counts[dname] = direction_counts.get(dname, 0) + 1
                    new_path = path + [[nr, nc]]
                    queue.append((nr, nc, new_path, next_level))
                    expanded_nodes.append([nr, nc])

        if len(queue) > max_queue_size:
            max_queue_size = len(queue)

        step_elapsed_us = (time.perf_counter() - step_start_time) * 1_000_000
        total_elapsed_ms = (time.perf_counter() - overall_start_time) * 1000

        snapshots.append({
            "step": step,
            "action": "EXPAND" if expanded_nodes else "VISIT",
            "current_node": current_node,
            "level": level,
            "expanded_nodes": expanded_nodes,
            "queue": [list(item[:2]) for item in queue],
            "queue_size": len(queue),
            "visited_count": len(visited),
            "current_path": path,
            "histogram": {
                "level_distribution": dict(sorted(level_distribution.items())),
                "queue_size_trend": len(queue),
                "direction_counts": dict(direction_counts),
                "explore_ratio": round((len(visited) / total_passable) * 100, 1)
            },
            "metadata": {
                "step_elapsed_us": round(step_elapsed_us, 2),
                "total_elapsed_ms": round(total_elapsed_ms, 2),
                "time_complexity_ops": len(visited) + total_edges_explored,
                "time_complexity_formula": "O(V + E)",
                "space_complexity_memory": len(queue),
                "space_complexity_formula": "O(V)",
                "status_note": f"레벨 {level} 노드 ({r},{c}) 탐색 중 / {len(expanded_nodes)}개 이웃 확장"
            }
        })

    total_time_ms = (time.perf_counter() - overall_start_time) * 1000

    return {
        "algorithm": "BFS",
        "name_ko": "너비 우선 탐색 (BFS)",
        "data_structure": "FIFO Queue",
        "guaranteed_shortest_path": True,
        "success": found_path is not None,
        "total_steps": step,
        "path_length": len(found_path) if found_path else 0,
        "final_path": found_path or [],
        "total_visited": len(visited),
        "total_passable": total_passable,
        "explore_ratio": round((len(visited) / total_passable) * 100, 1) if total_passable else 0,
        "peak_memory_size": max_queue_size,
        "total_time_ms": round(total_time_ms, 2),
        "snapshots": snapshots
    }


def solve_maze_dfs(
    grid: List[List[int]],
    start: Tuple[int, int] = (0, 0),
    goal: Tuple[int, int] = (9, 9)
) -> Dict[str, Any]:
    """
    깊이 우선 탐색 (DFS)을 수행하고 각 단계별 스냅샷, 히스토그램 및 메타데이터를 반환합니다.
    자료구조: LIFO Stack (list)
    특징: 깊이 우선 분기 탐색, 백트랙(Backtrack) 발생, 메모리 절약 O(h)
    """
    rows = len(grid)
    cols = len(grid[0])
    total_passable = count_passable_cells(grid)

    # stack element: dict(r, c, path, dir_idx)
    stack: List[Dict[str, Any]] = [{
        "r": start[0],
        "c": start[1],
        "path": [list(start)],
        "dir_idx": 0
    }]
    visited: Set[Tuple[int, int]] = {start}

    snapshots: List[Dict[str, Any]] = []
    step = 0
    max_stack_depth = 1
    backtrack_count = 0
    total_edges_explored = 0
    found_path: Optional[List[List[int]]] = None

    # 단계별 히스토그램 누적기: 깊이 구간(Depth Bin)별 노드 분포
    depth_bins: Dict[str, int] = {
        "0-4": 1,
        "5-9": 0,
        "10-14": 0,
        "15-19": 0,
        "20+": 0
    }
    direction_counts: Dict[str, int] = {"UP": 0, "RIGHT": 0, "DOWN": 0, "LEFT": 0}

    overall_start_time = time.perf_counter()

    while stack:
        step += 1
        step_start_time = time.perf_counter()

        current = stack[-1]
        r, c = current["r"], current["c"]
        current_node = [r, c]
        current_depth = len(stack)

        # 도착점 도달 확인
        if (r, c) == goal:
            found_path = current["path"]
            step_elapsed_us = (time.perf_counter() - step_start_time) * 1_000_000
            total_elapsed_ms = (time.perf_counter() - overall_start_time) * 1000

            snapshots.append({
                "step": step,
                "action": "GOAL_REACHED",
                "current_node": current_node,
                "depth": current_depth,
                "stack": [[frame["r"], frame["c"]] for frame in stack],
                "stack_depth": current_depth,
                "visited_count": len(visited),
                "backtrack_count": backtrack_count,
                "current_path": current["path"],
                "histogram": {
                    "depth_distribution": dict(depth_bins),
                    "stack_depth_trend": current_depth,
                    "direction_counts": dict(direction_counts),
                    "explore_ratio": round((len(visited) / total_passable) * 100, 1)
                },
                "metadata": {
                    "step_elapsed_us": round(step_elapsed_us, 2),
                    "total_elapsed_ms": round(total_elapsed_ms, 2),
                    "time_complexity_ops": len(visited) + total_edges_explored,
                    "time_complexity_formula": "O(V + E)",
                    "space_complexity_memory": current_depth,
                    "space_complexity_formula": "O(h)",
                    "status_note": f"목표점 도달 완료! 최종 탐색 경로: {len(found_path)} 보폭 (백트랙 {backtrack_count}회)"
                }
            })
            break

        # 다음 미방문 이웃 탐색
        moved = False
        while current["dir_idx"] < len(DIRECTIONS):
            dr, dc, dname = DIRECTIONS[current["dir_idx"]]
            current["dir_idx"] += 1
            nr, nc = r + dr, c + dc

            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                total_edges_explored += 1
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    direction_counts[dname] = direction_counts.get(dname, 0) + 1
                    new_depth = current_depth + 1

                    # 깊이 구간 카운트
                    if new_depth <= 4:
                        depth_bins["0-4"] += 1
                    elif new_depth <= 9:
                        depth_bins["5-9"] += 1
                    elif new_depth <= 14:
                        depth_bins["10-14"] += 1
                    elif new_depth <= 19:
                        depth_bins["15-19"] += 1
                    else:
                        depth_bins["20+"] += 1

                    new_frame = {
                        "r": nr,
                        "c": nc,
                        "path": current["path"] + [[nr, nc]],
                        "dir_idx": 0
                    }
                    stack.append(new_frame)
                    moved = True
                    break

        if len(stack) > max_stack_depth:
            max_stack_depth = len(stack)

        step_elapsed_us = (time.perf_counter() - step_start_time) * 1_000_000
        total_elapsed_ms = (time.perf_counter() - overall_start_time) * 1000

        if moved:
            action = "PROBE"
            note = f"깊이 {len(stack)} 노드 ({stack[-1]['r']},{stack[-1]['c']}) 전진 탐침"
        else:
            # 막다른 길 도달 -> 백트랙 (Backtrack)
            action = "BACKTRACK"
            popped = stack.pop()
            backtrack_count += 1
            note = f"막다른 길 ({popped['r']},{popped['c']})에서 스택 팝 및 백트랙 (누적 {backtrack_count}회)"

        snapshots.append({
            "step": step,
            "action": action,
            "current_node": current_node,
            "depth": len(stack),
            "stack": [[frame["r"], frame["c"]] for frame in stack],
            "stack_depth": len(stack),
            "visited_count": len(visited),
            "backtrack_count": backtrack_count,
            "current_path": current["path"],
            "histogram": {
                "depth_distribution": dict(depth_bins),
                "stack_depth_trend": len(stack),
                "direction_counts": dict(direction_counts),
                "explore_ratio": round((len(visited) / total_passable) * 100, 1)
            },
            "metadata": {
                "step_elapsed_us": round(step_elapsed_us, 2),
                "total_elapsed_ms": round(total_elapsed_ms, 2),
                "time_complexity_ops": len(visited) + total_edges_explored,
                "time_complexity_formula": "O(V + E)",
                "space_complexity_memory": len(stack),
                "space_complexity_formula": "O(h)",
                "status_note": note
            }
        })

    total_time_ms = (time.perf_counter() - overall_start_time) * 1000

    return {
        "algorithm": "DFS",
        "name_ko": "깊이 우선 탐색 (DFS)",
        "data_structure": "LIFO Stack",
        "guaranteed_shortest_path": False,
        "success": found_path is not None,
        "total_steps": step,
        "path_length": len(found_path) if found_path else 0,
        "final_path": found_path or [],
        "total_visited": len(visited),
        "total_passable": total_passable,
        "explore_ratio": round((len(visited) / total_passable) * 100, 1) if total_passable else 0,
        "backtrack_count": backtrack_count,
        "peak_memory_size": max_stack_depth,
        "total_time_ms": round(total_time_ms, 2),
        "snapshots": snapshots
    }


def compare_maze_algorithms(
    grid: List[List[int]],
    start: Tuple[int, int] = (0, 0),
    goal: Tuple[int, int] = (9, 9)
) -> Dict[str, Any]:
    """
    동일한 미로 환경에서 BFS와 DFS를 모두 실행하고 종합 비교 분석 리포트를 생성합니다.
    """
    bfs_result = solve_maze_bfs(grid, start, goal)
    dfs_result = solve_maze_dfs(grid, start, goal)

    b_len = bfs_result["path_length"]
    d_len = dfs_result["path_length"]

    b_mem = bfs_result["peak_memory_size"]
    d_mem = dfs_result["peak_memory_size"]

    # 승자 판정
    if b_len < d_len:
        shortest_winner = "BFS (최단 거리 보장)"
    elif b_len == d_len:
        shortest_winner = "공동 동률"
    else:
        shortest_winner = "DFS"

    if b_mem > d_mem:
        memory_winner = "DFS (스택 깊이 O(h)로 메모리 절약)"
    elif b_mem == d_mem:
        memory_winner = "동일 메모리 소비"
    else:
        memory_winner = "BFS"

    return {
        "maze_info": {
            "rows": len(grid),
            "cols": len(grid[0]),
            "start": list(start),
            "goal": list(goal),
            "passable_cells": bfs_result["total_passable"]
        },
        "bfs": bfs_result,
        "dfs": dfs_result,
        "comparison": {
            "path_length": {
                "bfs": b_len,
                "dfs": d_len,
                "difference": abs(b_len - d_len),
                "winner": shortest_winner
            },
            "memory_peak": {
                "bfs_queue_peak": b_mem,
                "dfs_stack_peak": d_mem,
                "winner": memory_winner
            },
            "visited_cells": {
                "bfs": bfs_result["total_visited"],
                "dfs": dfs_result["total_visited"]
            },
            "total_steps": {
                "bfs": bfs_result["total_steps"],
                "dfs": dfs_result["total_steps"]
            },
            "total_time_ms": {
                "bfs": bfs_result["total_time_ms"],
                "dfs": dfs_result["total_time_ms"]
            },
            "big_o_summary": {
                "time_complexity": "모두 O(V + E) (모든 정점과 간선을 최대 1회씩 탐색)",
                "space_complexity_bfs": "O(V) (최대 너비의 모든 노드가 큐에 상주)",
                "space_complexity_dfs": "O(h) (최대 탐색 깊이 h만큼의 호출 스택만 상주)"
            }
        }
    }
