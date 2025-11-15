목적
- Application Processor의 핀 목록을 사용하여 개별 핀의 기능을 설정하고 중복 여부를 확인할 수 있는 프로그램개발을 목적으로 한다.
- 이후 Application Processor는 AP라고 지칭한다.

프로그램의 형태
- 언어로는 파이썬을 사용하며 파이썬 기반의 웹 서버 프레임워크인 FastAPI를 사용한다.

사용자 핵심 시나리오
- 웹서버는 특정된 디렉토리를 탐색하여 현재 보유하고 있는 AP의 목록을 화면에 띄우고 사용자는 AP를 선택한다.
- 웹서버는 선택된 AP의 핀 목록을 읽어 화면에 테이블을 출력한다.
- 사용자는 테이블에서 "Signal Name"을 변경하고 프로젝트 이름을 지정하여 저장 버튼을 눌러 설정을 저장한다.

입력 데이터
- AP의 핀 목록은 엑셀문서(*.xlsx)로 제공된다.
- 문서에 나열된 여러가지 컬럼 중 다음 컬럼만 사용한다.
    - “Ball Location”
    - "Signal Name"
    - "Function Index"
    - "Default Function"

데이터 저장 디렉토리 구조
- /ap
  - 개별 AP의 핀 목록을 기록한 *.xlsx 파일을 저장하는 디렉토리이다.
  - AP 단위로 *.xlsx 파일을 저장한다.
- /project/AP_NAME
  - AP_NAME에 해당하는 ap를 사용하여 개발된 프로젝트들의 설정 파일들이 저장된다.
  - 프로젝트 단위로 json 파일이 생성된다.

동작 화면 #1
- 사용자가 접속하면 나타나는 화면이다.
- UI
  - "추가" 버튼
    - 사용자가 새로운 AP의 핀설정 파일을 추가 할 때 누른다.
    - 버튼을 누르면 파일 브라우저 창이 뜨고 선택된 파일을 업로드 할 수 있다.
    - 업로드를 실행하면 /project/ 밑에 파일이름에서 추출된 AP이름으로 디렉토리를 생성한다.
    - 파일이름 포맷은 "AP_XXXXX_PinList.xlsx"이다. 여기에서 XXXXX가 AP의 이름이다.
  - 콤보 박스
    - ap 디렉토리 저장된 파일의 제목에서 AP 이름을 추출하여 콤보박스로 나타낸다.
    - 사용자는 콤보박스에서 AP를 선택한다.
  - "다음" 버튼
    - 버튼을 눌러 다음 화면으로 진입한다.
    - 이 때 선택된 AP의 파일 이름과 AP 이름을 전달한다.

동작 화면 #2
- 사용자가 실제로 핀 설정을 편집하는 화면이다.
- UI
  - 프로젝트 콤보 박스
    - /project/AP_NAME 에 저장된 프로젝트를 선택할 수 있다.
    - 프로젝트 이름을 나타낸다.
  - "Save" 버튼
    - 프로젝트에 대한 설정을 저장하는 화면을 띄운다.
    - 이 화면에서는 기존 프로젝트의 설정을 업데이트 할 것인지 새로운 프로젝트로 추가할 것인지 묻는다.
    - 업데이트를 선택하면 기존의 설정을 변경하고 새로운 프로젝트를 선택했다면 프로젝트의 이름을 입력받고 json 파일 형태로 /project/AP_NAME 디렉토리에 저장한다.
    - 파일이름 포맷은 "Project_XXXXX.json"이다. 여기에서 XXXXX가 프로젝트의 이름이다.
    - json에 저장되는 맵의 키는 "ball location"을 사용하고 값은 선택된 signal의 인덱스를 사용한다.
  - "Load" 버튼
    - 프로젝트 콤보박스에 선택된 프로젝트의 설정을 로드하여 테이블에 반영한다.
    - 프로젝트에 해당하는 json 파일을 열고 각 "ball location"을 키로 저장된 인덱스를 사용하여 테이블의 콤보박스들을 업데이트 한다.
  - 테이블
    - 핀 설정 파일을 파싱하여 앞에서 정의된 컬럼 정보들을 추출한다. 다음 지침에 따라 맵 자료구조를 만든다.
      - ball 맵
        - "Ball Location"을 키로 사용한다. 중복은 허용하지 않는다.
        - 동일한 "Ball Location"을 가진 "signal name"을 모아 배열로 만들되 "Function Index"를 각 시그널의 인덱스로 사용한다.
        - "Ball Location"의 "Default Function"을 저장한다.
        - 예를 들면 다음과 같은 구조의 자료 구조이다.
          - ball_location: [ball_name:NAME1 signal:{signal1 signal2 signal3} reset_func:0]
      - signal 맵
        - 파일의 전체 "Signal Name"을 키로 사용한다. 중복은 허용하지 않는다.
        - "Signal Name"이 속하는 "Ball Location"을 추출하여 배열로 만들어 저장한다.
        - 예를 들면 다음과 같은 구조이다.
          - signal_name: [ball_location:{BALL1 BALL2 BALL3}]
    - 첫번째 컬럼은 1부터 시작하는 자동 증가 인덱스이다.
    - 두번째 컬럼은 "ball location"을 출력한다.
    - 세번째 컬럼은 "signal name"을 콤보 박스 형태로 출력한다.
      - 앞에서 생성한 ball 맵을 참조하여 "ball location"에 해당하는 "signal name"을 콤보박스에 채운다.
      - "Function Index"를 콤보박스에서의 인덱스로 사용한다.
      - "Default Function"은 콤보박스에 나타나는 아이템의 인덱스로 사용한다.
      - 콤보박스에서 사용자가 "Signal Name"을 변경하면 선택한 "Signal Name"이 다른 "Ball Location"에서 사용중인지 signal 맵과 현재 테이블의 선택을 비교 확인하여 사용중이라면 팝업을 띄우고 사용자의 선택을 되돌린다.


