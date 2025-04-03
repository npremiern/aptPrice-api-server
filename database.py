import asyncpg
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

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
        return await asyncpg.create_pool(
            db_url,
            min_size=5,
            max_size=20,
            command_timeout=60.0,
            server_settings={
                'application_name': 'facc-api-server'  # 서버 로그에서 식별하기 쉽게
            }
        )
    except Exception as e:
        print(f"데이터베이스 연결 실패: {str(e)}")
        raise