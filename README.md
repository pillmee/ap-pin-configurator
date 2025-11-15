# 🔌 AP Pin Configurator

Application Processor의 핀 목록을 사용하여 개별 핀의 기능을 설정하고 중복 여부를 확인할 수 있는 웹 기반 프로그램입니다.

## 📋 주요 기능

- **AP 관리**: 엑셀 파일(*.xlsx)로 제공되는 AP 핀 목록 업로드 및 관리
- **핀 설정 편집**: 개별 핀의 Signal Name을 선택하고 설정
- **중복 체크**: Signal Name이 다른 Ball Location에서 사용 중인지 자동 확인
- **프로젝트 관리**: 핀 설정을 프로젝트 단위로 저장 및 로드

## 🚀 시작하기

### 필요 조건

- Python 3.8 이상
- pip (Python 패키지 관리자)

### 설치

1. 저장소를 클론하거나 다운로드합니다.

2. 필요한 패키지를 설치합니다:
```bash
pip install -r requirements.txt
```

### 실행

1. 프로그램을 실행합니다:
```bash
python main.py
```

또는

```bash
uvicorn main:app --reload
```

2. 웹 브라우저에서 다음 주소로 접속합니다:
```
http://localhost:8000
```

## 📁 프로젝트 구조

```
pin configurator/
├── ap/                      # AP 핀 설정 파일(*.xlsx) 저장 디렉토리
├── project/                 # 프로젝트 설정 파일(*.json) 저장 디렉토리
│   └── AP_NAME/            # AP별 프로젝트 디렉토리
├── static/                  # 정적 파일 (CSS, JS, 이미지 등)
├── templates/              # HTML 템플릿
│   ├── index.html          # 메인 화면 (AP 선택)
│   └── editor.html         # 핀 설정 편집 화면
├── main.py                 # FastAPI 메인 애플리케이션
├── excel_parser.py         # 엑셀 파일 파싱 모듈
├── project_manager.py      # 프로젝트 저장/로드 모듈
└── requirements.txt        # Python 의존성 목록
```

## 📖 사용 방법

### 1. AP 추가

1. 메인 화면에서 "파일 선택" 버튼을 클릭합니다.
2. AP 핀 설정 파일을 선택합니다. (형식: `AP_XXXXX_PinList.xlsx`)
3. "업로드" 버튼을 클릭하여 파일을 등록합니다.

### 2. AP 선택 및 핀 설정 편집

1. 콤보박스에서 작업할 AP를 선택합니다.
2. "다음" 버튼을 클릭하여 편집 화면으로 이동합니다.
3. 테이블에서 각 Ball Location의 Signal Name을 콤보박스로 선택합니다.
4. Signal Name 중복 시 자동으로 경고가 표시됩니다.

### 3. 프로젝트 저장

1. "Save" 버튼을 클릭합니다.
2. 다음 중 하나를 선택합니다:
   - **새 프로젝트로 저장**: 프로젝트 이름을 입력하여 새로 저장
   - **기존 프로젝트 업데이트**: 선택된 프로젝트의 설정을 업데이트
3. "저장" 버튼을 클릭하여 완료합니다.

### 4. 프로젝트 로드

1. 프로젝트 콤보박스에서 불러올 프로젝트를 선택합니다.
2. "Load" 버튼을 클릭합니다.
3. 테이블에 저장된 설정이 자동으로 반영됩니다.

## 📊 AP 핀 설정 파일 형식

엑셀 파일은 다음 컬럼을 포함해야 합니다:

- **Ball Location**: 핀의 물리적 위치
- **Signal Name**: 핀의 신호 이름
- **Function Index**: 기능 인덱스 (숫자)
- **Default Function**: 기본 기능 여부 (TRUE/FALSE 또는 유사 값)

### 파일명 형식
```
AP_[AP이름]_PinList.xlsx
```

예시: `AP_S5E8825_PinList.xlsx`

## 🔧 API 엔드포인트

### GET `/`
메인 화면 (AP 선택)

### GET `/editor`
핀 설정 편집 화면

### GET `/api/ap-list`
등록된 AP 목록 조회

### POST `/api/upload-ap`
새 AP 파일 업로드

### GET `/api/pin-list/{ap_name}`
특정 AP의 핀 목록 조회

### GET `/api/projects/{ap_name}`
특정 AP의 프로젝트 목록 조회

### GET `/api/project/{ap_name}/{project_name}`
프로젝트 설정 로드

### POST `/api/project/{ap_name}`
프로젝트 설정 저장

### POST `/api/check-signal-duplicate`
Signal Name 중복 체크

## 🛠️ 기술 스택

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Data Processing**: openpyxl (Excel 파일 처리)
- **Server**: Uvicorn (ASGI 서버)

## 📝 프로젝트 설정 파일 형식

프로젝트 설정은 JSON 형식으로 저장됩니다:

```json
{
  "A1": 0,
  "A2": 1,
  "B1": 2,
  "B2": 0
}
```

- **키(Key)**: Ball Location
- **값(Value)**: 선택된 Signal의 Function Index

## ⚠️ 주의사항

- AP 파일은 반드시 `AP_XXXXX_PinList.xlsx` 형식의 파일명을 사용해야 합니다.
- 동일한 Signal Name을 여러 Ball Location에서 동시에 사용할 수 없습니다.
- 프로젝트 이름에는 파일시스템에서 허용하지 않는 특수문자를 사용할 수 없습니다.

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 개발되었습니다.

## 👥 기여

버그 리포트나 기능 제안은 환영합니다!

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.
