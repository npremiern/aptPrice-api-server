from fastapi import FastAPI, Depends, Request, Body
import database
from auth import verify_api_key
from models import ServiceData
from query_loader import queries  # 쿼리 로드 추가
from contextlib import asynccontextmanager
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 로깅 함수 정의
def log_query_results(rows: List[Dict[str, Any]], query_name: str = "쿼리") -> None:
    """
    쿼리 결과를 로깅하는 함수
    
    Args:
        rows: 데이터베이스 쿼리 결과 행 목록
        query_name: 로그에 표시할 쿼리 이름
    """
    try:
        logger.info(f"{query_name} 결과 행 수: {len(rows)}")
        if rows:
            # 샘플 데이터 일부 로깅 (민감 정보 제외)
            sample_data = dict(rows[0])
            logger.info(f"{query_name} 샘플 데이터: {sample_data}")
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

'''
@app.get("/data/{service_id}", response_model=list[ServiceData])
async def get_service_data(service_id: str, api_key: str = Depends(verify_api_key)):
    async with app.state.db.acquire() as conn:
        query = queries["GET_SERVICE_DATA"]  # 파일에서 로드한 쿼리 사용
        rows = await conn.fetch(query, service_id)
        # 로깅 함수 호출
        log_query_results(rows, "서비스 데이터 조회")
        result = [ServiceData(**row) for row in rows]
        return result
'''
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
    logger.info(f"시도 목록 조회 파라미터: {params}")
    
    async with app.state.db.acquire() as conn:
        query = queries["GET_SIDO_LIST"]
        rows = await conn.fetch(query)
        log_query_results(rows, "시도 목록 조회")
        
        result = [dict(row) for row in rows]
        return {"data": result, "params": params}

@app.get("/data/sigungu/{sidoCd}")
async def get_sigungu_list(sidoCd: str, request: Request, api_key: str = Depends(verify_api_key)):
    # 쿼리 파라미터 가져오기
    params = await get_query_params(request)
    logger.info(f"시군구 목록 조회 파라미터: {params}")
    
    async with app.state.db.acquire() as conn:
        query = queries["GET_SIGUNGU_LIST"]
        rows = await conn.fetch(query, sidoCd)
        log_query_results(rows, "시군구 목록 조회")
        
        result = [dict(row) for row in rows]
        return {"data": result, "params": params}

@app.get("/data/emd/{sigunguCd}")
async def get_emd_list(sigunguCd: str, request: Request, api_key: str = Depends(verify_api_key)):
    # 쿼리 파라미터 가져오기
    params = await get_query_params(request)
    logger.info(f"읍면동 목록 조회 파라미터: {params}")
    
    async with app.state.db.acquire() as conn:
        query = queries["GET_EMD_LIST"]
        rows = await conn.fetch(query, sigunguCd)
        log_query_results(rows, "읍면동 목록 조회")
        
        result = [dict(row) for row in rows]
        return {"data": result, "params": params}

@app.get("/data/ri/{emdCd}")
async def get_ri_list(emdCd: str, request: Request, api_key: str = Depends(verify_api_key)):
    # 쿼리 파라미터 가져오기
    params = await get_query_params(request)
    logger.info(f"동리 목록 조회 파라미터: {params}")
    
    async with app.state.db.acquire() as conn:
        query = queries["GET_RI_LIST"]
        rows = await conn.fetch(query, emdCd)
        log_query_results(rows, "동리 목록 조회")
        
        result = [dict(row) for row in rows]
        return {"data": result, "params": params}

# 추가: 메인 블록 - 서버 실행 부분
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")