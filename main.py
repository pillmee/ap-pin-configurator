"""
AP Pin Configurator - FastAPI Backend
Application Processor의 핀 목록을 사용하여 개별 핀의 기능을 설정하고 중복 여부를 확인
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.requests import Request
from pathlib import Path
import shutil
import os
from typing import List, Dict
import json

from excel_parser import parse_pin_list
from project_manager import save_project, load_project, get_projects

app = FastAPI(title="AP Pin Configurator")

# 디렉토리 설정
AP_DIR = Path("ap")
PROJECT_DIR = Path("project")
STATIC_DIR = Path("static")
TEMPLATES_DIR = Path("templates")

# 디렉토리 생성
AP_DIR.mkdir(exist_ok=True)
PROJECT_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# Static files and templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """메인 화면 (동작 화면 #1)"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/editor", response_class=HTMLResponse)
async def editor(request: Request):
    """핀 설정 편집 화면 (동작 화면 #2)"""
    return templates.TemplateResponse("editor.html", {"request": request})


@app.get("/api/ap-list")
async def get_ap_list():
    """
    AP 목록 조회
    ap 디렉토리에서 AP_XXXXX_PinList.xlsx 형식의 파일을 찾아 AP 이름 반환
    """
    ap_list = []
    
    for file_path in AP_DIR.glob("*.xlsx"):
        filename = file_path.stem  # 확장자 제외한 파일명
        # AP_XXXXX_PinList 형식에서 XXXXX 추출
        if filename.startswith("AP_") and filename.endswith("_PinList"):
            ap_name = filename[3:-8]  # "AP_" 제거, "_PinList" 제거
            ap_list.append({
                "name": ap_name,
                "filename": file_path.name
            })
    
    return {"ap_list": ap_list}


@app.post("/api/upload-ap")
async def upload_ap_file(file: UploadFile = File(...)):
    """
    새로운 AP 핀 설정 파일 업로드
    파일명 형식: AP_XXXXX_PinList.xlsx
    """
    filename = file.filename
    
    # 파일명 검증
    if not filename.startswith("AP_") or not filename.endswith("_PinList.xlsx"):
        raise HTTPException(
            status_code=400,
            detail="파일명 형식이 올바르지 않습니다. AP_XXXXX_PinList.xlsx 형식이어야 합니다."
        )
    
    # AP 이름 추출
    ap_name = filename[3:-13]  # "AP_" 제거, "_PinList.xlsx" 제거
    
    # 파일 저장
    file_path = AP_DIR / filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 프로젝트 디렉토리 생성
    project_ap_dir = PROJECT_DIR / ap_name
    project_ap_dir.mkdir(exist_ok=True)
    
    return {
        "success": True,
        "ap_name": ap_name,
        "filename": filename
    }


@app.get("/api/pin-list/{ap_name}")
async def get_pin_list(ap_name: str):
    """
    특정 AP의 핀 목록 조회
    엑셀 파일을 파싱하여 ball_map과 signal_map 반환
    """
    # AP 파일 찾기
    filename = f"AP_{ap_name}_PinList.xlsx"
    file_path = AP_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"AP 파일을 찾을 수 없습니다: {filename}")
    
    try:
        ball_map, signal_map = parse_pin_list(str(file_path))
        return {
            "ball_map": ball_map,
            "signal_map": signal_map
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 파싱 중 오류 발생: {str(e)}")


@app.get("/api/projects/{ap_name}")
async def get_project_list(ap_name: str):
    """특정 AP의 프로젝트 목록 조회"""
    project_ap_dir = PROJECT_DIR / ap_name
    
    if not project_ap_dir.exists():
        return {"projects": []}
    
    projects = []
    for file_path in project_ap_dir.glob("Project_*.json"):
        project_name = file_path.stem[8:]  # "Project_" 제거
        projects.append({
            "name": project_name,
            "filename": file_path.name
        })
    
    return {"projects": projects}


@app.get("/api/project/{ap_name}/{project_name}")
async def load_project_config(ap_name: str, project_name: str):
    """프로젝트 설정 로드 (ball_location: signal_name 형태)"""
    filename = f"Project_{project_name}.json"
    file_path = PROJECT_DIR / ap_name / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없습니다: {project_name}")
    
    try:
        config = load_project(str(file_path))
        return {"config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로젝트 로드 중 오류 발생: {str(e)}")


@app.post("/api/project/{ap_name}")
async def save_project_config(ap_name: str, data: Dict):
    """
    프로젝트 설정 저장
    data: {
        "project_name": str,
        "config": dict  # {ball_location: signal_name}
        "overwrite": bool
    }
    """
    project_name = data.get("project_name")
    config = data.get("config")
    overwrite = data.get("overwrite", False)
    
    if not project_name or not config:
        raise HTTPException(status_code=400, detail="프로젝트 이름과 설정이 필요합니다.")
    
    filename = f"Project_{project_name}.json"
    file_path = PROJECT_DIR / ap_name / filename
    
    # 프로젝트 디렉토리 생성
    (PROJECT_DIR / ap_name).mkdir(exist_ok=True)
    
    # 파일이 존재하고 overwrite가 False인 경우
    if file_path.exists() and not overwrite:
        raise HTTPException(status_code=409, detail="프로젝트가 이미 존재합니다.")
    
    try:
        save_project(str(file_path), config)
        return {
            "success": True,
            "project_name": project_name,
            "filename": filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로젝트 저장 중 오류 발생: {str(e)}")


@app.post("/api/check-signal-duplicate")
async def check_signal_duplicate(data: Dict):
    """
    Signal Name 중복 체크
    현재 테이블의 선택 상태와 signal_map을 비교하여 중복 확인
    data: {
        "ap_name": str,
        "signal_name": str,
        "current_ball_location": str,
        "current_selections": dict  # {ball_location: signal_name}
    }
    """
    ap_name = data.get("ap_name")
    signal_name = data.get("signal_name")
    current_ball_location = data.get("current_ball_location")
    current_selections = data.get("current_selections", {})
    
    # 현재 선택 상태에서 다른 Ball Location이 같은 Signal을 사용하는지 확인
    for ball_loc, selected_signal in current_selections.items():
        if ball_loc != current_ball_location and selected_signal == signal_name:
            return {
                "duplicate": True,
                "ball_location": ball_loc
            }
    
    return {"duplicate": False}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
