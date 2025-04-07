import asyncpg
import logging
import os
import urllib.parse
from dotenv import load_dotenv
import time

load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 로깅 레벨을 DEBUG로 설정

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

db_user = os.getenv("DATABASE_USER")
db_passwd = os.getenv("DATABASE_PASSWD")
db_host = os.getenv("DATABASE_HOST")
db_port = os.getenv("DATABASE_PORT")
db_dbnm = os.getenv("DATABASE_DB")


db_url = f"postgresql://{db_user}:{urllib.parse.quote(db_passwd)}@{db_host}:{db_port}/{db_dbnm}"


#async def connect_db():
#    return await asyncpg.create_pool(DATABASE_URL)
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
        logger.info("데이터베이스 연결 성공")
        return conn
    except Exception as e:
        logger.error(f"데이터베이스 연결 오류: {str(e)}")
        raise