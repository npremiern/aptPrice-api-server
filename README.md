# API 서버 (FastAPI + PostgreSQL)

## 📌 개요
이 프로젝트는 **FastAPI**를 사용하여 PostgreSQL 데이터베이스의 정보를 제공하는 API 서버입니다.
API 키 인증을 지원하며, 특정 서비스 ID를 기반으로 두 개의 테이블을 조인하여 데이터를 조회합니다.
국토교통부_주택 공시가격 정보를 조회하는 서버입니다.

## 🏗️ 프로젝트 구조
```
api-server/
│── main.py            # FastAPI 실행 파일
│── database.py        # PostgreSQL 연결 관리
│── auth.py            # API 키 인증 로직 (여러 개 지원)
│── models.py          # Pydantic 데이터 모델
│── query_loader.py    # SQL 파일 로드
├── query_template.py  # SQL 쿼리 템플릿 처리
├── query_loader.py    # SQL 쿼리 파일 로드
├── query_logging_middleware.py # 쿼리 로깅 미들웨어
├── korean_ip_middleware.py     # 한국 IP 처리 미들웨어
│── queries.sql        # SQL 쿼리 저장 파일
│── .env               # 환경 변수 (DB 정보, API 키 저장)
│── requirements.txt   # 필요한 패키지 목록
│── build_exe.bat      # EXE 파일 빌드용 배치 파일
└── logs/
```

## ⚙️ 환경설정 (.env)
```
DATABASE_URL=postgresql://
DATABASE_USER="postgres"
DATABASE_PASSWD=""
DATABASE_HOST="127.0.0.1"
DATABASE_PORT="5432"
DATABASE_DB="postgres"
API_KEYS=key1,key2,key3
```

## 🚀 실행 방법

### 1️⃣ 가상환경 설정 및 패키지 설치
```sh
pip install -r requirements.txt
```

### 2️⃣ 서버 실행
```sh
uvicorn main:app --reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3️⃣ API 호출 예시
```sh
curl -H "api-key: key1" http://127.0.0.1:8000/data/123
```

### 4️⃣ EXE 파일 빌드
```sh
build_exe.bat
pyinstaller --hidden-import=asyncpg.pgproto.pgproto --onefile --name api_server main.py
```

✅ `dist/api_server.exe` 파일이 생성되며, 이를 실행하면 API 서버가 동작합니다!
```sh
    .env 파일에 환경변수를 설정해야 합니다.
    queries.sql 파일이 같은폴더에 있어야합니다.
```

### 5️⃣ 추가 설명
```sh
# PNU조회
- GET /data/pnu/{pnu} PNU단건조회
- POST /data/pnu PNU 목록조회
    - 쿼리 파라미터
    {"pnu_list": ["1165010100108730001", "1165010100108730011"]}

# 주소 단계별 셀렉트박스 조회
- GET /data/sido 시도 목록조회
- GET /data/sigungu/{sidoCd} 시군구 목록조회
- GET /data/emd/{sigunguCd} 읍면동 목록조회
- GET /data/ri/{emdCd}   동리 목록조회
- GET /data/jibunAddr/{jibunAddr} 지번주소(PNU조회->DB조회)
- GET /bonboo/{legalCd}?spCd=1&bon=755&boo=38   법정동코드, 특수지코드, 본번, 부번
#
```
### 6️⃣ 로그
```sh
# 로그 파일 위치
logs/

# 로그 파일 이름
logs/
├── 2023-04/
│   ├── 2023-04-01.log
│   ├── 2023-04-02.log
│   └── ...
├── 2023-05/
│   ├── 2023-05-01.log
│   └── ...
└── ...
```
