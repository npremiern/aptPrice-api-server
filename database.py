import asyncpg
import logging
import os
import urllib.parse
from dotenv import load_dotenv, find_dotenv
import time

# 로거 설정 (먼저 설정해야 로깅이 가능)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 로깅 레벨을 DEBUG로 설정

# .env 파일 경로 찾기 및 로깅
def load_env_file(path=None):
    """지정된 경로 또는 기본 경로에서 .env 파일을 로드하고 경로를 로깅합니다."""
    if path and os.path.exists(path):
        dotenv_path = os.path.abspath(path)
        load_dotenv(dotenv_path)
        logger.info(f".env 파일 로드됨: {dotenv_path}")
        return True
    return False

# 현재 디렉토리 .env 파일 로드 시도
default_env = find_dotenv()
if default_env:
    logger.info(f"기본 .env 파일 발견: {os.path.abspath(default_env)}")
    load_dotenv(default_env)
else:
    logger.warning("기본 .env 파일을 찾을 수 없습니다.")

# 추가 경로에서 .env 파일 로드 시도
additional_paths = [
    '../.env',
    'dist/.env',
    './.env',
    os.path.join(os.getcwd(), '.env')
]

for path in additional_paths:
    if load_env_file(path):
        logger.info(f"추가 .env 파일 로드됨: {path}")

# 환경 변수 로깅
logger.info(f"현재 작업 디렉토리: {os.getcwd()}")
logger.info(f"환경 변수 확인: DATABASE_USER={os.getenv('DATABASE_USER')}, DATABASE_HOST={os.getenv('DATABASE_HOST')}")

# 쿼리 로깅 클래스
class LoggingConnection(asyncpg.Connection):
    async def execute(self, query, *args, **kwargs):
        start_time = time.time()
        # 쿼리가 너무 길면 잘릴 수 있으므로 로깅 방식 개선
        logger.info(f"실행 쿼리 (길이: {len(query)}): {query}")
        logger.info(f"쿼리 파라미터: {args}")
        
        try:
            result = await super().execute(query, *args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"쿼리 실행 시간: {execution_time:.4f}초")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"쿼리 실행 오류: {str(e)}, 실행 시간: {execution_time:.4f}초")
            raise

    async def fetch(self, query, *args, **kwargs):
        start_time = time.time()
        logger.info(f"실행 쿼리: {query}")
        logger.info(f"쿼리 파라미터: {args}")
        
        try:
            result = await super().fetch(query, *args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"쿼리 결과 행 수: {len(result)}, 실행 시간: {execution_time:.4f}초")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"쿼리 실행 오류: {str(e)}, 실행 시간: {execution_time:.4f}초")
            raise

# 환경 변수 로드
db_user = os.getenv("DATABASE_USER")
db_passwd = os.getenv("DATABASE_PASSWD")
db_host = os.getenv("DATABASE_HOST")
db_port = os.getenv("DATABASE_PORT")
db_dbnm = os.getenv("DATABASE_DB")

# 환경 변수 값 로깅 (비밀번호 제외)
logger.info(f"데이터베이스 설정: USER={db_user}, HOST={db_host}, PORT={db_port}, DB={db_dbnm}")

# 비밀번호 처리 (None인 경우 빈 문자열로)
passwd_quoted = urllib.parse.quote(db_passwd) if db_passwd is not None else ""

# 데이터베이스 URL 생성
db_url = f"postgresql://{db_user}:{passwd_quoted}@{db_host}:{db_port}/{db_dbnm}"
# 비밀번호를 마스킹하여 로깅
masked_url = db_url.replace(passwd_quoted, "********") if passwd_quoted else db_url
logger.info(f"데이터베이스 URL: {masked_url}")

async def connect_db():
    try:
        # 로깅 연결 클래스 사용
        conn = await asyncpg.create_pool(
            db_url,
            min_size=5,
            max_size=20,
            command_timeout=60.0,
            server_settings={
                'application_name': 'facc-api-server'  # 서버 로그에서 식별하기 쉽게
            },
            connection_class=LoggingConnection
        )
        logger.info(f"데이터베이스 연결 성공: {db_host}:{db_port}")
        return conn
    except Exception as e:
        logger.error(f"데이터베이스 연결 오류: {str(e)}")
        # 연결 실패 시 환경 변수 정보 로깅 (비밀번호 제외)
        logger.error(f"환경 변수: DATABASE_USER={db_user}, DATABASE_HOST={db_host}, DATABASE_PORT={db_port}, DATABASE_DB={db_dbnm}")
        raise