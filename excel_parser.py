"""
Excel 파일 파싱 모듈
AP의 핀 목록 엑셀 파일(*.xlsx)을 읽어 필요한 컬럼 정보를 추출
"""
import openpyxl
from typing import List, Dict, Tuple


def parse_pin_list(file_path: str) -> Tuple[Dict[str, Dict], Dict[str, List[str]]]:
    """
    엑셀 파일에서 핀 목록 정보를 파싱하여 ball 맵과 signal 맵 생성
    
    Args:
        file_path: 엑셀 파일 경로
        
    Returns:
        Tuple[ball_map, signal_map]
        
        ball_map: Ball Location을 키로 하는 맵
        {
            "ball_location": {
                "signals": [signal_name],  # Function Index 순서대로 정렬
                "default_index": int        # Default Function의 인덱스
            }
        }
        
        signal_map: Signal Name을 키로 하는 맵
        {
            "signal_name": [ball_location1, ball_location2, ...]
        }
    """
    workbook = openpyxl.load_workbook(file_path, data_only=True)
    sheet = workbook.active
    
    # 헤더 행 찾기 (첫 번째 행이라고 가정)
    header_row = 1
    headers = {}
    
    for col_idx, cell in enumerate(sheet[header_row], start=1):
        if cell.value:
            headers[cell.value] = col_idx
    
    # 필요한 컬럼 확인
    required_columns = ["Ball Location", "Signal Name", "Function Index", "Default Function"]
    for col in required_columns:
        if col not in headers:
            raise ValueError(f"필수 컬럼을 찾을 수 없습니다: {col}")
    
    # 컬럼 인덱스
    ball_loc_col = headers["Ball Location"]
    signal_name_col = headers["Signal Name"]
    func_index_col = headers["Function Index"]
    default_func_col = headers["Default Function"]
    
    # 임시 데이터 저장용 (Function Index별로 정렬하기 위해)
    temp_data = []
    
    for row_idx in range(header_row + 1, sheet.max_row + 1):
        ball_location = sheet.cell(row_idx, ball_loc_col).value
        signal_name = sheet.cell(row_idx, signal_name_col).value
        function_index = sheet.cell(row_idx, func_index_col).value
        default_function = sheet.cell(row_idx, default_func_col).value
        
        # 빈 행 건너뛰기
        if not ball_location:
            continue
        
        # Ball Location을 문자열로 변환
        ball_location = str(ball_location).strip()
        
        # Signal Name을 문자열로 변환
        signal_name = str(signal_name).strip() if signal_name else ""
        
        # Function Index를 정수로 변환
        try:
            function_index = int(function_index) if function_index is not None else 0
        except (ValueError, TypeError):
            function_index = 0
        
        # Default Function 여부 확인
        is_default = False
        if default_function:
            default_str = str(default_function).strip().upper()
            is_default = default_str in ["TRUE", "YES", "1", "X", "O"]
        
        temp_data.append({
            "ball_location": ball_location,
            "signal_name": signal_name,
            "function_index": function_index,
            "is_default": is_default
        })
    
    # Ball 맵 생성
    ball_map = {}
    signal_map = {}
    
    for item in temp_data:
        ball_loc = item["ball_location"]
        signal_name = item["signal_name"]
        func_idx = item["function_index"]
        is_default = item["is_default"]
        
        # Ball 맵 구성
        if ball_loc not in ball_map:
            ball_map[ball_loc] = {
                "signals": {},  # {function_index: signal_name}
                "default_index": 0
            }
        
        ball_map[ball_loc]["signals"][func_idx] = signal_name
        
        if is_default:
            ball_map[ball_loc]["default_index"] = func_idx
        
        # Signal 맵 구성
        if signal_name and signal_name not in signal_map:
            signal_map[signal_name] = []
        
        if signal_name and ball_loc not in signal_map[signal_name]:
            signal_map[signal_name].append(ball_loc)
    
    # Ball 맵의 signals를 Function Index 순으로 정렬된 리스트로 변환
    for ball_loc, data in ball_map.items():
        sorted_signals = [data["signals"][idx] for idx in sorted(data["signals"].keys())]
        ball_map[ball_loc]["signals"] = sorted_signals
    
    workbook.close()
    
    return ball_map, signal_map


def get_default_signal_index(ball_data: Dict) -> int:
    """
    특정 Ball Location의 기본 Signal Index 찾기
    
    Args:
        ball_data: ball_map의 값 (특정 ball location의 데이터)
        
    Returns:
        기본 Signal의 인덱스 (0-based), 없으면 0
    """
    return ball_data.get("default_index", 0)


if __name__ == "__main__":
    # 테스트 코드
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            ball_map, signal_map = parse_pin_list(file_path)
            
            print(f"총 {len(ball_map)}개의 Ball Location 발견")
            print(f"총 {len(signal_map)}개의 고유 Signal Name 발견")
            
            # 처음 3개 Ball Location 출력
            print("\n[Ball Map]")
            for idx, (ball_loc, data) in enumerate(list(ball_map.items())[:3]):
                print(f"\nBall Location: {ball_loc}")
                print(f"  Signals: {len(data['signals'])}개")
                print(f"  Default Index: {data['default_index']}")
                for sig_idx, sig_name in enumerate(data['signals']):
                    default_mark = " (DEFAULT)" if sig_idx == data['default_index'] else ""
                    print(f"    [{sig_idx}] {sig_name}{default_mark}")
            
            # 처음 3개 Signal 출력
            print("\n[Signal Map]")
            for idx, (sig_name, ball_locs) in enumerate(list(signal_map.items())[:3]):
                print(f"\nSignal: {sig_name}")
                print(f"  Used in: {', '.join(ball_locs)}")
        except Exception as e:
            print(f"오류: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("사용법: python excel_parser.py <엑셀파일경로>")
