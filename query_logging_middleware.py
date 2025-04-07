from fastapi import Request
import time
import logging

logger = logging.getLogger(__name__)

async def query_logging_middleware(request: Request, call_next):
    # 요청 시작 시간
    start_time = time.time()
    
    # 요청 경로 및 메서드 로깅
    logger.info(f"요청 시작: {request.method} {request.url.path}")
    
    # 다음 미들웨어 또는 엔드포인트 호출
    response = await call_next(request)
    
    # 요청 처리 시간 계산
    process_time = time.time() - start_time
    
    # 응답 상태 코드 및 처리 시간 로깅
    logger.info(f"요청 완료: {request.method} {request.url.path} - 상태 코드: {response.status_code}, 처리 시간: {process_time:.4f}초")
    
    return response 