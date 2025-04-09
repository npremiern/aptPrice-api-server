from fastapi import FastAPI, Depends, Request, Body
import database
from auth import verify_api_key
from models import ServiceData
from query_loader import queries  # 쿼리 로드 추가
from contextlib import asynccontextmanager
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from korean_ip_middleware import korean_ip_middleware
from logging.handlers import TimedRotatingFileHandler
import os
import time
import psutil
import functools
from query_template import parse_template
from sqlalchemy import select, and_, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import aiohttp
import urllib.parse
import json
import datetime
from fastapi.responses import StreamingResponse, Response, HTMLResponse, FileResponse
from io import BytesIO
import pandas as pd
from fastapi.staticfiles import StaticFiles

# 로그 디렉토리 구조 설정 (월별 폴더)
def get_log_path():
    """월별 폴더와 일별 로그 파일 경로를 생성합니다."""
    today = datetime.datetime.now()
    month_folder = today.strftime('%Y-%m')  # 2023-04 형식
    log_folder = os.path.join('logs', month_folder)
    
    # 월별 폴더 생성
    os.makedirs(log_folder, exist_ok=True)
    
    # 일별 로그 파일 경로
    log_file = today.strftime('%Y-%m-%d.log')  # 2023-04-15.log 형식
    return os.path.join(log_folder, log_file)

# 기본 로그 디렉토리 생성
os.makedirs('logs', exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,  # 기본 로깅 레벨
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # 일별 로그 파일 핸들러
        TimedRotatingFileHandler(
            get_log_path(),
            when='midnight',  # 매일 자정에 새 파일 생성
            interval=1,       # 1일 간격
            backupCount=30,   # 최대 30일치 보관
            encoding='utf-8'
        ),
        logging.StreamHandler()  # 콘솔 출력
    ]
)

# 데이터베이스 로거 설정
db_logger = logging.getLogger('database')
db_logger.setLevel(logging.DEBUG)  # 데이터베이스 로거는 DEBUG 레벨로 설정

# 메인 로거
logger = logging.getLogger(__name__)

# 로그 핸들러 업데이트 함수
def update_log_handlers():
    """로그 핸들러를 현재 날짜에 맞게 업데이트합니다."""
    root_logger = logging.getLogger()
    
    # 기존 파일 핸들러 제거
    for handler in root_logger.handlers[:]:
        if isinstance(handler, TimedRotatingFileHandler):
            root_logger.removeHandler(handler)
    
    # 새 파일 핸들러 추가
    file_handler = TimedRotatingFileHandler(
        get_log_path(),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(file_handler)
    
    logger.info(f"로그 파일 경로 업데이트: {get_log_path()}")

# 로깅 함수 정의
def log_query_results(rows: List[Dict[str, Any]], query_name: str = "쿼리") -> None:
    """
    쿼리 결과를 로깅하는 함수
    
    Args:
        rows: 데이터베이스 쿼리 결과 행 목록
        query_name: 로그에 표시할 쿼리 이름
    """
    try:
        # 날짜가 바뀌었는지 확인하고 필요시 로그 핸들러 업데이트
        update_log_handlers()
        
        logger.info(f"{query_name} 결과 행 수: {len(rows)}")
        if rows:
            # 샘플 데이터 일부 로깅 (민감 정보 제외)
            sample_data = dict(rows[0])
            # 민감 정보 필터링 (예: 비밀번호, 개인정보 등)
            filtered_data = {k: v for k, v in sample_data.items() 
                            if not any(sensitive in k.lower() for sensitive in ['password', 'secret', 'token'])}
            logger.info(f"{query_name} 샘플 데이터: {filtered_data}")
            
            # 성능 정보 로깅 (선택 사항)
            if hasattr(rows, 'execution_time'):
                logger.info(f"{query_name} 실행 시간: {rows.execution_time:.4f}초")
    except Exception as e:
        logger.error(f"{query_name} 결과 로깅 중 오류 발생: {str(e)}")

# 쿼리 파라미터를 딕셔너리로 변환하는 함수
async def get_query_params(request: Request) -> Dict[str, str]:
    """
    요청의 쿼리 파라미터를 딕셔너리로 변환
    
    Args:
        request: FastAPI 요청 객체
    
    Returns:
        쿼리 파라미터를 포함하는 딕셔너리
    """
    params = {}
    for key, value in request.query_params.items():
        params[key] = value
    return params

@asynccontextmanager
async def lifespan(app):
    # 시작 시 실행할 코드
    app.state.db = await database.connect_db()
    yield
    # 종료 시 실행할 코드
    await app.state.db.close()

app = FastAPI(lifespan=lifespan)

# 미들웨어 등록
#app.middleware("http")(korean_ip_middleware)

# 미들웨어를 직접 정의
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    # 요청 시작 시간
    start_time = time.time()
    
    # 요청 경로 및 메서드 로깅
    path = request.url.path
    method = request.method
    logger.info(f"요청 시작: {method} {path}")
    
    # 요청 처리 전 메모리 사용량 (선택 사항)
    process = psutil.Process()
    memory_before = process.memory_info().rss / 1024 / 1024  # MB 단위
    
    # 다음 미들웨어 또는 엔드포인트 호출
    response = await call_next(request)
    
    # 요청 처리 시간 계산
    process_time = time.time() - start_time
    
    # 요청 처리 후 메모리 사용량 (선택 사항)
    memory_after = process.memory_info().rss / 1024 / 1024  # MB 단위
    memory_diff = memory_after - memory_before
    
    # 상세 성능 정보 로깅
    logger.info(
        f"요청 완료: {method} {path} - "
        f"상태 코드: {response.status_code}, "
        f"처리 시간: {process_time:.4f}초, "
        f"메모리 사용: {memory_diff:.2f}MB"
    )
    
    # 응답 헤더에 처리 시간 추가 (클라이언트에게 성능 정보 제공)
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

@app.middleware("http")
async def download_middleware(request: Request, call_next):
    # 원래 경로 저장
    original_path = request.url.path
    
    # 다운로드 접두사 확인 (/download/로 시작하는지)
    is_download = original_path.startswith("/download/")
    
    if is_download:
        # 원래 API 경로로 변환 (접두사 제거)
        request.scope["path"] = original_path.replace("/download/", "/", 1)
    
    # 다운로드 요청이 아니면 일반 처리
    if not is_download:
        return await call_next(request)
    
    # 다운로드 요청인 경우 처리
    response = await call_next(request)
    
    # 다운로드 요청이면 응답을 파일로 변환
    if is_download and response.status_code == 200:
        # 응답 본문 가져오기
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        
        # JSON 데이터 파싱
        try:
            data = json.loads(body.decode('utf-8'))  # UTF-8로 명시적 디코딩
            
            # 데이터 추출 (대부분의 API가 'data' 키에 결과를 저장)
            result_data = data.get('data', data)
            
            if isinstance(result_data, list):
                # 파일명 생성 (경로에서 추출)
                filename = original_path.split('/')[-1]
                if not filename:
                    filename = "data"
                
                # 파일 형식 확인 (쿼리 파라미터에서)
                file_format = request.query_params.get('format', 'csv').lower()
                
                # 데이터프레임 변환
                df = pd.DataFrame(result_data)
                
                # 파일 생성
                output = BytesIO()
                if file_format == 'excel' or file_format == 'xlsx':
                    df.to_excel(output, index=False)
                    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    filename = f"{filename}.xlsx"
                else:  # 기본값은 CSV
                    df.to_csv(output, index=False, encoding='utf-8-sig')  # BOM 포함 UTF-8
                    media_type = "text/csv"
                    filename = f"{filename}.csv"
                
                output.seek(0)
                
                # 파일명 URL 인코딩 (한글 지원)
                encoded_filename = urllib.parse.quote(filename)
                
                # 스트리밍 응답으로 반환 - Content-Length 헤더 없이
                return StreamingResponse(
                    iter([output.getvalue()]),
                    media_type=media_type,
                    headers={
                        'Content-Disposition': f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}'
                    }
                )
        except Exception as e:
            logger.error(f"파일 다운로드 변환 중 오류: {str(e)}")
            # 오류 발생 시 새 응답 생성
            return Response(
                content=body,
                status_code=response.status_code,
                headers={k: v for k, v in response.headers.items() if k.lower() != 'content-length'},
                media_type=response.media_type
            )
    
    # 원래 응답 반환 (200이 아닌 경우)
    return response

def measure_time(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # 함수 이름 로깅
        logger.info(f"엔드포인트 시작: {func.__name__}")
        
        # 함수 실행
        result = await func(*args, **kwargs)
        
        # 실행 시간 계산
        execution_time = time.time() - start_time
        
        # 성능 정보 로깅
        logger.info(f"엔드포인트 완료: {func.__name__}, 실행 시간: {execution_time:.4f}초")
        
        # 결과가 딕셔너리인 경우 실행 시간 추가
        if isinstance(result, dict):
            result["execution_time"] = execution_time
        
        return result
    return wrapper

# API 테스트 페이지 제공
@app.get("/api-test", response_class=HTMLResponse)
async def get_api_test_page():
    """API 테스트 페이지를 제공합니다."""
    try:
        with open("api_test.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"API 테스트 페이지 로드 오류: {str(e)}")
        return HTMLResponse(content=f"<h1>오류 발생</h1><p>{str(e)}</p>")


@app.get("/data/bldgReg/{bldgReg}") # 건축물대장 조회
async def get_building_data(bldgReg: str, api_key: str = Depends(verify_api_key)):
    async with app.state.db.acquire() as conn:
        query = queries["GET_BUILDING_LEDGER"]
        rows = await conn.fetch(query, bldgReg)
        
        # 로깅 함수 호출
        log_query_results(rows, "건축물대장 조회")
        
        # 딕셔너리 리스트로 변환
        result = [dict(row) for row in rows]
        return result

# PNU 조회 엔드포인트
@app.get("/data/pnu/{pnu}")
async def get_pnu_data(pnu: str, request: Request, api_key: str = Depends(verify_api_key)):
    # 쿼리 파라미터 가져오기
    params = await get_query_params(request)
    logger.info(f"PNU 단건 조회 파라미터: {params}")
    
    async with app.state.db.acquire() as conn:
        query = queries["GET_PNU_DATA"]
        rows = await conn.fetch(query, pnu)
        log_query_results(rows, "PNU 단건 조회")
        
        result = [dict(row) for row in rows]
        return {"data": result, "params": params}

class PnuListRequest(BaseModel):
    pnu_list: List[str]

@app.post("/data/pnu")
async def get_pnu_list(
    request: Request, 
    pnu_request: PnuListRequest, 
    api_key: str = Depends(verify_api_key)
):
    params = await get_query_params(request)
    logger.info(f"PNU 목록 조회 파라미터: {params}")
    logger.info(f"요청된 PNU 목록: {pnu_request.pnu_list}")
    
    result = []
    pnu_results = {}  # 각 PNU별 결과를 추적하기 위한 딕셔너리
    
    async with app.state.db.acquire() as conn:
        for pnu in pnu_request.pnu_list:
            try:
                query = queries["GET_PNU_DATA"]
                rows = await conn.fetch(query, pnu)
                logger.info(f"PNU {pnu} 조회 결과 행 수: {len(rows)}")
                
                pnu_data = [dict(row) for row in rows]
                pnu_results[pnu] = len(pnu_data)  # 각 PNU별 결과 행 수 기록
                
                # 결과에 추가
                for row_dict in pnu_data:
                    result.append(row_dict)
            except Exception as e:
                logger.error(f"PNU {pnu} 조회 중 오류 발생: {str(e)}")
                pnu_results[pnu] = f"오류: {str(e)}"
        
        logger.info(f"PNU별 결과 요약: {pnu_results}")
        logger.info(f"전체 결과 행 수: {len(result)}")
        
        log_query_results(result[:1] if result else [], "PNU 목록 조회")
        return {"data": result, "params": params, "pnu_summary": pnu_results}

# 주소 단계별 셀렉트박스 조회 엔드포인트
@app.get("/data/sido")
async def get_sido_list(request: Request, api_key: str = Depends(verify_api_key)):
    # 쿼리 파라미터 가져오기
    params = await get_query_params(request)
    
    async with app.state.db.acquire() as conn:
        query = queries["GET_SIDO_LIST"]
        rows = await conn.fetch(query)
        
        log_query_results(rows, "시도 목록 조회")
        
        result = [dict(row) for row in rows]
        return {"data": result, "params": params, "count": len(result)}

@app.get("/data/sigungu/{sidoCd}")
async def get_sigungu_list(sidoCd: str, request: Request, api_key: str = Depends(verify_api_key)):
    # 쿼리 파라미터 가져오기
    params = await get_query_params(request)
    
    async with app.state.db.acquire() as conn:
        query = queries["GET_SIGUNGU_LIST"]
        rows = await conn.fetch(query, sidoCd)
        
        log_query_results(rows, "시군구 목록 조회")
        
        result = [dict(row) for row in rows]
        return {"data": result, "params": params, "count": len(result)}

@app.get("/data/emd/{sigunguCd}")
async def get_emd_list(sigunguCd: str, request: Request, api_key: str = Depends(verify_api_key)):
    # 쿼리 파라미터 가져오기
    params = await get_query_params(request)
    
    async with app.state.db.acquire() as conn:
        query = queries["GET_EMD_LIST"]
        rows = await conn.fetch(query, sigunguCd)
        
        log_query_results(rows, "읍면동 목록 조회")
        
        result = [dict(row) for row in rows]
        return {"data": result, "params": params, "count": len(result)}

@app.get("/data/ri/{emdCd}")
async def get_ri_list(emdCd: str, request: Request, api_key: str = Depends(verify_api_key)):
    # 쿼리 파라미터 가져오기
    params = await get_query_params(request)
    
    async with app.state.db.acquire() as conn:
        query = queries["GET_RI_LIST"]
        rows = await conn.fetch(query, emdCd)
        
        log_query_results(rows, "동리 목록 조회")
        
        result = [dict(row) for row in rows]
        return {"data": result, "params": params, "count": len(result)}

@app.get("/data/roadAddr/{roadAddr}")
@measure_time
async def get_road_addr_list(roadAddr: str, request: Request, api_key: str = Depends(verify_api_key)):
    # 쿼리 파라미터 가져오기
    params = await get_query_params(request)
    logger.info(f"도로명주소 목록 조회 파라미터: {params}")
    
    async with app.state.db.acquire() as conn:
        start_time = time.time()
        query = queries["GET_ROAD_ADDR_LIST"]
        rows = await conn.fetch(query, roadAddr)
        query_time = time.time() - start_time
        
        logger.info(f"도로명주소 목록 조회 쿼리 실행 시간: {query_time:.4f}초")
        log_query_results(rows, "도로명주소 목록 조회")
        
        result = [dict(row) for row in rows]
        return {"data": result, "params": params, "query_time": query_time, "count": len(result)}

@app.get("/data/bonboo/{legalCode}")
@measure_time
async def get_jibun_addr_list(
    legalCode: str, 
    request: Request, 
    spCd: Optional[str] = "1",
    bon: Optional[str] = None,
    boo: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    # 쿼리 파라미터 가져오기
    params = await get_query_params(request)
    logger.info(f"지번주소 목록 조회 파라미터: {params}")
    
    # spCd 값을 데이터베이스에서 사용하는 값으로 변환 (반대 로직)
    db_spCd = None
    if spCd == "1":
        db_spCd = "0"
    elif spCd == "2":
        db_spCd = "1"
    elif spCd == "3":
        db_spCd = "2"
    elif spCd == "5":
        db_spCd = "6"
    else:
        db_spCd = spCd
    
    logger.info(f"변환된 특수지코드: 입력={spCd}, DB용={db_spCd}")

    # 기본 쿼리
    base_query = """
    SELECT 법정동코드 AS "legalCd", 도로명주소 AS "roadAddr", 시도 AS "sido", 시군구 AS "sigungu", 
           읍면 AS "emd", 동리 AS "ri", 
           CASE WHEN 특수지코드 = '0' THEN '1' 
                WHEN 특수지코드 = '1' THEN '2' 
                WHEN 특수지코드 = '2' THEN '3' 
                WHEN 특수지코드 = '6' THEN '5' 
                ELSE 특수지코드 END AS "spCd", 
           본번 AS "bon", 부번 AS "boo", 특수지명 AS "spNm", 단지명 AS "cmpNm", 
           동명 AS "dongNm", 호명 AS "hoNm", 전용면적 AS "exArea", 공시가격 AS "pubPrice", 
           단지코드 AS "cmpCd", 동코드 AS "dongCd", 호코드 AS "hoCd", 
           건축물대장PK AS "bldbLedgerPK", "(구)건축물대장PK" AS "oldBldbLedgerPK", PNU AS "PNU" 
    FROM housing_prices hp 
    WHERE hp.법정동코드 = $1
    """
    
    # 조건부 쿼리 추가
    conditions = []
    query_params = [legalCode]  # 기본 파라미터
    
    if spCd:
        conditions.append(f"특수지코드 = ${len(query_params) + 1}")
        query_params.append(db_spCd)
        
    if bon:
        conditions.append(f"본번 = ${len(query_params) + 1}")
        query_params.append(bon)
        
    if boo:
        conditions.append(f"부번 = ${len(query_params) + 1}")
        query_params.append(boo)
    
    # 조건이 있으면 쿼리에 추가
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    logger.info(f"최종 쿼리: {base_query}")
    logger.info(f"쿼리 파라미터: {query_params}")
    
    async with app.state.db.acquire() as conn:
        start_time = time.time()
        try:
            rows = await conn.fetch(base_query, *query_params)
            query_time = time.time() - start_time
            
            logger.info(f"지번주소 목록 조회 쿼리 실행 시간: {query_time:.4f}초")
            log_query_results(rows, "지번주소 목록 조회")
            
            result = [dict(row) for row in rows]
            return {"data": result, "params": params, "query_time": query_time, "count": len(result)}
        except Exception as e:
            logger.error(f"쿼리 실행 오류: {str(e)}")
            return {"error": str(e), "query": base_query, "params": query_params}

async def get_pnu_by_address(address: str) -> Dict[str, Any]:
    """
    주소를 입력받아 V-World API를 통해 PNU 번호를 조회하는 함수
    
    Args:
        address: 조회할 주소 (예: "방배동 1022-3")
        
    Returns:
        Dictionary containing:
        - items: 모든 결과 항목 (성공 시)
        - error: 오류 메시지 (실패 시)
        - status: 상태 코드
    """
    try:
        # API 키와 기본 URL 설정
        api_key = "319AE1D3-A638-3922-93C7-053E31B7B3DA"  # 실제 운영 환경에서는 환경 변수로 관리하는 것이 좋습니다
        base_url = "https://api.vworld.kr/req/search"
        
        # 쿼리 파라미터 설정
        params = {
            "request": "search",
            "key": api_key,
            "query": address,
            "type": "address",
            "category": "PARCEL",
            "size": "100",
            "page": "1"
        }
        
        # URL 인코딩 및 전체 URL 구성
        encoded_params = urllib.parse.urlencode(params)
        url = f"{base_url}?{encoded_params}"
        
        logger.info(f"V-World API 호출: {url}")
        start_time = time.time()
        
        # 비동기 HTTP 요청
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_time = time.time() - start_time
                logger.info(f"V-World API 응답 시간: {response_time:.4f}초")
                
                # 응답 상태 확인
                if response.status != 200:
                    logger.error(f"V-World API 오류: 상태 코드 {response.status}")
                    return {
                        "error": f"API 요청 실패: 상태 코드 {response.status}",
                        "status": "error"
                    }
                
                # JSON 응답 파싱
                data = await response.json()
                
                # 응답 데이터 확인
                if data.get("response", {}).get("status") != "OK":
                    error_msg = data.get("response", {}).get("error", {}).get("text", "알 수 없는 오류")
                    logger.error(f"V-World API 오류: {error_msg}")
                    return {
                        "error": f"API 응답 오류: {error_msg}",
                        "status": "error"
                    }
                
                # 결과 항목 확인
                items = data.get("response", {}).get("result", {}).get("items", [])
                if not items:
                    logger.warning(f"주소 '{address}'에 대한 결과가 없습니다.")
                    return {
                        "error": "주소에 대한 결과가 없습니다.",
                        "status": "not_found"
                    }
                
                # 모든 결과 항목 처리
                processed_items = []
                for item in items:
                    pnu = item.get("id")  # V-World API에서는 'id' 필드가 PNU입니다
                    parcel_address = item.get("address", {}).get("parcel", "")  # 지번주소
                    
                    if not pnu:
                        logger.warning(f"항목에 PNU 정보가 없습니다: {item}")
                        continue
                    
                    # 결과 로깅
                    logger.info(f"주소 '{address}'의 PNU: {pnu}, 지번주소: {parcel_address}")
                    
                    # 필요한 주소 정보 추출
                    address_info = {
                        "pnu": pnu,
                        "parcel_address": parcel_address,
                        "road_address": item.get("address", {}).get("road", ""),
                        "sido": item.get("address", {}).get("sido", ""),
                        "sigungu": item.get("address", {}).get("sigungu", ""),
                        "zipcode": item.get("address", {}).get("zipcode", ""),
                        "bldnm": item.get("address", {}).get("bldnm", ""),
                        "point": item.get("point", {})
                    }
                    
                    processed_items.append({
                        "pnu": pnu,
                        "parcel_address": parcel_address,
                        "address_info": address_info
                    })
                
                if not processed_items:
                    return {
                        "error": "유효한 PNU 정보가 없습니다.",
                        "status": "no_valid_pnu"
                    }
                
                return {
                    "items": processed_items,
                    "status": "success"
                }
                
    except Exception as e:
        logger.error(f"PNU 조회 중 오류 발생: {str(e)}")
        return {
            "error": f"PNU 조회 중 오류 발생: {str(e)}",
            "status": "error"
        }

@app.get("/data/jibunAddr/{address}")
@measure_time
async def address_to_pnu(address: str, request: Request, api_key: str = Depends(verify_api_key)):
    """
    주소를 PNU 번호로 변환하는 API 엔드포인트
    
    Args:
        address: 변환할 주소
        
    Returns:
        PNU 번호 및 관련 정보
    """
    # 쿼리 파라미터 가져오기
    params = await get_query_params(request)
    logger.info(f"주소-PNU 변환 요청: {address}")
    
    # 1. 주소를 V-World API를 통해 PNU로 변환
    start_time = time.time()
    result = await get_pnu_by_address(address)
    
    # PNU 변환 실패 시 오류 응답 반환
    if result.get("status") != "success":
        return {
            "error": result.get("error"),
            "params": params,
            "status": result.get("status")
        }
    
    # 2. 모든 PNU에 대해 데이터베이스 조회
    all_results = []
    processed_count = 0
    
    for item in result.get("items", []):
        pnu = item.get("pnu")
        parcel_address = item.get("parcel_address", "")
        
        try:
            async with app.state.db.acquire() as conn:
                query = queries["GET_PNU_DATA"]
                logger.info(f"PNU {pnu} 조회 쿼리 실행")
                rows = await conn.fetch(query, pnu)
                
                # 3. 데이터가 있으면 결과에 추가
                if rows:
                    # 결과 데이터 변환
                    result_data = [dict(row) for row in rows]
                    
                    # 각 결과 항목에 지번주소(parcel) 추가
                    for row_item in result_data:
                        row_item["parcel"] = parcel_address
                        all_results.append(row_item)
                    
                    processed_count += 1
                    logger.info(f"PNU {pnu}에 대한 데이터 {len(result_data)}건 조회 완료")
                else:
                    logger.info(f"PNU {pnu}에 대한 데이터가 없습니다")
        except Exception as e:
            logger.error(f"PNU {pnu} 데이터 조회 중 오류: {str(e)}")
    
    # 쿼리 실행 시간 계산
    query_time = time.time() - start_time
    
    # 4. 최종 결과 반환
    return {
        "data": all_results,
        "params": params,
        "query_time": query_time,
        "count": len(all_results),
        "processed_pnu_count": processed_count,
        "total_pnu_count": len(result.get("items", []))
    }

# 추가: 메인 블록 - 서버 실행 부분
if __name__ == "__main__":
    import uvicorn
    import os
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    uvicorn.run(app, host=host, port=port, log_level="info")