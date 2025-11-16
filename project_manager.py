"""
프로젝트 설정 저장/로드 모듈
프로젝트 설정을 JSON 형식으로 저장하고 불러오기
"""
import json
from typing import Dict
from pathlib import Path


def save_project(file_path: str, config: Dict[str, int]) -> None:
    """
    프로젝트 설정을 JSON 파일로 저장
    
    Args:
        file_path: 저장할 파일 경로 (Project_XXXXX.json)
        config: 설정 딕셔너리 {ball_location: function_index}
    """
    # 파일 디렉토리가 없으면 생성
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def load_project(file_path: str) -> Dict[str, int]:
    """
    JSON 파일에서 프로젝트 설정 로드
    
    Args:
        file_path: 로드할 파일 경로
        
    Returns:
        설정 딕셔너리 {ball_location: function_index}
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


def get_projects(ap_dir: Path) -> list:
    """
    특정 AP 디렉토리의 프로젝트 목록 조회
    
    Args:
        ap_dir: AP 프로젝트 디렉토리 경로
        
    Returns:
        프로젝트 이름 리스트
    """
    projects = []
    
    if not ap_dir.exists():
        return projects
    
    for file_path in ap_dir.glob("Project_*.json"):
        project_name = file_path.stem[8:]  # "Project_" 제거
        projects.append(project_name)
    
    return sorted(projects)


def validate_config(config: Dict[str, int], pin_data: list) -> tuple[bool, str]:
    """
    설정이 유효한지 검증
    
    Args:
        config: 검증할 설정 {ball_location: function_index}
        pin_data: parse_pin_list에서 반환한 핀 데이터
        
    Returns:
        (유효 여부, 오류 메시지)
    """
    # Ball Location별 유효한 Function Index 맵 생성
    valid_indices = {}
    for pin in pin_data:
        ball_loc = pin["ball_location"]
        valid_indices[ball_loc] = [sig["function_index"] for sig in pin["signals"]]
    
    # 설정 검증
    for ball_loc, func_idx in config.items():
        # Ball Location이 존재하는지 확인
        if ball_loc not in valid_indices:
            return False, f"알 수 없는 Ball Location: {ball_loc}"
        
        # Function Index가 유효한지 확인
        if func_idx not in valid_indices[ball_loc]:
            return False, f"Ball Location '{ball_loc}'에 유효하지 않은 Function Index: {func_idx}"
    
    return True, ""


if __name__ == "__main__":
    # 테스트 코드
    import tempfile
    import os
    
    # 임시 설정 생성 및 저장
    test_config = {
        "A1": 0,
        "A2": 1,
        "B1": 2,
        "B2": 0
    }
    
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        print(f"테스트 설정 저장: {temp_path}")
        save_project(temp_path, test_config)
        
        print("설정 로드:")
        loaded_config = load_project(temp_path)
        print(loaded_config)
        
        print(f"\n원본과 로드된 설정이 일치: {test_config == loaded_config}")
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.unlink(temp_path)
